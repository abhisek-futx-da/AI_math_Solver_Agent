"""Audio input: speech-to-text with Whisper. Return transcript and confidence proxy."""
import io
import tempfile
from typing import Tuple

def transcribe_audio(audio_bytes: bytes, filename: str = "") -> Tuple[str, float]:
    """
    Transcribe audio to text using Whisper. Returns (transcript, confidence_proxy).
    Confidence is 1.0 if we got a non-empty transcript; 0.5 if empty (unclear).
    """
    try:
        import whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            path = f.name
        try:
            model = whisper.load_model("base")
            result = model.transcribe(path, fp16=False)
            text = (result.get("text") or "").strip()
            # Normalize math phrases
            text = _normalize_math_phrases(text)
            conf = 0.9 if text else 0.4
            return text, conf
        finally:
            import os
            try:
                os.unlink(path)
            except Exception:
                pass
    except Exception:
        return "", 0.0


def _normalize_math_phrases(s: str) -> str:
    """Handle math-specific phrases like 'square root of', 'raised to'."""
    s = s.replace("square root of", "sqrt(").replace("raised to", "^")
    # Simple cleanup
    s = s.replace("  ", " ").strip()
    return s
