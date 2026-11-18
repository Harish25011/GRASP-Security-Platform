"""
Safe Box — quarantine system with SQLite-backed storage.
"""
import json
from datetime import datetime
from backend.database import get_db


class SafeBox:
    """Manages quarantined nodes."""
    
    def quarantine(self, node_id: str, risk_score: float, reason: str, agent_scores: dict) -> dict:
        """Add a node to quarantine."""
        # Convert numpy types to native Python for JSON serialization
        safe_scores = {k: float(v) for k, v in agent_scores.items()} if agent_scores else {}
        with get_db() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO safe_box (node_id, risk_score, reason, agent_scores, status, quarantined_at)
                VALUES (?, ?, ?, ?, 'quarantined', datetime('now'))
            """, (node_id, float(risk_score), reason, json.dumps(safe_scores)))
        
        return {
            "node_id": node_id,
            "status": "quarantined",
            "risk_score": risk_score,
            "reason": reason,
        }
    
    def release(self, node_id: str) -> dict:
        """Release a node from quarantine."""
        with get_db() as conn:
            conn.execute("""
                UPDATE safe_box SET status = 'released', released_at = datetime('now')
                WHERE node_id = ? AND status = 'quarantined'
            """, (node_id,))
        
        return {"node_id": node_id, "status": "released"}
    
    def get_all(self) -> list:
        """Get all quarantined nodes."""
        with get_db() as conn:
            rows = conn.execute("""
                SELECT * FROM safe_box WHERE status = 'quarantined'
                ORDER BY quarantined_at DESC
            """).fetchall()
        
        return [
            {
                "id": row["id"],
                "node_id": row["node_id"],
                "risk_score": row["risk_score"],
                "reason": row["reason"],
                "agent_scores": json.loads(row["agent_scores"]) if row["agent_scores"] else {},
                "quarantined_at": row["quarantined_at"],
                "status": row["status"],
            }
            for row in rows
        ]
    
    def get_count(self) -> int:
        with get_db() as conn:
            result = conn.execute("SELECT COUNT(*) FROM safe_box WHERE status = 'quarantined'").fetchone()
        return result[0] if result else 0
