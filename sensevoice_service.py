import os
import threading
from typing import Any

from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


class SenseVoiceService:
    def __init__(self) -> None:
        self._model = None
        self._lock = threading.Lock()

    def _load_model(self) -> None:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    device = os.getenv("SENSEVOICE_DEVICE", "cpu")
                    self._model = AutoModel(
                        model=os.getenv("SENSEVOICE_MODEL", "iic/SenseVoiceSmall"),
                        vad_model=os.getenv("SENSEVOICE_VAD_MODEL", "fsmn-vad"),
                        trust_remote_code=True,
                        device=device,
                        disable_update=True,
                    )

    def transcribe_file(self, file_path: str) -> str:
        self._load_model()
        assert self._model is not None

        result: Any = self._model.generate(
            input=file_path,
            cache={},
            language=os.getenv("SENSEVOICE_LANGUAGE", "zh"),
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,
            merge_length_s=15,
        )

        text = ""
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                text = str(first.get("text", "")).strip()
            else:
                text = str(first).strip()
        else:
            text = str(result).strip()

        if text:
            text = rich_transcription_postprocess(text)
        return text.strip()


svc = SenseVoiceService()
