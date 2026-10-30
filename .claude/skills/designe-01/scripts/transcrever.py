"""Transcreve um WAV mono 16 kHz com faster-whisper, com tempo por palavra.
Uso: python transcrever.py audio.wav words.json PASTA_OU_NOME_DO_MODELO [idioma]
Saída: lista de segmentos {start, end, text, words:[{w, s, e}]}.
"""
import json, sys, wave
import numpy as np
from faster_whisper import WhisperModel

wav, out_path, model = sys.argv[1], sys.argv[2], sys.argv[3]
lang = sys.argv[4] if len(sys.argv) > 4 else "pt"
m = WhisperModel(model, device="cpu", compute_type="int8")
# lê o WAV direto (evita o decodificador do PyAV, que quebra em algumas versões)
audio = np.frombuffer(wave.open(wav).readframes(10**10), np.int16).astype(np.float32) / 32768
segs, _ = m.transcribe(audio, language=lang, word_timestamps=True, vad_filter=True)
out = []
for s in segs:
    print(f"[{s.start:7.2f}] {s.text.strip()}", flush=True)
    out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for w in s.words]})
json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=1)
