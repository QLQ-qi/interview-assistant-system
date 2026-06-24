# Interview Assistant - LLM Prompt Templates

SYSTEM_PROMPT = '''You are a professional interview assistant.
Your role is to analyze real-time interview conversations and provide helpful suggestions.
Focus on being concise and practical.'''

TRANSCRIPTION_CONTEXT_PROMPT = '''Here is the recent interview transcription:

{history}

The {speaker} just said: "{text}"

Analyze this and provide actionable hints for the interviewer.'''
