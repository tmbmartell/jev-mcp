#!/usr/bin/env python3
"""Prepara o vídeo bruto antes dos efeitos: acelera a fala, limpa o ruído e padroniza.

Uso:
  python preparar.py bruto.mp4 base.mp4 [--velocidade 1.2] [--sem-ruido]
  python preparar.py base.mp4 --transcrever palavras.json [--modelo caminho/ou/nome]

- Velocidade: vídeo e áudio juntos, sem mudar o tom da voz (atempo).
- Ruído: passa-alta, redução de ruído (afftdn), gate suave e compressor.
- Volume: normalização em DUAS passadas, com ganho fixo, até -14 LUFS (padrão Reels/TikTok).
  Uma passada só "bombeia" o chiado nos trechos sem fala, por isso as duas.
- Imagem: sobe para 720x1280 (ou mantém, se já for maior) e dá uma leve nitidez.
- Transcrição (opcional): faster-whisper com tempo de cada palavra, no formato que a
  `legenda` do motion.py aceita: [[palavra, inicio, fim], ...].
"""
import argparse
import json
import subprocess
import sys

FILTRO_VOZ = ("highpass=f=80,lowpass=f=12000,afftdn=nr=18:nf=-40:tn=1,"
              "agate=threshold=0.02:ratio=4:range=0.06:attack=8:release=300,"
              "acompressor=threshold=-22dB:ratio=3:attack=5:release=150")


def preparar(entrada, saida, velocidade, limpar):
    voz = (f"atempo={velocidade}," if velocidade != 1 else "") + (FILTRO_VOZ if limpar else "anull")
    medida = subprocess.run(["ffmpeg", "-i", entrada, "-af", voz + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                             "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(medida[medida.rindex("{"):medida.rindex("}") + 1])
    norm = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
            f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:"
            f"offset={j['target_offset']}:linear=true")
    video = (f"setpts=PTS/{velocidade}," if velocidade != 1 else "") + \
        "scale='max(720,iw)':-2:flags=lanczos,unsharp=5:5:0.4,fps=30"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", entrada,
                    "-filter_complex", f"[0:v]{video}[v];[0:a]{voz},{norm}[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", saida], check=True)
    print("Pronto:", saida)


def transcrever(entrada, saida, modelo):
    import numpy as np
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", entrada, "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True).stdout
    segs, _ = WhisperModel(modelo, device="cpu", compute_type="int8").transcribe(
        np.frombuffer(raw, np.float32), word_timestamps=True, language="pt", beam_size=5)
    palavras = []
    for s in segs:
        print(f"[{s.start:5.1f}-{s.end:5.1f}] {s.text}")
        palavras += [[w.word.strip(), round(w.start, 2), round(w.end, 2)] for w in s.words]
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(palavras, f, ensure_ascii=False)
    print(f"{len(palavras)} palavras em {saida}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("saida", nargs="?")
    ap.add_argument("--velocidade", type=float, default=1.0)
    ap.add_argument("--sem-ruido", action="store_true")
    ap.add_argument("--transcrever")
    ap.add_argument("--modelo", default="small")
    a = ap.parse_args()
    if a.saida:
        preparar(a.entrada, a.saida, a.velocidade, not a.sem_ruido)
    if a.transcrever:
        transcrever(a.saida or a.entrada, a.transcrever, a.modelo)
    if not a.saida and not a.transcrever:
        sys.exit(__doc__)
