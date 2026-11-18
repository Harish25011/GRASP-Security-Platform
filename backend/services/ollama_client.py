import httpx
import asyncio
import logging

logger = logging.getLogger("ollama_client")

OLLAMA_BASE = "http://localhost:11434"

async def generate(prompt: str, model: str = "llama3",
                   system: str = None, temperature: float = 0.3) -> str:
    """
    Communicates dynamically with the local Ollama LLM running strictly on the host. 
    Maintains complete data privacy by sidestepping all external OpenAI/Anthropic APIs.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 512}
    }
    if system:
        payload["system"] = system

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(f"{OLLAMA_BASE}/api/generate", json=payload)
            r.raise_for_status()
            return r.json().get("response", "").strip()
    except Exception as e:
        logger.error(f"[Ollama] Generation error: {e}")
        return "Ollama generation failed offline/timeout."

async def is_available() -> bool:
    """Verifies if the Ollama daemon is currently running on port 11434."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_BASE}/api/tags")
            return r.status_code == 200
    except:
        return False
