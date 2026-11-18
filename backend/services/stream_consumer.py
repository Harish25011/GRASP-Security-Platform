"""
Consumer loop that pulls events from the stream processor queue
and runs them through the agent pipeline for real-time detection.
"""
import asyncio
import logging
from backend.services.stream_processor import event_queue
from backend.services.graph_builder import GraphBuilder
from backend.services.aggregator import Aggregator
from backend.services.decision_engine import DecisionEngine
from backend.services.safe_box import SafeBox

logger = logging.getLogger("stream_consumer")

graph_builder = GraphBuilder()
aggregator = Aggregator()
decision_engine = DecisionEngine()
safe_box = SafeBox()


async def consume_events(ws_manager):
    """Long-running consumer: pull from event_queue → agents → decisions."""
    logger.info("[StreamConsumer] Starting consumer loop...")

    while True:
        try:
            event = await asyncio.wait_for(event_queue.get(), timeout=5.0)
        except asyncio.TimeoutError:
            continue

        try:
            # Build graph node from event
            src = event.get("src_ip", "unknown")
            dst = event.get("dst_ip", "unknown")

            if not graph_builder.graph.has_node(src):
                graph_builder.graph.add_node(src, node_type="External",
                    label=src, risk_score=0.0, status="active", features=[])
            if not graph_builder.graph.has_node(dst):
                graph_builder.graph.add_node(dst, node_type="Internal",
                    label=dst, risk_score=0.0, status="active", features=[])

            graph_builder.graph.add_edge(src, dst,
                protocol=event.get("protocol", "TCP"),
                bytes_sent=event.get("size", 0),
                bytes_recv=0,
            )

            # Recompute features
            graph_builder._compute_features()
            snapshot = graph_builder.freeze()

            # Run agent swarm
            event_data = {
                "event_type": event.get("heuristic_label", "unknown"),
                "payload": "",
                "source_ip": src,
                "dest_ip": dst,
            }
            swarm_result = aggregator.run_swarm(snapshot, dst, event_data)
            decision = decision_engine.evaluate(dst, swarm_result)

            # Quarantine if critical
            if decision["action"] == "quarantine":
                safe_box.quarantine(dst, decision["risk_score"],
                    f"Live detection: {event.get('heuristic_label', 'unknown')}",
                    swarm_result["scores"])

                # Broadcast quarantine to WebSocket
                await ws_manager.send_anomaly(decision)
                logger.warning(
                    f"[StreamConsumer] QUARANTINE: {dst} "
                    f"(risk={decision['risk_score']:.2f})"
                )

            # Broadcast threat event to Live Threat Monitor
            top_agents = sorted(swarm_result["scores"].items(),
                                key=lambda x: x[1], reverse=True)[:3]
            await ws_manager.broadcast({
                "type": "threat_detected",
                "payload": {
                    "timestamp": __import__('datetime').datetime.now().isoformat(),
                    "source_ip": src,
                    "dest_ip": dst,
                    "attack_type": event.get("heuristic_label", "unknown"),
                    "risk_score": float(decision["risk_score"]),
                    "tier": decision["tier"],
                    "fired_agents": [a for a, _ in top_agents],
                }
            })

            # Broadcast event to all connected dashboard clients
            await ws_manager.send_event({
                "source": src, "target": dst,
                "risk_score": decision["risk_score"],
                "tier": decision["tier"],
            })

        except Exception as e:
            logger.error(f"[StreamConsumer] Error processing event: {e}")
