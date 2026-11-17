"""Gera a narração provisória (Piper, offline) e o arquivo de tempos usado pelo Remotion.
Uso: python3 scripts/gerar_voz.py <modelo.onnx>
Para trocar pela voz final (ElevenLabs/gravação), salve um WAV por trecho em public/voz/<id>.wav
e rode com --so-tempos para recalcular os tempos.
Velocidade: a voz é acelerada 1,1x (atempo, sem alterar o tom)."""
import json, subprocess, sys, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
segs = json.load(open(os.path.join(ROOT, "scripts/narracao.json")))
out = os.path.join(ROOT, "public/voz"); os.makedirs(out, exist_ok=True)
so_tempos = "--so-tempos" in sys.argv
GAP = 0.38
def dur(p):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]).decode())
t = 0.6; result = []
for s in segs:
    wav = os.path.join(out, s["id"] + ".wav")
    if not so_tempos:
        raw = wav + ".raw.wav"
        subprocess.run(["piper","-m",sys.argv[1],"--length_scale","0.9","--sentence_silence","0.25","-f",raw], input=s["tts"].encode(), check=True, capture_output=True)
        # tratamento estilo podcast: corta graves, realce de presença, compressão pesada, normaliza
        subprocess.run(["ffmpeg","-y","-v","error","-i",raw,"-af",
            "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
            "atempo=1.1,highpass=f=80,equalizer=f=4000:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=4:attack=5:release=60:makeup=4,loudnorm=I=-16:TP=-1.5",
            "-ar","48000",wav], check=True)
        os.remove(raw)
    d = dur(wav)
    result.append({"id": s["id"], "text": s["text"], "start": round(t,3), "duration": round(d,3)})
    t += d + GAP
json.dump({"total": round(t + 1.5, 3), "segments": result}, open(os.path.join(ROOT,"src/tempos.json"),"w"), ensure_ascii=False, indent=1)
print("total", round(t,2))
for r in result: print(r["id"], r["start"], r["duration"])
