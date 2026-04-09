import os
import re
import torch
import torchaudio
from f5_tts.api import F5TTS

# Max characters per chunk — keeps tensor sizes compatible with reference audio
MAX_CHUNK_CHARS = 150


class TTSEngine:
    def __init__(self):
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.device = device
        self.model = F5TTS(device=device)

    def _split_text(self, text: str) -> list[str]:
        """Split text into sentence-aware chunks under MAX_CHUNK_CHARS."""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        chunks = []
        current = ""

        for sent in sentences:
            if len(current) + len(sent) + 1 <= MAX_CHUNK_CHARS:
                current = (current + " " + sent).strip()
            else:
                if current:
                    chunks.append(current)
                # Sentence itself is too long — split further at commas
                if len(sent) > MAX_CHUNK_CHARS:
                    parts = re.split(r"(?<=,)\s+", sent)
                    sub = ""
                    for part in parts:
                        if len(sub) + len(part) + 1 <= MAX_CHUNK_CHARS:
                            sub = (sub + " " + part).strip()
                        else:
                            if sub:
                                chunks.append(sub)
                            sub = part
                    if sub:
                        chunks.append(sub)
                    current = ""
                else:
                    current = sent

        if current:
            chunks.append(current)

        return chunks if chunks else [text]

    def generate(self, text: str, ref_audio: str, ref_text: str, output_path: str, speed: float = 1.0):
        """
        text       : target text to synthesize
        ref_audio  : path to reference audio file
        ref_text   : transcript of the reference audio
        output_path: output WAV file path
        speed      : speech rate multiplier, 1.0 = normal
        """
        chunks = self._split_text(text)

        if len(chunks) == 1:
            self.model.infer(
                ref_file=ref_audio,
                ref_text=ref_text,
                gen_text=chunks[0],
                file_wave=output_path,
                speed=speed,
            )
            return output_path

        # Generate each chunk then concatenate into one WAV
        audio_parts = []
        sample_rate = None

        for i, chunk in enumerate(chunks):
            chunk_path = f"{output_path}.chunk{i}.wav"
            self.model.infer(
                ref_file=ref_audio,
                ref_text=ref_text,
                gen_text=chunk,
                file_wave=chunk_path,
                speed=speed,
            )
            waveform, sr = torchaudio.load(chunk_path)
            audio_parts.append(waveform)
            sample_rate = sr
            os.remove(chunk_path)

        combined = torch.cat(audio_parts, dim=1)
        torchaudio.save(output_path, combined, sample_rate)
        return output_path
