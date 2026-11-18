import asyncio
import time
import hashlib
import logging
from backend.services.stream_processor import ingest_event
from backend.services.attack_classifier import pre_classify

logger = logging.getLogger("live_capture")

import platform

TARGET_IP = None   # set via /api/capture/start
INTERFACE = "Wi-Fi" if platform.system() == "Windows" else "eth0"  # Auto-detect OS
STOP_FLAG = False

def parse_packet(pkt) -> dict | None:
    from scapy.all import IP, TCP, UDP, ICMP
    if not pkt.haslayer(IP):
        return None
    
    # Filter for targeted IP traffic only to avoid background system noise
    if TARGET_IP and pkt[IP].dst != TARGET_IP and pkt[IP].src != TARGET_IP:
        return None
        
    event = {
        "src_ip":   pkt[IP].src,
        "dst_ip":   pkt[IP].dst,
        "protocol": pkt[IP].proto,
        "size":     len(pkt),
        "timestamp": time.time(),
        "port":     pkt[TCP].dport if pkt.haslayer(TCP) else
                    pkt[UDP].dport if pkt.haslayer(UDP) else 0,
        "flags":    str(pkt[TCP].flags) if pkt.haslayer(TCP) else "",
        "icmp":     pkt.haslayer(ICMP)
    }
    
    # Append the pre-classification heuristic
    event["heuristic_label"] = pre_classify(event)
    return event

def start_capture_sync(interface: str, target_ip: str, loop: asyncio.AbstractEventLoop):
    """Sync Scapy wrapper designed to run inside a ThreadPoolExecutor."""
    global TARGET_IP, INTERFACE, STOP_FLAG
    from scapy.all import sniff
    
    TARGET_IP = target_ip
    INTERFACE = interface
    STOP_FLAG = False
    
    logger.info(f"[*] Starting scapy packet sniffer on {INTERFACE} tracking {TARGET_IP}")

    def callback(pkt):
        event = parse_packet(pkt)
        if event:
            # Safely schedule the async ingest from the synchronous scapy thread
            asyncio.run_coroutine_threadsafe(ingest_event(event), loop)

    sniff(iface=interface, prn=callback, store=False, stop_filter=lambda _: STOP_FLAG)
    logger.info("[*] Scapy capture thread shutting down.")

def stop_capture():
    global STOP_FLAG
    STOP_FLAG = True
