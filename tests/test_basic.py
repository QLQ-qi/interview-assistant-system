"""Basic tests for the Interview Assistant System."""


def test_imports():
    """Verify that core modules can be imported."""
    from app.config import settings
    assert settings.APP_NAME == "Interview Assistant System"


def test_health():
    """Verify that the main app can be instantiated."""
    from app.main import app
    assert app.title == "Interview Assistant System API"
    assert app.version == "0.1.0"


def test_llm_types():
    """Verify LLM module exports."""
    from app.llm.service import BaseLLM, MockLLM, OllamaLLM
    assert BaseLLM is not None
    assert MockLLM is not None
    assert OllamaLLM is not None


def test_mock_llm_returns_empty_for_empty_input():
    """MockLLM should handle empty text gracefully."""
    from app.llm.service import MockLLM
    import asyncio
    llm = MockLLM()
    hints = asyncio.run(llm.analyze_transcription([], "candidate", "", "test-session"))
    assert isinstance(hints, list)


def test_mock_llm_detects_salary_keyword():
    """MockLLM should detect salary-related keywords as warnings."""
    from app.llm.service import MockLLM
    import asyncio
    llm = MockLLM()
    hints = asyncio.run(llm.analyze_transcription([], "candidate", "I expect a salary of 100k", "test"))
    assert len(hints) > 0
    assert hints[0]["hint_type"] == "warning"
