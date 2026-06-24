"""LLM Service - Abstract interface + Mock + Ollama implementations"""
from abc import ABC, abstractmethod
import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Abstract LLM interface for interview analysis"""

    @abstractmethod
    async def analyze_transcription(
        self, history: list[dict], speaker: str, text: str, session_id: str
    ) -> list[dict]:
        """Analyze a transcription utterance and return hints."""
        ...



class MockLLM(BaseLLM):
    """Rule-based mock LLM that generates hints without a real model.
    
    Uses keyword patterns to simulate AI-generated interview hints.
    Useful for development, testing, and demo purposes.
    """

    RULES = [
        {
            "keywords": ["salary", "compensation", "pay", "package", "bonus"],
            "hint_type": "warning",
            "content": "Candidate raised compensation topic early. Consider acknowledging the question professionally while refocusing on role fit and value alignment before discussing numbers.",
            "confidence": 0.75,
        },
        {
            "keywords": ["previous", "last", "former", "earlier company", "my last"],
            "hint_type": "case_reference",
            "content": "Reference to past experience detected. Probe for specific STAR examples: the Situation, Task, Action, and measurable Result.",
            "confidence": 0.7,
        },
        {
            "keywords": ["team", "collaboration", "worked with", "cross-functional", "stakeholder"],
            "hint_type": "standard_talk",
            "content": "Collaboration context detected. Ask about team size, their specific role, and how they handled disagreements within the team.",
            "confidence": 0.8,
        },
        {
            "keywords": ["project", "led", "managed", "responsible", "delivered"],
            "hint_type": "standard_talk",
            "content": "Leadership experience mentioned. Follow up with: scope of the project, timeline, team size under their supervision, and key outcomes.",
            "confidence": 0.75,
        },
        {
            "keywords": ["challenge", "difficult", "hard", "struggle", "problem", "issue"],
            "hint_type": "standard_talk",
            "content": "Challenge mentioned. Use the STAR follow-up: What was the specific challenge, what actions did they take, and what was the measurable outcome?",
            "confidence": 0.85,
        },
        {
            "keywords": ["learn", "improve", "grow", "develop", "skill"],
            "hint_type": "standard_talk",
            "content": "Growth mindset cue detected. Ask how they applied this learning in a practical setting and what impact it had on their work.",
            "confidence": 0.7,
        },
        {
            "keywords": ["python", "java", "javascript", "react", "sql", "docker", "kubernetes", "aws", "cloud"],
            "hint_type": "case_reference",
            "content": "Technical skill mentioned. Ask about depth of experience, production usage, and any certifications or formal training.",
            "confidence": 0.65,
        },
        {
            "keywords": ["interested in", "excited about", "passionate", "love", "enjoy"],
            "hint_type": "standard_talk",
            "content": "Positive motivation cue. Probe deeper: what specifically excites them about this area and how have they pursued it outside of work?",
            "confidence": 0.6,
        },
        {
            "keywords": ["quit", "resign", "leave", "fired", "laid off", "let go"],
            "hint_type": "warning",
            "content": "Sensitive employment topic. Listen for red flags in how they describe the departure. Avoid leading questions, focus on facts.",
            "confidence": 0.7,
        },
        {
            "keywords": ["weakness", "improve", "better at", "not good", "lack"],
            "hint_type": "standard_talk",
            "content": "Self-improvement awareness. Good sign if they can articulate specific weaknesses and concrete steps they are taking to address them.",
            "confidence": 0.75,
        },
    ]

    DEFAULT_HINTS = [
        {"hint_type": "standard_talk", "content": "Good opportunity to ask an open-ended follow-up question to understand their thought process better.", "confidence": 0.5},
        {"hint_type": "standard_talk", "content": "Let the candidate finish their response fully before asking the next question. Silence can encourage elaboration.", "confidence": 0.4},
    ]

    async def analyze_transcription(
        self, history: list[dict], speaker: str, text: str, session_id: str
    ) -> list[dict]:
        text_lower = text.lower()
        hints = []

        for rule in self.RULES:
            for kw in rule["keywords"]:
                if kw.lower() in text_lower:
                    hints.append({
                        "hint_type": rule["hint_type"],
                        "content": rule["content"],
                        "confidence": rule["confidence"],
                    })
                    break

        if not hints:
            hints.append(self.DEFAULT_HINTS[0])

        logger.debug(f"MockLLM generated {len(hints)} hints for session {session_id}")
        return hints[:3]  # max 3 hints per utterance





class OllamaLLM(BaseLLM):
    """Real LLM implementation using Ollama REST API."""

    def __init__(self, api_url: str = None, model: str = None):
        self.api_url = (api_url or "http://localhost:11434").rstrip("/")
        self.model = model or "qwen2.5:0.5b"

    async def analyze_transcription(
        self, history: list[dict], speaker: str, text: str, session_id: str
    ) -> list[dict]:
        from app.llm.prompts import SYSTEM_PROMPT, TRANSCRIPTION_CONTEXT_PROMPT

        history_lines = []
        for entry in history[-10:]:
            spk = entry.get("speaker", "unknown")
            txt = entry.get("text", "")
            label = 'Interviewer' if spk == 'interviewer' else 'Candidate'
            history_lines.append(f"{label}: {txt}")
        history_str = chr(10).join(history_lines) if history_lines else "(no prior conversation)"

        prompt = TRANSCRIPTION_CONTEXT_PROMPT.format(
            history=history_str,
            speaker='Interviewer' if speaker == 'interviewer' else 'Candidate',
            text=text,
        )

        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.api_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                        ],
                        "stream": False,
                        "options": {"temperature": 0.3, "top_p": 0.9},
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            response_text = data.get("message", {}).get("content", "")
            parsed = self._parse_response(response_text)
            return parsed

        except Exception as e:
            logger.error(f"OllamaLLM request failed: {e}")
            return []

    def _parse_response(self, text: str) -> list[dict]:
        hints = []
        cleaned = text.strip()
        if not cleaned:
            return hints
        if cleaned.startswith('[') and cleaned.endswith(']'):
            try:
                import json
                parsed = json.loads(cleaned)
                for item in parsed:
                    if isinstance(item, dict) and 'hint_type' in item and 'content' in item:
                        hints.append(item)
                if hints:
                    return hints[:5]
            except json.JSONDecodeError:
                pass
        cleaned = cleaned.strip(' : - ' + chr(34) + chr(39))
        if cleaned:
            hints.append({
                'hint_type': 'standard_talk',
                'content': cleaned[:300],
                'confidence': 0.6,
            })
        return hints[:5]




# LLM factory with caching
_llm_instance = None


def get_llm():
    """Get the configured LLM instance (cached)."""
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    try:
        from app.config import settings
        api_url = settings.LLM_API_URL.rstrip("/")
        model_name = settings.LLM_MODEL or 'qwen2.5:0.5b'
        try:
            import httpx
            with httpx.Client(timeout=2.0) as c:
                r = c.get(f"{api_url}/api/tags")
                if r.status_code == 200:
                    _llm_instance = OllamaLLM(api_url=api_url, model=model_name)
                    logger.info(f"Using OllamaLLM with model {model_name} at {api_url}")
                    return _llm_instance
        except Exception as e:
            logger.info(f"Ollama not reachable at {api_url}: {e}")
    except Exception as e:
        logger.info(f"Config not available: {e}")

    _llm_instance = MockLLM()
    logger.info("Using MockLLM (rule-based)")
    return _llm_instance
