"""Fast heuristic pre-classification engine for live packet streams."""

def pre_classify(event: dict) -> str:
    """
    Provides a lightning-fast heuristic label to raw packets before the 
    intensive 15-agent swarm completes execution.
    """
    flags = event.get("flags", "")
    port  = event.get("port", 0)
    size  = event.get("size", 0)

    if "S" in flags and size < 100:           
        return "PORT_SCAN"
    if event.get("icmp") and size > 1000:     
        return "DDOS"
    if port in [22, 3389, 21, 23, 80, 443]:  
        return "BRUTE_FORCE_CANDIDATE"
    if size > 50000:                           
        return "EXFILTRATION_CANDIDATE"
        
    return "UNKNOWN"
