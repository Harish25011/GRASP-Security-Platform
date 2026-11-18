import asyncio
import hashlib
from collections import OrderedDict
import logging

logger = logging.getLogger("stream_processor")

# 10,000-element LRU Cache for mitigating duplicated payloads (e.g. volumetric DDoS)
DEDUP_CACHE = OrderedDict()
MAX_CACHE_SIZE = 10000

# The core asynchronous event stream queue (Backpressure threshold: 50,000 events)
event_queue = asyncio.Queue(maxsize=50000)

DROP_COUNTER = 0

async def ingest_event(event: dict):
    """
    Ingests raw networking events. Provides O(1) deduplication and active backpressure.
    Returns True if ingested, False if dropped.
    """
    global DROP_COUNTER
    
    # 1. Deduplication (Hash the entire event payload/headers)
    event_str = str(event).encode('utf-8')
    key = hashlib.md5(event_str).hexdigest()
    
    if key in DEDUP_CACHE:
        # It's a duplicate - move to end to show it was recently used
        DEDUP_CACHE.move_to_end(key)
        return False
        
    DEDUP_CACHE[key] = True
    if len(DEDUP_CACHE) > MAX_CACHE_SIZE:
        DEDUP_CACHE.popitem(last=False)
        
    # 2. Backpressure
    if event_queue.full():
        DROP_COUNTER += 1
        if DROP_COUNTER % 1000 == 0:
            logger.warning(f"Queue full - dropped event #{DROP_COUNTER}")
        return False
        
    try:
        # Non-blocking put since we checked full()
        event_queue.put_nowait(event)
        return True
    except asyncio.QueueFull:
        DROP_COUNTER += 1
        return False

def get_stream_status() -> dict:
    """Returns the current operating health of the stream processor."""
    return {
        "queueDepth": event_queue.qsize(),
        "dropCount": DROP_COUNTER,
        "dedupCacheSize": len(DEDUP_CACHE)
    }
