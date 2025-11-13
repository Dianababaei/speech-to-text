"""Service modules for the speech-to-text prototype."""

from src.services.openai_service import OpenAIService, transcribe_audio

__all__ = ['OpenAIService', 'transcribe_audio']
