"""Gera um vídeo animado (estilo desenho) explicando o Bolsa Família.

Uso:  python3 gerar_video.py  ->  bolsa_familia.mp4
Requer: Pillow, numpy, ffmpeg.
"""
import math
import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_fc = {}


def font(size, bold=True):
    size = max(1, int(size))
    k = (size, bold)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONT_B if bold else FONT_R, max(1, size))
    return _fc[k]


# ---------- paleta ----------
INK = (40, 30, 45)
SKY = (140, 210, 245)
GRASS = (120, 200, 100)
YEL = (255, 210, 60)
RED = (235, 85, 80)
BLUE = (60, 120, 220)
GREEN = (40, 170, 90)
ORANGE = (250, 150, 50)
PURPLE = (150, 90, 200)
WHITE = (255, 255, 255)
CREAM = (255, 248, 230)
SKIN1 = (150, 95, 65)
SKIN2 = (225, 175, 135)
SKIN3 = (100, 65, 45)


# ---------- utilidades ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def pop(x):
    """0->1 com 'overshoot' de desenho animado."""
    x = clamp(x)
    if x >= 1:
        return 1.0
    return 1 - math.cos(x * math.pi * 2.5) * math.exp(-5 * x) * (1 - x)


def circle(d, cx, cy, r, fill, w=4):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=INK, width=w)


def rrect(d, box, fill, r=18, w=4):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=INK, width=w)


def text_c(d, xy, s, size, fill=INK, bold=True, stroke=0, stroke_fill=WHITE):
    d.text(xy, s, font=font(size, bold), fill=fill, anchor="mm",
           stroke_width=stroke, stroke_fill=stroke_fill)


def wrap(s, size, maxw, bold=True):
    f = font(size, bold)
    out, line = [], ""
    for word in s.split():
        t = (line + " " + word).strip()
        if f.getlength(t) <= maxw:
            line = t
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def background(d, sky=SKY, ground=GRASS, t=0):
    d.rectangle([0, 0, W, H], fill=sky)
    # nuvens passeando
    for i, (bx, by, s) in enumerate([(150, 90, 1.0), (700, 60, 0.8), (1100, 120, 1.1)]):
        x = (bx + t * 18 * (i + 1)) % (W + 300) - 150
        for dx, dy, r in [(-40, 10, 30), (0, 0, 42), (45, 10, 32)]:
            d.ellipse([x + dx * s - r * s, by + dy * s - r * s,
                       x + dx * s + r * s, by + dy * s + r * s], fill=WHITE)
    d.rectangle([0, 520, W, H], fill=ground)
    d.line([0, 520, W, 520], fill=INK, width=4)


def sun(d, x, y, t):
    for k in range(12):
        a = k * math.pi / 6 + t * 0.6
        d.line([x + math.cos(a) * 55, y + math.sin(a) * 55,
                x + math.cos(a) * 80, y + math.sin(a) * 80], fill=ORANGE, width=8)
    circle(d, x, y, 48, YEL)
    d.ellipse([x - 20, y - 10, x - 10, y + 2], fill=INK)
    d.ellipse([x + 10, y - 10, x + 20, y + 2], fill=INK)
    d.arc([x - 22, y - 8, x + 22, y + 24], 20, 160, fill=INK, width=4)


def person(d, x, y, s, skin, shirt, hair, t=0.0, walk=False, wave_arm=False,
           long_hair=False, blink_off=0.0, pants=(60, 60, 110)):
    """Personagem: (x, y) = posição dos pés."""
    bob = math.sin(t * 10) * 4 * s if walk else math.sin(t * 2.5) * 2 * s
    y = y + bob
    lw = max(3, int(4 * s))
    # pernas
    sw = math.sin(t * 10) * 18 * s if walk else 0
    for side in (-1, 1):
        lx = x + side * 14 * s
        d.line([lx, y - 70 * s, lx + side * sw * (1 if side > 0 else -1), y],
               fill=pants, width=int(16 * s))
        d.ellipse([lx + side * sw * (1 if side > 0 else -1) - 12 * s, y - 6 * s,
                   lx + side * sw * (1 if side > 0 else -1) + 14 * s, y + 6 * s], fill=INK)
    # braços
    for side in (-1, 1):
        sx, sy = x + side * 32 * s, y - 150 * s
        if wave_arm and side == 1:
            a = -math.pi / 2 + math.sin(t * 8) * 0.5
            ex, ey = sx + math.cos(a) * 60 * s + 20 * s, sy + math.sin(a) * 60 * s
        else:
            a = math.sin(t * 10) * 0.4 * side if walk else 0
            ex, ey = sx + side * 10 * s + math.sin(a) * 30 * s, sy + 65 * s
        d.line([sx, sy, ex, ey], fill=shirt, width=int(16 * s))
        circle(d, ex, ey, 9 * s, skin, lw - 1)
    # tronco
    rrect(d, [x - 36 * s, y - 165 * s, x + 36 * s, y - 65 * s], shirt, int(20 * s), lw)
    # cabeça
    hx, hy, hr = x, y - 205 * s, 40 * s
    if long_hair:
        d.rounded_rectangle([hx - hr - 6 * s, hy - hr, hx + hr + 6 * s, hy + hr + 25 * s],
                            radius=int(25 * s), fill=hair, outline=INK, width=lw)
    circle(d, hx, hy, hr, skin, lw)
    d.chord([hx - hr, hy - hr, hx + hr, hy + hr * 0.6], 180, 360, fill=hair, outline=INK, width=lw)
    # olhos (piscando)
    blink = ((t + blink_off) % 3.2) < 0.12
    for side in (-1, 1):
        ex = hx + side * 14 * s
        if blink:
            d.line([ex - 6 * s, hy + 4 * s, ex + 6 * s, hy + 4 * s], fill=INK, width=lw)
        else:
            d.ellipse([ex - 5 * s, hy - 3 * s, ex + 5 * s, hy + 10 * s], fill=INK)
    d.arc([hx - 16 * s, hy + 2 * s, hx + 16 * s, hy + 26 * s], 20, 160, fill=INK, width=lw)
    d.ellipse([hx - 30 * s, hy + 10 * s, hx - 20 * s, hy + 18 * s], fill=(240, 130, 130))
    d.ellipse([hx + 20 * s, hy + 10 * s, hx + 30 * s, hy + 18 * s], fill=(240, 130, 130))


def mom(d, x, y, t, s=1.0, **kw):
    person(d, x, y, s, SKIN1, PURPLE, (35, 25, 25), t, long_hair=True, **kw)


def kid1(d, x, y, t, s=0.62, **kw):
    person(d, x, y, s, SKIN1, ORANGE, (35, 25, 25), t, blink_off=1.1, **kw)


def kid2(d, x, y, t, s=0.55, **kw):
    person(d, x, y, s, SKIN1, GREEN, (60, 35, 20), t, long_hair=True, blink_off=2.0, **kw)


def house(d, x, y, s=1.0, color=(250, 220, 170), roof=RED):
    rrect(d, [x - 110 * s, y - 160 * s, x + 110 * s, y], color, 6)
    d.polygon([(x - 135 * s, y - 155 * s), (x, y - 260 * s), (x + 135 * s, y - 155 * s)],
              fill=roof, outline=INK, width=4)
    rrect(d, [x - 25 * s, y - 85 * s, x + 25 * s, y], (150, 90, 50), 6)
    rrect(d, [x + 45 * s, y - 130 * s, x + 90 * s, y - 85 * s], SKY, 4)


def coin(d, x, y, r=26, label="R$"):
    circle(d, x, y, r, YEL)
    circle(d, x, y, r * 0.72, (255, 225, 110), 2)
    text_c(d, (x, y), label, int(r * 0.6), INK)


def title_bar(d, s, t, color=BLUE):
    k = pop(t * 2.2)
    w = font(44).getlength(s) + 60
    x0 = W / 2 - w / 2
    yy = -80 + 120 * k
    rrect(d, [x0, yy - 38, x0 + w, yy + 38], color, 24, 5)
    text_c(d, (W / 2, yy), s, 44, WHITE, stroke=3, stroke_fill=INK)


def caption(d, s, t, start=0.4, cps=38):
    """Caixa de legenda com efeito máquina de escrever."""
    if t < start:
        return
    n = int((t - start) * cps)
    lines = wrap(s, 30, 1080)
    rrect(d, [70, 568, W - 70, 568 + 26 + 40 * len(lines)], CREAM, 20, 4)
    shown = 0
    for i, ln in enumerate(lines):
        part = ln[:max(0, n - shown)]
        shown += len(ln) + 1
        d.text((100, 580 + i * 40), part, font=font(30), fill=INK)


def bubble(d, x, y, s, t, start=0.0, w=330, size=28, tail=(0, 1)):
    if t < start:
        return
    k = pop((t - start) * 3)
    lines = wrap(s, size, w - 40)
    h = 30 + len(lines) * (size + 8)
    ww, hh = w * k, h * k
    if k < 0.05:
        return
    d.polygon([(x - 20, y + hh / 2 - 6), (x + 15, y + hh / 2 - 6),
               (x - 30 + tail[0] * 60, y + hh / 2 + 40)], fill=WHITE, outline=INK, width=4)
    rrect(d, [x - ww / 2, y - hh / 2, x + ww / 2, y + hh / 2], WHITE, 24, 4)
    d.rectangle([x - 18, y + hh / 2 - 8, x + 12, y + hh / 2 - 1], fill=WHITE)
    if k > 0.9:
        for i, ln in enumerate(lines):
            text_c(d, (x, y - h / 2 + 15 + (size + 8) * i + size / 2 + 2), ln, size)


def check(d, x, y, r, k):
    if k <= 0:
        return
    rr = r * pop(k)
    circle(d, x, y, rr, GREEN)
    d.line([x - rr * 0.45, y, x - rr * 0.1, y + rr * 0.35, x + rr * 0.5, y - rr * 0.35],
           fill=WHITE, width=max(3, int(rr * 0.22)), joint="curve")


# ---------- cenas ----------
def scene_title(d, t, T):
    background(d, t=t)
    sun(d, 1130, 110, t)
    house(d, 260, 520, 1.0)
    mom(d, 560, 560, t, wave_arm=True)
    kid1(d, 670, 560, t)
    kid2(d, 450, 560, t)
    for i in range(7):
        ph = t * 3 + i * 0.9
        cx = 760 + i * 70
        cy = 470 - abs(math.sin(ph)) * 140
        coin(d, cx, cy, 24)
    k = pop(t * 1.4)
    rrect(d, [W / 2 - 360 * k, 165 - 75 * k, W / 2 + 360 * k, 165 + 75 * k], YEL, 30, 6)
    if k > 0.8:
        text_c(d, (W / 2, 140), "BOLSA FAMÍLIA", 64, RED, stroke=4, stroke_fill=INK)
        text_c(d, (W / 2, 205), "explicado em desenho", 32, INK)
    caption(d, "Oi! Eu sou a Dona Maria. Bora entender, sem enrolação, como funciona o Bolsa Família?", t, 1.6)


def scene_oque(d, t, T):
    background(d, t=t)
    title_bar(d, "O que é?", t)
    # rede de circo (analogia)
    nx = 380
    d.line([nx - 230, 500, nx - 230, 300], fill=INK, width=8)
    d.line([nx + 230, 500, nx + 230, 300], fill=INK, width=8)
    sag = 40 + math.sin(t * 4) * 10 * math.exp(-0.3 * max(0, t - 2))
    pts = [(nx - 230 + i * 23, 380 + sag * math.sin(math.pi * i / 20)) for i in range(21)]
    d.line(pts, fill=RED, width=8, joint="curve")
    for i in range(0, 21, 2):
        d.line([pts[i], (pts[i][0], pts[i][1] - 25)], fill=RED, width=3)
    # personagem caindo na rede e quicando
    fall = clamp(t / 1.6)
    py = -100 + (380 + sag - 5 + 100) * ease(fall)
    if t > 1.6:
        py = 380 + sag - 5 - abs(math.sin((t - 1.6) * 3)) * 60 * math.exp(-0.6 * (t - 1.6))
    mom(d, nx, py, t, s=0.55)
    text_c(d, (nx, 250), "rede de proteção", 30, INK)
    # info
    rrect(d, [680, 180, 1240, 500], WHITE, 26, 5)
    items = [("Programa do Governo Federal", 0.8), ("Dinheiro todo mês para", 1.5),
             ("famílias de baixa renda", 1.5), ("Criado em 2003", 2.4),
             ("Volta repaginado em 2023", 3.1)]
    for i, (s, st) in enumerate(items):
        k = ease((t - st) * 3)
        if k > 0:
            d.text((705 + (1 - k) * 60, 210 + i * 56), ("• " if i != 2 else "   ") + s,
                   font=font(28), fill=INK if i not in (3, 4) else BLUE)
    caption(d, "Pensa numa rede de circo: ela não faz o show pelo trapezista, mas segura quem cai "
               "para que possa subir de novo. É transferência de renda + acesso a saúde e educação.", t, 3.6)


def scene_quem(d, t, T):
    background(d, sky=(255, 230, 190), t=t)
    title_bar(d, "Quem pode receber?", t, ORANGE)
    # família
    for i, (fn, xx) in enumerate([(mom, 150), (kid1, 245), (kid2, 320)]):
        fn(d, xx, 520, t)
    person(d, 60, 520, 1.0, SKIN3, BLUE, (20, 20, 20), t, blink_off=0.6)
    # bolo de dinheiro dividido
    k = ease((t - 0.8) * 1.5)
    if k > 0:
        rrect(d, [430, 170, 1220, 500], WHITE, 26, 5)
        text_c(d, (825, 210), "Renda total da família: R$ 800", 32, INK)
        text_c(d, (825, 255), "÷ 4 pessoas", 32, BLUE)
    k2 = clamp((t - 2.2) / 1.5)
    for i in range(4):
        sh = ease(k2 - i * 0.15)
        x = 520 + i * 165
        y = 330 + 10 * math.sin(t * 3 + i)
        if sh > 0:
            coin(d, x, y, int(40 * pop(sh)) + 1, "200")
    if t > 4.2:
        kk = pop((t - 4.2) * 2)
        rrect(d, [530, 400, 1120, 470], (220, 255, 220), 20, 4)
        text_c(d, (825, 435), "R$ 200 por pessoa ≤ R$ 218  ✔", int(30 * kk) + 1, GREEN)
    caption(d, "A regra: dividir a renda da casa pelo número de pessoas. Se der até R$ 218 por pessoa "
               "por mês, a família pode entrar no programa.", t, 1.0)


def cras(d, x, y):
    rrect(d, [x - 170, y - 230, x + 170, y], (235, 235, 245), 8)
    rrect(d, [x - 150, y - 270, x + 150, y - 210], BLUE, 12)
    text_c(d, (x, y - 240), "CRAS", 40, WHITE, stroke=2, stroke_fill=INK)
    rrect(d, [x - 35, y - 110, x + 35, y], (150, 90, 50), 6)
    for dx in (-110, 110):
        rrect(d, [x + dx - 35, y - 180, x + dx + 35, y - 120], SKY, 4)


def scene_cad(d, t, T):
    background(d, t=t)
    title_bar(d, "Passo 1: Cadastro Único", t, GREEN)
    cras(d, 950, 520)
    walk_k = clamp(t / 3.5)
    mx = 120 + 620 * ease(walk_k)
    walking = 0.05 < walk_k < 0.98
    mom(d, mx, 560, t, walk=walking)
    if t > 3.6:
        # prancheta com campos sendo preenchidos
        k = pop((t - 3.6) * 2)
        x0, y0 = 300, 160
        rrect(d, [x0, y0, x0 + 360 * k, y0 + 300 * k], CREAM, 18, 5)
        if k > 0.9:
            text_c(d, (x0 + 180, y0 + 35), "CadÚnico", 30, BLUE)
            fields = ["Quem mora na casa", "Renda de cada um", "Documentos (CPF)", "Endereço"]
            for i, f in enumerate(fields):
                d.text((x0 + 25, y0 + 75 + i * 52), f, font=font(24, False), fill=INK)
                check(d, x0 + 320, y0 + 88 + i * 52, 16, (t - 4.2 - i * 0.4) * 3)
    caption(d, "A porta de entrada é o Cadastro Único, feito no CRAS ou no setor do Cadastro da sua "
               "cidade. Leve documento com CPF de todo mundo e mantenha os dados atualizados!", t, 0.8)


def scene_quanto(d, t, T):
    background(d, sky=(205, 235, 255), t=t)
    title_bar(d, "Quanto recebe?", t, PURPLE)
    blocks = [
        ("R$ 142 por pessoa", "Renda de Cidadania", BLUE, 0.6),
        ("Mínimo de R$ 600", "por família", GREEN, 1.6),
        ("+ R$ 150", "por criança de 0 a 6 anos", ORANGE, 2.6),
        ("+ R$ 50", "gestante, bebê mamando ou 7 a 17 anos", RED, 3.6),
    ]
    for i, (a, b, c, st) in enumerate(blocks):
        k = ease((t - st) * 2.5)
        if k <= 0:
            continue
        y = 150 + i * 100
        x = 80 - (1 - k) * 700
        rrect(d, [x, y, x + 760, y + 82], c, 22, 5)
        d.text((x + 25, y + 10), a, font=font(32), fill=WHITE, stroke_width=2, stroke_fill=INK)
        d.text((x + 25, y + 48), b, font=font(22, False), fill=WHITE)
    # pilha de moedas crescendo
    n = int(clamp((t - 0.6) / 4) * 12)
    for i in range(n):
        coin(d, 1030, 500 - i * 18, 50)
    kid1(d, 1160, 520, t)
    caption(d, "É como montar um sanduíche: tem o pão (R$ 142 por pessoa), garantia de pelo menos "
               "R$ 600, e os recheios extras para crianças pequenas, gestantes e adolescentes.", t, 4.4)


def school(d, x, y, t):
    rrect(d, [x - 70, y - 90, x + 70, y], (255, 230, 150), 6)
    d.polygon([(x - 85, y - 85), (x, y - 140), (x + 85, y - 85)], fill=RED, outline=INK, width=4)
    rrect(d, [x - 18, y - 50, x + 18, y], (150, 90, 50), 4)
    circle(d, x, y - 110, 12, WHITE, 3)


def syringe(d, x, y):
    d.rounded_rectangle([x - 60, y - 16, x + 40, y + 16], radius=8, fill=(200, 240, 255), outline=INK, width=4)
    d.rectangle([x - 55, y - 12, x - 5, y + 12], fill=(120, 200, 255))
    d.line([x + 40, y, x + 80, y], fill=INK, width=4)
    d.line([x - 60, y, x - 85, y], fill=INK, width=8)
    d.line([x - 85, y - 18, x - 85, y + 18], fill=INK, width=6)


def heart(d, x, y, r):
    d.polygon([(x - r, y - r * 0.2), (x, y + r), (x + r, y - r * 0.2)], fill=RED, outline=INK)
    circle(d, x - r / 2, y - r * 0.35, r * 0.55, RED, 0)
    circle(d, x + r / 2, y - r * 0.35, r * 0.55, RED, 0)


def scale_icon(d, x, y):
    rrect(d, [x - 60, y - 20, x + 60, y + 25], (230, 230, 230), 10)
    circle(d, x, y - 40, 32, WHITE)
    d.line([x, y - 40, x + 18, y - 58], fill=RED, width=4)


def scene_comb(d, t, T):
    background(d, sky=(225, 245, 225), ground=(170, 215, 140), t=t)
    title_bar(d, "Os combinados", t, GREEN)
    cards = [
        ("Escola", "frequência mínima (75% de 6 a 17 anos)", school, 0.6),
        ("Vacinas", "caderneta em dia", syringe, 1.6),
        ("Pré-natal", "consultas para gestantes", heart, 2.6),
        ("Peso e altura", "acompanhamento de crianças até 7 anos", scale_icon, 3.6),
    ]
    for i, (a, b, ico, st) in enumerate(cards):
        k = pop((t - st) * 2)
        if k <= 0.02:
            continue
        cx = 175 + i * 310
        cy = 340
        hw, hh = 140 * k, 175 * k
        rrect(d, [cx - hw, cy - hh, cx + hw, cy + hh], WHITE, 24, 5)
        if k > 0.9:
            if ico is heart:
                heart(d, cx, cy - 75, 40)
            elif ico is school:
                school(d, cx, cy - 30, t)
            else:
                ico(d, cx, cy - 75)
            text_c(d, (cx, cy + 30), a, 30)
            for j, ln in enumerate(wrap(b, 20, 250, False)):
                text_c(d, (cx, cy + 70 + j * 26), ln, 20, bold=False)
            check(d, cx + 110, cy - 145, 26, (t - st - 0.6) * 3)
    caption(d, "O dinheiro vem com combinados: criança na escola, vacina em dia, pré-natal e saúde "
               "acompanhada. É um pacto: o governo ajuda hoje e investe no futuro da família.", t, 4.4)


def phone(d, x, y, t):
    rrect(d, [x - 80, y - 150, x + 80, y + 150], (40, 40, 50), 24, 5)
    rrect(d, [x - 65, y - 125, x + 65, y + 120], WHITE, 10, 2)
    text_c(d, (x, y - 95), "CAIXA Tem", 18, BLUE)
    k = pop((t - 1.2) * 2)
    if k > 0.1:
        rrect(d, [x - 55, y - 60, x + 55, y + 10], (220, 255, 220), 12, 3)
        text_c(d, (x, y - 37), "Depósito", 18, GREEN)
        text_c(d, (x, y - 10), "recebido!", 18, GREEN)
    coin(d, x, y + 65, int(30 * max(0.05, k)))


def card(d, x, y, ang=0):
    img = Image.new("RGBA", (340, 210), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    g.rounded_rectangle([5, 5, 335, 205], radius=22, fill=(40, 110, 200), outline=INK, width=5)
    g.rectangle([5, 50, 335, 85], fill=YEL)
    g.rounded_rectangle([30, 110, 90, 155], radius=8, fill=(240, 200, 90), outline=INK, width=3)
    g.text((110, 120), "BOLSA FAMÍLIA", font=font(24), fill=WHITE)
    g.text((30, 165), "**** **** 1234", font=font(20, False), fill=WHITE)
    return img.rotate(ang, expand=True, resample=Image.BICUBIC), (x, y)


def scene_rec(d, t, T, frame):
    background(d, t=t)
    title_bar(d, "Como recebe?", t, BLUE)
    mom(d, 180, 560, t)
    phone(d, 470, 330, t)
    # calendário
    k = pop((t - 2.2) * 2)
    if k > 0.05:
        x0, y0 = 860, 170
        rrect(d, [x0, y0, x0 + 330 * k, y0 + 300 * k], WHITE, 18, 5)
        if k > 0.9:
            rrect(d, [x0, y0, x0 + 330, y0 + 60], RED, 18, 5)
            text_c(d, (x0 + 165, y0 + 30), "Calendário", 28, WHITE)
            for i in range(10):
                cx = x0 + 45 + (i % 5) * 60
                cy = y0 + 110 + (i // 5) * 90
                hl = int((t * 2) % 10) == i
                circle(d, cx, cy, 24, YEL if hl else (235, 235, 235), 3)
                text_c(d, (cx, cy), str((i + 1) % 10), 22)
            text_c(d, (x0 + 165, y0 + 275), "pelo final do NIS", 22, bold=False)
    img, pos = card(d, 700, 380, math.sin(t * 2) * 8)
    frame.paste(img, (int(pos[0] - img.width / 2), int(pos[1] - img.height / 2 + 90)), img)
    caption(d, "O pagamento sai todo mês pela Caixa, no app Caixa Tem ou no cartão, seguindo o "
               "calendário pelo último número do NIS. De preferência, em nome da mulher da casa.", t, 0.6)


def scene_prot(d, t, T):
    background(d, sky=(255, 220, 200), t=t)
    title_bar(d, "Arrumou emprego? Não perde tudo!", t, RED)
    # escada (analogia)
    for i in range(5):
        rrect(d, [120 + i * 130, 520 - (i + 1) * 60, 250 + i * 130, 520], (200, 160, 110), 4, 4)
    step = clamp((t - 0.6) / 4.0) * 4
    si = int(step)
    fr = step - si
    mx = 185 + si * 130 + fr * 130
    my = 520 - (si + 1) * 60 - (math.sin(fr * math.pi) * 30 if si < 4 else 0)
    mom(d, mx, my, t, s=0.55, walk=si < 4)
    if t > 1.0:
        kk = pop((t - 1.0) * 2)
        rrect(d, [200, 250 - 30 * kk, 470, 250 + 30 * kk], WHITE, 14, 4)
        if kk > 0.9:
            text_c(d, (335, 250), "novo emprego!", 26, GREEN)
    # medidor de benefício
    k = ease((t - 2.5) / 1.2)
    x0, y0 = 900, 180
    rrect(d, [x0, y0, x0 + 280, y0 + 300], WHITE, 22, 5)
    text_c(d, (x0 + 140, y0 + 30), "Benefício", 26)
    barh = 200 * (1 - 0.5 * k)
    rrect(d, [x0 + 95, y0 + 260 - barh, x0 + 185, y0 + 260], GREEN, 10, 4)
    text_c(d, (x0 + 140, y0 + 230), "100%" if k < 0.5 else "50%", 26, WHITE, stroke=2, stroke_fill=INK)
    caption(d, "Regra de Proteção: se a renda subir (até meio salário mínimo por pessoa), "
               "a família segue recebendo metade por um tempo. É escada, não teto!", t, 1.4)


def scene_fim(d, t, T):
    background(d, sky=(255, 240, 160), ground=(250, 200, 90), t=t)
    sun(d, 120, 110, t)
    for i in range(14):
        ph = (t * 0.35 + i * 0.137) % 1
        x = 60 + (i * 97) % W
        y = -40 + ph * 760
        c = [RED, BLUE, GREEN, ORANGE, PURPLE][i % 5]
        d.rectangle([x, y, x + 14, y + 22], fill=c)
    mom(d, 1000, 560, t, wave_arm=True)
    kid1(d, 1110, 560, t, wave_arm=True)
    kid2(d, 890, 560, t)
    k = pop(t * 1.5)
    rrect(d, [80, 170, 80 + 700 * k, 170 + 330 * k], WHITE, 26, 5)
    if k > 0.9:
        text_c(d, (430, 215), "Ficou com dúvida?", 38, RED)
        rows = [("CRAS da sua cidade", 0.8), ("Disque Social 121 (ligação gratuita)", 1.3),
                ("gov.br/mds", 1.8), ("App Bolsa Família", 2.3)]
        for i, (s, st) in enumerate(rows):
            kk = ease((t - st) * 3)
            if kk > 0:
                check(d, 130, 285 + i * 52, 18, kk)
                d.text((165 - (1 - kk) * 30, 268 + i * 52), s, font=font(28), fill=INK)
    caption(d, "Valores de referência das regras de 2023 — podem ser reajustados. "
               "Sempre confira no CRAS ou nos canais oficiais. Até a próxima!", t, 2.8)


SCENES = [
    (scene_title, 7.5), (scene_oque, 11.0), (scene_quem, 10.0), (scene_cad, 10.0),
    (scene_quanto, 11.0), (scene_comb, 11.0), (scene_rec, 10.0), (scene_prot, 11.0),
    (scene_fim, 9.0),
]


# ---------- trilha sonora sintetizada ----------
def music(path, dur, sr=44100):
    bpm = 112
    beat = 60 / bpm
    notes = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

    def f(n, o=4):
        return 440 * 2 ** ((notes[n] + 12 * (o - 4) - 9) / 12)

    mel = "E G A G E D C D E E D C D E G A G E D C D C C -".split()
    chords = [("C", "E", "G"), ("A", "C", "E"), ("F", "A", "C"), ("G", "B", "D")]
    n = int(dur * sr)
    out = np.zeros(n)
    tt = np.arange(int(beat * sr)) / sr

    def pluck(freq, length, vol):
        x = np.arange(int(length * sr)) / sr
        env = np.exp(-x * 6)
        return vol * env * (np.sin(2 * np.pi * freq * x) + 0.3 * np.sin(4 * np.pi * freq * x))

    i = 0
    pos = 0.0
    while pos < dur:
        s0 = int(pos * sr)
        m = mel[i % len(mel)]
        if m != "-":
            w = pluck(f(m, 5), beat * 0.9, 0.18)
            out[s0:s0 + len(w)] += w[:max(0, n - s0)]
        if i % 4 == 0:
            ch = chords[(i // 8) % 4]
            for j, c in enumerate(ch):
                w = pluck(f(c, 3 if j == 0 else 4), beat * 3.5, 0.07)
                out[s0:s0 + len(w)] += w[:max(0, n - s0)]
        if i % 2 == 0:  # "chocalho"
            k = np.random.uniform(-1, 1, int(0.05 * sr)) * np.exp(-np.arange(int(0.05 * sr)) / 400) * 0.05
            out[s0:s0 + len(k)] += k[:max(0, n - s0)]
        i += 1
        pos += beat / 2
    fade = int(2 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = np.int16(np.clip(out / (np.abs(out).max() + 1e-9) * 0.6, -1, 1) * 32767)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(out.tobytes())


def main():
    total = sum(T for _, T in SCENES)
    wav = os.path.join(HERE, "_trilha.wav")
    music(wav, total)
    out = os.path.join(HERE, "bolsa_familia.mp4")
    p = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-preset", "medium",
         "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)
    prev = None
    for idx, (fn, T) in enumerate(SCENES):
        for fi in range(int(T * FPS)):
            t = fi / FPS
            frame = Image.new("RGB", (W, H))
            d = ImageDraw.Draw(frame)
            if fn is scene_rec:
                fn(d, t, T, frame)
            else:
                fn(d, t, T)
            # transição: círculo "íris" de desenho animado
            if prev is not None and t < 0.5:
                r = int(ease(t / 0.5) * 800)
                mask = Image.new("L", (W, H), 255)
                ImageDraw.Draw(mask).ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=0)
                frame.paste(Image.new("RGB", (W, H), INK), (0, 0), mask)
            if T - t < 0.5 and idx < len(SCENES) - 1:
                r = int(ease((T - t) / 0.5) * 800)
                mask = Image.new("L", (W, H), 255)
                ImageDraw.Draw(mask).ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=0)
                frame.paste(Image.new("RGB", (W, H), INK), (0, 0), mask)
            p.stdin.write(frame.tobytes())
        prev = fn
    p.stdin.close()
    p.wait()
    os.remove(wav)
    print("ok ->", out, f"({total:.0f}s)")


if __name__ == "__main__":
    main()
