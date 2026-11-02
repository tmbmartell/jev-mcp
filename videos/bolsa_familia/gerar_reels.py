"""Versão Reels (1080x1920, 9:16) do vídeo do Bolsa Família, com narração.

Reaproveita os desenhos de gerar_video.py: cada cena é desenhada num "palco"
1280x720, que é encaixado no meio do quadro vertical. Título e legendas são
redesenhados grandes, e a legenda troca em sincronia com cada trecho falado.

Voz: RHVoice (Letícia, pt-BR), offline.
    sudo apt-get install rhvoice rhvoice-brazilian-portuguese
Uso: python3 gerar_reels.py  ->  bolsa_familia_reels.mp4
"""
import math
import os
import subprocess
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw

import gerar_video as gv
from gerar_video import (INK, WHITE, CREAM, YEL, RED, BLUE, GREEN, ORANGE, PURPLE,
                         font, wrap, rrect, ease, pop)

RW, RH, FPS = 1080, 1920, 24
SR = 44100
STAGE_Y = 470                      # topo do palco no quadro vertical
STAGE_H = int(720 * RW / 1280)     # 607
HERE = os.path.dirname(os.path.abspath(__file__))
VOICE_RATE = "118"                 # % da velocidade normal da Letícia

# (legenda na tela, texto falado) por trecho. Números por extenso na fala.
SCRIPT = {
    "scene_title": ("Você sabe como funciona?", BLUE, [
        ("Oi! Eu sou a Dona Maria.", "Oi! Eu sou a Dona Maria."),
        ("Bora entender, sem enrolação, como funciona o Bolsa Família?",
         "Bora entender, sem enrolação, como funciona o Bolsa Família?"),
    ]),
    "scene_oque": ("O que é?", BLUE, [
        ("Um programa do Governo Federal, criado em 2003...",
         "É um programa do Governo Federal, criado em dois mil e três,"),
        ("...que dá dinheiro todo mês para famílias de baixa renda.",
         "que dá dinheiro todo mês para famílias de baixa renda."),
        ("Pensa numa rede de circo: ela não faz o show pelo trapezista...",
         "Pensa numa rede de circo: ela não faz o show pelo trapezista,"),
        ("...mas segura quem cai, pra que possa subir de novo.",
         "mas segura quem cai, pra que possa subir de novo."),
    ]),
    "scene_quem": ("Quem pode receber?", ORANGE, [
        ("Divida a renda da casa pelo número de pessoas.",
         "É só dividir a renda da casa pelo número de pessoas."),
        ("Deu até R$ 218 por pessoa por mês? A família pode entrar!",
         "Se der até duzentos e dezoito reais por pessoa, por mês, a família pode entrar!"),
    ]),
    "scene_cad": ("Passo 1: Cadastro Único", GREEN, [
        ("O primeiro passo é o Cadastro Único, feito no CRAS da sua cidade.",
         "O primeiro passo é o Cadastro Único, feito no CRAS da sua cidade."),
        ("Leve documento com CPF de todo mundo e mantenha os dados atualizados.",
         "Leve documento com cê pê éfe de todo mundo, e mantenha os dados sempre atualizados."),
    ]),
    "scene_quanto": ("Quanto recebe?", PURPLE, [
        ("É como montar um sanduíche: o pão é R$ 142 por pessoa...",
         "É como montar um sanduíche: o pão são cento e quarenta e dois reais por pessoa,"),
        ("...com garantia mínima de R$ 600 por família.",
         "com garantia mínima de seiscentos reais por família."),
        ("Recheio extra: + R$ 150 por criança de até 6 anos...",
         "E tem recheio extra: mais cento e cinquenta reais por criança de até seis anos,"),
        ("...e + R$ 50 para gestantes, bebês e adolescentes.",
         "e mais cinquenta reais para gestantes, bebês e adolescentes."),
    ]),
    "scene_comb": ("Os combinados", GREEN, [
        ("Mas tem combinados: criança na escola e vacina em dia...",
         "Mas tem combinados: criança na escola, vacina em dia,"),
        ("...pré-natal e peso e altura das crianças acompanhados.",
         "pré-natal para as gestantes, e peso e altura das crianças acompanhados no posto de saúde."),
    ]),
    "scene_rec": ("Como recebe?", BLUE, [
        ("O dinheiro cai todo mês pela Caixa: no app Caixa Tem ou no cartão.",
         "O dinheiro cai todo mês pela Caixa, no aplicativo Caixa Tem, ou no cartão."),
        ("A data segue o final do NIS. De preferência, no nome da mulher da casa.",
         "A data segue o final do NIS. De preferência, no nome da mulher da casa."),
    ]),
    "scene_prot": ("Arrumou emprego?", RED, [
        ("Arrumou emprego? Não perde tudo!", "Arrumou emprego? Não perde tudo!"),
        ("Renda subiu até meio salário mínimo por pessoa? Continua recebendo metade por um tempo.",
         "Pela regra de proteção, se a renda subir até meio salário mínimo por pessoa, "
         "a família continua recebendo metade, por um tempo."),
        ("É escada, não teto!", "É escada, não teto!"),
    ]),
    "scene_fim": ("Salve e compartilhe!", ORANGE, [
        ("Dúvidas? CRAS, Disque Social 121 ou gov.br/mds.",
         "Ficou com dúvida? Procure o CRAS, ligue para o Disque Social, cento e vinte e um, "
         "ou acesse gov ponto bê erre, barra, ême dê ésse."),
        ("Valores podem ser reajustados: confira sempre nos canais oficiais. Tchau!",
         "Os valores podem mudar, então confira sempre nos canais oficiais. Tchau!"),
    ]),
}
LEAD, GAP, TAIL = 0.5, 0.2, 0.7   # segundos: antes da 1ª fala, entre trechos, depois


# ---------- voz ----------
def tts(text, tmp):
    raw = os.path.join(tmp, "raw.wav")
    out = os.path.join(tmp, "out.wav")
    subprocess.run(["RHVoice-test", "-p", "Leticia-F123", "-r", VOICE_RATE, "-o", raw],
                   input=text.encode(), check=True, stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-ar", str(SR), "-ac", "1",
                    "-af", "highpass=f=70,acompressor=threshold=-18dB:ratio=3", out], check=True)
    with wave.open(out) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def build_timeline():
    """Gera a voz e calcula duração das cenas e o tempo de cada legenda."""
    plan, voice_parts, t0 = [], [], 0.0
    with tempfile.TemporaryDirectory() as tmp:
        for fn, _ in gv.SCENES:
            title, color, chunks = SCRIPT[fn.__name__]
            t, cues = LEAD, []
            for cap, spoken in chunks:
                a = tts(spoken, tmp)
                dur = len(a) / SR
                cues.append((t, t + dur, cap))
                voice_parts.append((t0 + t, a))
                t += dur + GAP
            T = max(t - GAP + TAIL, 4.0)
            plan.append((fn, T, title, color, cues))
            t0 += T
    voice = np.zeros(int(t0 * SR) + SR)
    for start, a in voice_parts:
        i = int(start * SR)
        voice[i:i + len(a)] += a
    return plan, voice, t0


# ---------- desenho vertical ----------
_state = {}


def _bg(d, sky=gv.SKY, ground=gv.GRASS, t=0):
    _state["sky"], _state["ground"] = sky, ground
    _orig_bg(d, sky, ground, t)


_orig_bg = gv.background
gv.background = _bg
gv.title_bar = lambda *a, **k: None   # título e legenda são redesenhados no quadro vertical
gv.caption = lambda *a, **k: None


def fit_font(s, maxw, size):
    while size > 20 and font(size).getlength(s) > maxw:
        size -= 2
    return size


def draw_title(d, s, color, t):
    k = pop(t * 2.2)
    size = fit_font(s, 900, 72)
    w = font(size).getlength(s) + 80
    y = 330 - (1 - k) * 260
    rrect(d, [RW / 2 - w / 2, y - 62, RW / 2 + w / 2, y + 62], color, 36, 6)
    d.text((RW / 2, y), s, font=font(size), fill=WHITE, anchor="mm",
           stroke_width=4, stroke_fill=INK)


def draw_caption(d, cues, t):
    cur = None
    for a, b, cap in cues:
        if t >= a - 0.05:
            cur = (a, b, cap)
    if cur is None:
        return
    a, b, cap = cur
    k = pop((t - a + 0.05) * 4)
    lines = wrap(cap, 54, 900)
    lh = 70
    h = 60 + lh * len(lines)
    cy = 1200
    hw, hh = 500 * (0.85 + 0.15 * k), h / 2 * (0.85 + 0.15 * k)
    rrect(d, [RW / 2 - hw, cy - hh, RW / 2 + hw, cy + hh], CREAM, 34, 6)
    if k < 0.6:
        return
    # palavras faladas ficam em destaque (karaokê aproximado)
    prog = clamp01((t - a) / max(0.1, b - a))
    total = sum(len(ln) for ln in lines)
    said = prog * total
    acc = 0
    for i, ln in enumerate(lines):
        y = cy - h / 2 + 30 + lh * i + lh / 2
        x = RW / 2 - font(54).getlength(ln) / 2
        for word in ln.split(" "):
            done = acc + len(word) / 2 <= said
            d.text((x, y), word, font=font(54), anchor="lm",
                   fill=RED if done else INK)
            x += font(54).getlength(word + " ")
            acc += len(word) + 1


def clamp01(x):
    return max(0.0, min(1.0, x))


def clouds(d, t, sky):
    for i, (bx, by, s) in enumerate([(200, 120, 1.3), (850, 70, 1.0), (500, 200, 0.8)]):
        x = (bx + t * 14 * (i + 1)) % (RW + 300) - 150
        for dx, dy, r in [(-40, 10, 30), (0, 0, 42), (45, 10, 32)]:
            d.ellipse([x + dx * s - r * s, by + dy * s - r * s,
                       x + dx * s + r * s, by + dy * s + r * s], fill=WHITE)


def flowers(d, t):
    """Florzinhas balançando no chão (fixas, sem aleatoriedade)."""
    for i in range(16):
        x = 40 + (i * 137) % (RW - 80)
        y = 1460 + (i * 89) % 330
        sway = math.sin(t * 2 + i) * 6
        d.line([x, y + 40, x + sway, y], fill=(40, 120, 50), width=6)
        c = [YEL, RED, WHITE, ORANGE, PURPLE][i % 5]
        for k in range(5):
            a = k * 2 * math.pi / 5 + t * 0.5
            px, py = x + sway + math.cos(a) * 16, y + math.sin(a) * 16
            d.ellipse([px - 12, py - 12, px + 12, py + 12], fill=c, outline=INK, width=3)
        d.ellipse([x + sway - 9, y - 9, x + sway + 9, y + 9], fill=YEL, outline=INK, width=3)


def iris(frame, k):
    r = int(ease(k) * 1150)
    mask = Image.new("L", (RW, RH), 255)
    ImageDraw.Draw(mask).ellipse([RW / 2 - r, RH / 2 - r, RW / 2 + r, RH / 2 + r], fill=0)
    frame.paste(Image.new("RGB", (RW, RH), INK), (0, 0), mask)


def main():
    plan, voice, total = build_timeline()
    music_wav = os.path.join(HERE, "_trilha.wav")
    gv.music(music_wav, total)
    with wave.open(music_wav) as w:
        music = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    os.remove(music_wav)
    n = min(len(music), len(voice))
    # música baixinha, abaixando mais enquanto a Letícia fala
    env = np.convolve(np.abs(voice[:n]), np.ones(SR // 5) / (SR // 5), mode="same")
    duck = np.where(env > 0.01, 0.10, 0.22)
    duck = np.convolve(duck, np.ones(SR // 4) / (SR // 4), mode="same")
    mix = voice[:n] / (np.abs(voice).max() + 1e-9) * 0.9 + music[:n] * duck
    mix = np.int16(np.clip(mix / max(1.0, np.abs(mix).max()), -1, 1) * 32767)
    audio = os.path.join(HERE, "_audio.wav")
    with wave.open(audio, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(mix.tobytes())

    out = os.path.join(HERE, "bolsa_familia_reels.mp4")
    p = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{RW}x{RH}", "-r", str(FPS), "-i", "-", "-i", audio,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "medium",
         "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest",
         "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for idx, (fn, T, title, color, cues) in enumerate(plan):
        for fi in range(int(T * FPS)):
            t = fi / FPS
            stage = Image.new("RGB", (1280, 720))
            sd = ImageDraw.Draw(stage)
            if fn is gv.scene_rec:
                fn(sd, t, T, stage)
            else:
                fn(sd, t, T)
            stage = stage.resize((RW, STAGE_H), Image.LANCZOS)
            frame = Image.new("RGB", (RW, RH), _state["ground"])
            d = ImageDraw.Draw(frame)
            d.rectangle([0, 0, RW, STAGE_Y + 10], fill=_state["sky"])
            clouds(d, t, _state["sky"])
            frame.paste(stage, (0, STAGE_Y))
            flowers(d, t)
            draw_title(d, title, color, t)
            draw_caption(d, cues, t)
            if idx > 0 and t < 0.5:
                iris(frame, t / 0.5)
            if idx < len(plan) - 1 and T - t < 0.5:
                iris(frame, (T - t) / 0.5)
            p.stdin.write(frame.tobytes())
    p.stdin.close()
    p.wait()
    os.remove(audio)
    print("ok ->", out, f"({total:.1f}s)")


if __name__ == "__main__":
    main()
