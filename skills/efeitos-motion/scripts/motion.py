#!/usr/bin/env python3
"""Motor de efeitos motion para vídeos verticais (Reels/TikTok/Shorts).

Uso:
  python motion.py render plano.json            # renderiza o vídeo final
  python motion.py preview plano.json 12.5      # salva um PNG do segundo 12.5
  python motion.py efeitos                      # lista os efeitos disponíveis

O plano é um JSON:
  {
    "entrada": "meu-video.mp4",
    "saida": "editado.mp4",
    "efeitos": [
      {"tipo": "titulo_lista", "inicio": 0, "fim": 6, ...},
      {"tipo": "legenda", "inicio": 0, "fim": 49, "texto": "..."}
    ]
  }

Os efeitos são aplicados na ordem da lista: os que mexem no vídeo inteiro
(fundo, zoom, recorte) vêm antes dos que só desenham por cima (cards, texto).
"""
import json
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(AQUI, "..", "assets")

COR = {
    "amarelo": (245, 213, 71),
    "creme": (239, 235, 227),
    "vermelho": (210, 48, 44),
    "azul": (46, 75, 198),
    "laranja": (217, 119, 87),
    "verde": (52, 199, 89),
    "card": (24, 24, 24),
    "branco": (255, 255, 255),
    "preto": (0, 0, 0),
    "cinza": (150, 150, 150),
}

_fontes = {}


def fonte(nome, tam):
    arq = {
        "serif": "PlayfairDisplay-Bold.woff",
        "sans": "Inter-Medium.woff",
        "sans_bold": "Inter-SemiBold.woff",
    }[nome]
    chave = (arq, int(tam))
    if chave not in _fontes:
        _fontes[chave] = ImageFont.truetype(os.path.join(ASSETS, "fonts", arq), max(6, int(tam)))
    return _fontes[chave]


def cor(v, padrao="branco"):
    if v is None:
        v = padrao
    if isinstance(v, (list, tuple)):
        return tuple(v)
    if v in COR:
        return COR[v]
    v = v.lstrip("#")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- easing / tempo

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def ease_in(x):
    return clamp(x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_back(x, s=1.7):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def envelope(t, ini, fim, ent=0.35, sai=0.25):
    """0→1 na entrada, 1 no meio, 1→0 na saída."""
    if t < ini or t > fim:
        return 0.0
    a = (t - ini) / ent if ent > 0 else 1
    b = (fim - t) / sai if sai > 0 else 1
    return clamp(min(a, b))


# ---------------------------------------------------------------- desenho

def camada(W, H):
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def sombra(img, raio=18, opac=110, dy=8):
    """Devolve img (RGBA) com sombra suave embaixo, com margem extra."""
    m = raio * 2
    base = Image.new("RGBA", (img.width + 2 * m, img.height + 2 * m), (0, 0, 0, 0))
    a = img.getchannel("A").point(lambda v: v * opac // 255)
    s = Image.new("RGBA", img.size, (0, 0, 0, 255))
    s.putalpha(a)
    base.alpha_composite(s, (m, m + dy))
    base = base.filter(ImageFilter.GaussianBlur(raio / 2))
    base.alpha_composite(img, (m, m))
    return base


def retangulo(w, h, r, fill, borda=None, larg_borda=0):
    img = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(r), fill=fill,
                        outline=borda, width=int(larg_borda))
    return img


def colar(canvas, img, cx, cy, escala=1.0, rot=0.0, alpha=1.0):
    """Cola img centralizada em (cx, cy) com escala, rotação e opacidade."""
    if alpha <= 0.003 or escala <= 0.01:
        return
    if escala != 1.0:
        img = img.resize((max(1, int(img.width * escala)), max(1, int(img.height * escala))),
                         Image.BICUBIC)
    if rot:
        img = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2))) \
        if _cabe(canvas, img, cx, cy) else _colar_recortado(canvas, img, cx, cy)


def _cabe(canvas, img, cx, cy):
    x, y = int(cx - img.width / 2), int(cy - img.height / 2)
    return x >= 0 and y >= 0 and x + img.width <= canvas.width and y + img.height <= canvas.height


def _colar_recortado(canvas, img, cx, cy):
    x, y = int(cx - img.width / 2), int(cy - img.height / 2)
    tmp = camada(canvas.width, canvas.height)
    tmp.paste(img, (x, y))
    canvas.alpha_composite(tmp)


def texto_img(txt, fnt, fill, sombra_txt=True, tracking=0):
    bb = fnt.getbbox(txt)
    w = bb[2] - bb[0] + abs(tracking) * len(txt) + 8
    h = bb[3] + 12
    img = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if tracking:
        x = 4
        for ch in txt:
            d.text((x, 2), ch, font=fnt, fill=fill)
            x += fnt.getlength(ch) + tracking
    else:
        d.text((4 - bb[0], 2), txt, font=fnt, fill=fill)
    if sombra_txt:
        img = sombra(img, raio=8, opac=150, dy=2)
    return img


def cobrir(img, W, H):
    """Redimensiona img para cobrir W×H (como background-size: cover)."""
    r = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * r + 1), int(img.height * r + 1)), Image.BICUBIC)
    x, y = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def asterisco(tam, fill=(255, 255, 255)):
    """Faísca de 10 pontas (ícone genérico de IA)."""
    s = tam * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2
    for i in range(10):
        a = i * math.pi / 5 + 0.15 * (i % 2)
        r = s * (0.48 if i % 2 == 0 else 0.4)
        d.line([(c, c), (c + r * math.cos(a), c + r * math.sin(a))], fill=fill, width=int(s * 0.09))
        d.ellipse([c + r * math.cos(a) - s * 0.045, c + r * math.sin(a) - s * 0.045,
                   c + r * math.cos(a) + s * 0.045, c + r * math.sin(a) + s * 0.045], fill=fill)
    return img.resize((tam, tam), Image.LANCZOS)


def check_icon(tam, fundo=COR["verde"], traco=(255, 255, 255)):
    s = tam * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, s - 1, s - 1], fill=fundo)
    d.line([(s * .28, s * .52), (s * .44, s * .68), (s * .74, s * .34)], fill=traco,
           width=int(s * .11), joint="curve")
    return img.resize((tam, tam), Image.LANCZOS)


def zigue(w, h, n, fill, larg):
    img = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(i * w / n, 0 if i % 2 else h - 1) for i in range(n + 1)]
    d.line(pts, fill=fill, width=int(larg), joint="curve")
    return img


def xis(tam, fill, larg):
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (tam, tam)], fill=fill, width=larg)
    d.line([(0, tam), (tam, 0)], fill=fill, width=larg)
    return img


# ---------------------------------------------------------------- vídeo / máscara

def sonda(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate:format=duration",
        "-of", "json", path])
    j = json.loads(out)
    s = j["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(n) / float(d), float(j["format"]["duration"])


def miniatura(path, t, W, H):
    """Um quadro de um vídeo (ou a própria imagem) como RGBA."""
    if path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        return Image.open(path).convert("RGBA")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1",
                          "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    if len(raw) < W * H * 3:
        return Image.new("RGBA", (W, H), (40, 40, 40, 255))
    return Image.frombytes("RGB", (W, H), raw[:W * H * 3]).convert("RGBA")


class Segmentador:
    """Recorta a pessoa do fundo (modelo selfie segmenter do MediaPipe, roda offline na CPU)."""

    def __init__(self):
        try:
            from ai_edge_litert.interpreter import Interpreter
        except ImportError:
            try:
                from tflite_runtime.interpreter import Interpreter
            except ImportError:
                sys.exit("Este efeito precisa recortar a pessoa. Instale: pip install ai-edge-litert")
        self.it = Interpreter(model_path=os.path.join(ASSETS, "selfie_segmenter.tflite"))
        self.it.allocate_tensors()
        self.ent = self.it.get_input_details()[0]
        self.sai = self.it.get_output_details()[0]
        self.lado = int(self.ent["shape"][1])
        self.ant = None

    def __call__(self, frame_np, ts_ms):
        H, W = frame_np.shape[:2]
        x = np.asarray(Image.fromarray(frame_np).resize((self.lado, self.lado), Image.BILINEAR),
                       np.float32)[None] / 255.0
        self.it.set_tensor(self.ent["index"], x)
        self.it.invoke()
        m = self.it.get_tensor(self.sai["index"])[0, ..., 0]
        if self.ant is not None:
            m = 0.6 * m + 0.4 * self.ant  # suaviza o tremido entre quadros
        self.ant = m
        # sobe a resolução suavizando antes de cortar: borda limpa em vez de "serrilhada"
        mask = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), "L").resize((W, H), Image.BICUBIC)
        mask = mask.filter(ImageFilter.GaussianBlur(4 * W / 720))
        return mask.point(lambda v: int(255 * clamp((v - 120) / 40)))


class Contexto:
    def __init__(self, plano, W, H, fps):
        self.plano, self.W, self.H, self.fps = plano, W, H, fps
        self.u = W / 720.0
        self.cache = {}
        self._seg = None
        self.frame_np = None
        self.ts = 0
        self.mask = None  # máscara da pessoa já na geometria atual do canvas

    def mascara(self):
        if self.mask is None:
            if self._seg is None:
                self._seg = Segmentador()
            self.mask = self._seg(self.frame_np, self.ts)
        return self.mask

    def transformar_mascara(self, fn):
        if self.mask is not None:
            self.mask = fn(self.mask)

    def pessoa(self, canvas):
        """Recorte RGBA da pessoa a partir do canvas atual."""
        p = canvas.copy()
        p.putalpha(ImageChops.multiply(p.getchannel("A"), self.mascara()))
        return p

    def thumbs(self, ef, n):
        chave = ("thumbs", id(ef))
        if chave not in self.cache:
            W, H = self.W // 2, self.H // 2
            midias = ef.get("midias") or []
            out = []
            if midias:
                for i in range(n):
                    out.append(miniatura(midias[i % len(midias)], 1.0, W, H))
            else:
                _, _, _, dur = sonda(self.plano["entrada"])
                rnd = random.Random(7)
                for i in range(n):
                    img = miniatura(self.plano["entrada"], rnd.uniform(0.5, max(1, dur - 0.5)), W, H)
                    tint = Image.new("RGBA", img.size, (*rnd.choice(
                        [(120, 60, 200), (30, 30, 30), (200, 160, 40), (40, 120, 200), (0, 0, 0)]), 70))
                    img.alpha_composite(tint)
                    out.append(img)
            self.cache[chave] = out
        return self.cache[chave]


# ---------------------------------------------------------------- efeitos

EFEITOS = {}


def efeito(nome, descricao):
    def reg(fn):
        fn.descricao = descricao
        EFEITOS[nome] = fn
        return fn
    return reg


@efeito("parede_videos", "Grade de vídeos que dá zoom até o seu vídeo ocupar a tela.")
def parede_videos(cv, t, ef, ctx):
    W, H = cv.size
    ini, fim = ef["inicio"], ef["fim"]
    dz = ef.get("duracao_zoom", min(1.2, (fim - ini) * 0.6))
    p = ease_in_out((t - (fim - dz)) / dz)
    esc0 = ef.get("escala_inicial", 0.34)
    c = esc0 + (1 - esc0) * p
    gap = 18 * ctx.u
    th = ctx.thumbs(ef, 24)
    fundo = Image.new("RGBA", (W, H), (8, 8, 10, 255))
    tw, thh = max(1, int(W * c)), max(1, int(H * c))
    drift = (t - ini) * 6 * ctx.u * (1 - p)
    k = 0
    for j in range(-3, 4):
        for i in range(-2, 3):
            if i == 0 and j == 0:
                continue
            x = W / 2 + i * (W + gap) * c - tw / 2
            y = H / 2 + j * (H + gap) * c - thh / 2 + (drift if i % 2 else -drift)
            k += 1
            if x > W or y > H or x + tw < 0 or y + thh < 0:
                continue
            tile = th[k % len(th)].resize((tw, thh), Image.BILINEAR)
            r = retangulo(tw, thh, 16 * c * 2, (255, 255, 255, 255))
            tile.putalpha(r.getchannel("A"))
            fundo.alpha_composite(tile, (int(x), int(y)))
    principal = cv.resize((tw, thh), Image.BILINEAR)
    fundo.alpha_composite(principal, (int(W / 2 - tw / 2), int(H / 2 - thh / 2)))

    def geo(m):
        z = Image.new("L", (W, H), 0)
        z.paste(m.resize((tw, thh), Image.BILINEAR), (int(W / 2 - tw / 2), int(H / 2 - thh / 2)))
        return z
    ctx.transformar_mascara(geo)
    return fundo


@efeito("zoom_palavra", "Punch-in (zoom rápido) no rosto quando uma palavra-chave é dita.")
def zoom_palavra(cv, t, ef, ctx):
    W, H = cv.size
    z = 1 + (ef.get("zoom", 1.25) - 1) * envelope(t, ef["inicio"], ef["fim"], 0.18, 0.2) ** 0.7
    cx, cy = ef.get("centro", [0.5, 0.36])
    cx, cy = cx * W, cy * H
    box = (cx - cx / z, cy - cy / z, cx + (W - cx) / z, cy + (H - cy) / z)
    out = cv.resize((W, H), Image.BICUBIC, box=box)
    ctx.transformar_mascara(lambda m: m.resize((W, H), Image.BILINEAR, box=box))
    if ef.get("palavra"):
        a = envelope(t, ef["inicio"], ef["fim"], 0.15, 0.15)
        img = texto_img(ef["palavra"], fonte("serif", 96 * ctx.u), cor(ef.get("cor"), "amarelo"))
        colar(out, img, W / 2, ef.get("y", 0.5) * H, 0.7 + 0.3 * ease_back(a), alpha=a)
    return out


@efeito("fundo_trocado", "Troca o fundo atrás da pessoa por uma imagem ou cor.")
def fundo_trocado(cv, t, ef, ctx):
    W, H = cv.size
    chave = ("fundo", id(ef))
    if chave not in ctx.cache:
        f = ef.get("fundo", "#111111")
        if isinstance(f, str) and os.path.exists(f):
            bg = cobrir(Image.open(f).convert("RGBA"), W, H)
            if ef.get("desfoque"):
                bg = bg.filter(ImageFilter.GaussianBlur(ef["desfoque"]))
        else:
            bg = Image.new("RGBA", (W, H), (*cor(f), 255))
        ctx.cache[chave] = bg
    bg = ctx.cache[chave].copy()
    bg.alpha_composite(ctx.pessoa(cv))
    a = envelope(t, ef["inicio"], ef["fim"], ef.get("transicao", 0.25), ef.get("transicao", 0.25))
    if a >= 1:
        return bg
    return Image.blend(cv, bg, a)


@efeito("recorte_papel", "Pessoa recortada com borda branca de adesivo, fundo creme, bloco amarelo, rabiscos e letras de recorte de revista.")
def recorte_papel(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    ini = ef["inicio"]
    boil = int((t - ini) * 8)  # tremidinha de stop-motion a cada 1/8 s
    rnd = random.Random(boil)
    j = lambda: rnd.uniform(-1.5, 1.5) * u  # noqa: E731
    out = Image.new("RGBA", (W, H), (*cor(ef.get("fundo"), "creme"), 255))
    a = ease_out((t - ini) / 0.3)
    bloco = retangulo(W * 0.52, H * 0.42, 0, (*cor(ef.get("cor_bloco"), "amarelo"), 255))
    colar(out, bloco, W * 0.82 + j(), H * 0.36 + j(), alpha=a)
    pessoa = ctx.pessoa(cv)
    borda = int(ef.get("borda", 9) * u)
    m = pessoa.getchannel("A").resize((W // 4, H // 4), Image.BILINEAR)
    m = m.filter(ImageFilter.MaxFilter(2 * max(1, borda // 4) + 1)).resize((W, H), Image.BILINEAR)
    m = m.point(lambda v: 255 if v > 90 else 0).filter(ImageFilter.GaussianBlur(1))
    adesivo = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    adesivo.putalpha(m)
    adesivo = sombra(adesivo, raio=14, opac=60, dy=6)
    out.alpha_composite(adesivo, (-28 + int(j()), -28 + int(j())))
    out.alpha_composite(pessoa)
    d_in = lambda k: ease_back((t - ini - 0.12 * k) / 0.35)  # noqa: E731
    colar(out, zigue(70 * u, 150 * u, 9, (*COR["azul"], 255), 3 * u), 70 * u + j(), H * 0.68 + j(), d_in(1))
    colar(out, zigue(110 * u, 70 * u, 14, (*COR["vermelho"], 255), 3 * u), W - 70 * u + j(), H * 0.73 + j(), d_in(2))
    colar(out, xis(int(16 * u), (40, 40, 40, 255), int(2 * u)), 45 * u + j(), H * 0.6, d_in(2))
    colar(out, xis(int(14 * u), (*COR["vermelho"], 255), int(2 * u)), W - 50 * u, H * 0.66 + j(), d_in(3))
    letras = ef.get("letras")
    if letras:
        lx, ly = ef.get("pos_letras", [0.3, 0.52])
        caixas = []
        for i, ch in enumerate(letras):
            fnd = (*COR["amarelo"], 255) if not ch.isalnum() else (255, 255, 255, 255)
            fc = [COR["vermelho"], COR["azul"], COR["preto"]][i % 3] if ch.isalnum() else COR["preto"]
            b = retangulo(54 * u, 66 * u, 3 * u, fnd, (30, 30, 30, 255), 2 * u)
            tx = texto_img(ch, fonte("serif", 52 * u), (*fc, 255), sombra_txt=False)
            b.alpha_composite(tx, (int((b.width - tx.width) / 2), int((b.height - tx.height) / 2 - 4 * u)))
            caixas.append(b)
        x0 = lx * W
        for i, b in enumerate(caixas):
            s = ease_back((t - ini - 0.25 - 0.08 * i) / 0.3)
            colar(out, b, x0 + i * 58 * u + j(), ly * H + j(), s, rot=rnd.uniform(-4, 4))
        if ef.get("circulo", True):
            s = clamp((t - ini - 0.6) / 0.4)
            if s > 0:
                el = Image.new("RGBA", (int(78 * u), int(96 * u)), (0, 0, 0, 0))
                ImageDraw.Draw(el).arc([2, 2, el.width - 3, el.height - 3], 200, 200 + 360 * s,
                                       fill=(*COR["vermelho"], 255), width=int(3 * u))
                colar(out, el, x0 + j(), ly * H + j(), rot=-12)
    if ef.get("etiqueta"):
        te = ef.get("etiqueta_em", ini + 1.0)
        s = ease_back((t - te) / 0.3)
        if s > 0:
            tx = texto_img(ef["etiqueta"], fonte("serif", 24 * u), (20, 20, 20, 255), sombra_txt=False)
            pill = retangulo(tx.width + 28 * u, tx.height + 10 * u, (tx.height + 10 * u) / 2,
                             (*COR["amarelo"], 255))
            pill.alpha_composite(tx, (int(14 * u), int(5 * u)))
            ex, ey = ef.get("pos_etiqueta", [0.73, 0.525])
            colar(out, sombra(pill, 8, 80, 3), ex * W + j(), ey * H + j(), s, rot=-2)
    ent = ease_out((t - ini) / 0.2)
    return out if ent >= 1 else Image.blend(cv, out, ent)


@efeito("afasta_e_revela", "A câmera 'se afasta': o vídeo encolhe e revela um fundo novo atrás.")
def afasta_e_revela(cv, t, ef, ctx):
    W, H = cv.size
    p = ease_in_out((t - ef["inicio"]) / ef.get("duracao", 0.8))
    volta = ease_in_out((t - (ef["fim"] - ef.get("duracao_volta", 0.5))) / ef.get("duracao_volta", 0.5))
    esc = 1 - (1 - ef.get("escala", 0.72)) * p * (1 - volta)
    out = Image.new("RGBA", (W, H), (*cor(ef.get("fundo"), "creme"), 255))
    if ef.get("bloco", True):
        out.alpha_composite(retangulo(W * 0.55, H * 0.5, 0, (*COR["amarelo"], 255)),
                            (int(W * 0.5), int(H * 0.12)))
    nw, nh = int(W * esc), int(H * esc)
    x, y = (W - nw) // 2, H - nh  # ancorado embaixo, como se a câmera recuasse
    if ef.get("modo", "recorte") == "card":
        card = cv.resize((nw, nh), Image.BICUBIC)
        card.putalpha(retangulo(nw, nh, 28 * ctx.u * p, (0, 0, 0, 255)).getchannel("A"))
        out.alpha_composite(sombra(card, 24, 120, 10), (x - 48, y - 48))
        ctx.transformar_mascara(lambda m: _reposiciona(m, W, H, nw, nh, x, y))
        return out
    m = ctx.mascara()
    pessoa = ctx.pessoa(cv).resize((nw, nh), Image.BICUBIC)
    fundo_orig = cv.resize((nw, nh), Image.BICUBIC)
    # o fundo antigo some à medida que a câmera recua
    fundo_orig.putalpha(int(255 * (1 - p * (1 - volta))))
    out.alpha_composite(fundo_orig, (x, y))
    mm = m.resize((nw, nh), Image.BILINEAR).filter(ImageFilter.MaxFilter(9)).point(lambda v: 255 if v > 90 else 0)
    contorno = Image.new("RGBA", (nw, nh), (255, 255, 255, int(255 * p)))
    contorno.putalpha(ImageChops.multiply(mm, Image.new("L", (nw, nh), int(255 * p * (1 - volta)))))
    out.alpha_composite(contorno, (x, y))
    out.alpha_composite(pessoa, (x, y))
    ctx.transformar_mascara(lambda mk: _reposiciona(mk, W, H, nw, nh, x, y))
    return out


def _reposiciona(m, W, H, nw, nh, x, y):
    z = Image.new("L", (W, H), 0)
    z.paste(m.resize((nw, nh), Image.BILINEAR), (x, y))
    return z


@efeito("orbita", "Cards/miniaturas girando em órbita em volta da pessoa (passam por trás e pela frente).")
def orbita(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    n = ef.get("quantidade", 6)
    th = ctx.thumbs(ef, n)
    a = envelope(t, ef["inicio"], ef["fim"], 0.5, 0.4)
    cx, cy = ef.get("centro", [0.5, 0.66])
    cx, cy = cx * W, cy * H
    rx, ry = W * ef.get("raio", 0.42) * ease_out(a), H * 0.06 * ease_out(a)
    vel = ef.get("velocidade", 0.9)
    cards = []
    for i in range(n):
        ang = vel * (t - ef["inicio"]) + 2 * math.pi * i / n
        prof = math.sin(ang)
        x, y = cx + rx * math.cos(ang), cy + ry * prof
        esc = (0.78 + 0.22 * prof) * ef.get("tamanho", 1.0)
        cw, ch = int(150 * u), int(230 * u)
        c = th[i % len(th)].resize((cw, ch), Image.BILINEAR)
        r = retangulo(cw, ch, 12 * u, (255, 255, 255, 255))
        c.putalpha(r.getchannel("A"))
        if prof < 0:
            c.alpha_composite(Image.new("RGBA", c.size, (0, 0, 0, int(-prof * 90))))
            c.putalpha(r.getchannel("A"))
        cards.append((prof, x, y, esc, sombra(c, 12, 90, 5)))
    cards.sort(key=lambda k: k[0])
    pessoa = ctx.pessoa(cv)
    for prof, x, y, esc, c in cards:
        if prof < 0:
            colar(cv, c, x, y, esc, alpha=a)
    cv.alpha_composite(pessoa)
    for prof, x, y, esc, c in cards:
        if prof >= 0:
            colar(cv, c, x, y, esc, alpha=a)
    return cv


@efeito("capa_revista", "Palavra gigante em serifa no topo, estilo capa de revista (a cabeça pode passar na frente).")
def capa_revista(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    a = envelope(t, ef["inicio"], ef["fim"], 0.4, 0.3)
    palavra = ef.get("palavra", "EDIÇÃO")
    tam = ef.get("tamanho", 1.0) * 128 * u
    fnt = fonte("serif", tam)
    while fnt.getlength(palavra) > W * 0.92 and tam > 20:
        tam *= 0.94
        fnt = fonte("serif", tam)
    img = texto_img(palavra, fnt, (*cor(ef.get("cor")), 255), tracking=int(-2 * u))
    pessoa = ctx.pessoa(cv) if ef.get("atras_da_pessoa", True) else None
    y = ef.get("y", 0.085) * H + 30 * u * (1 - ease_out(a))
    colar(cv, img, W / 2, y + img.height / 2, 1.06 - 0.06 * ease_out(a), alpha=a)
    if ef.get("subtitulo"):
        st = texto_img(ef["subtitulo"].upper(), fonte("sans_bold", 15 * u), (255, 255, 255, 230), tracking=int(4 * u))
        colar(cv, st, W / 2, y + img.height + 6 * u, alpha=a)
    if pessoa is not None:
        cv.alpha_composite(pessoa)
    return cv


@efeito("mural_comentarios", "Comentários de rede social voando para a tela, opcionalmente com fundo preto atrás da pessoa.")
def mural_comentarios(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    if ef.get("fundo_escuro", True):
        a = envelope(t, ef["inicio"], ef["fim"], 0.25, 0.25)
        bg = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        bg.alpha_composite(ctx.pessoa(cv))
        cv = Image.blend(cv, bg, a)
    coms = ef.get("comentarios") or [{"usuario": "fulano", "texto": "Comentário de exemplo"}]
    rnd = random.Random(3)
    posicoes = [(0.3, 0.08), (0.72, 0.15), (0.25, 0.24), (0.7, 0.33), (0.28, 0.42), (0.68, 0.52),
                (0.3, 0.6), (0.72, 0.7)]
    for i, c in enumerate(coms):
        t0 = ef["inicio"] + i * ef.get("intervalo", 0.25)
        e = ease_out((t - t0) / 0.45)
        s = envelope(t, t0, ef["fim"], 0.01, 0.25)
        if e <= 0 or s <= 0:
            continue
        card = _card_comentario(c, u, ctx, ("com", id(ef), i))
        px, py = posicoes[i % len(posicoes)]
        lado = -1 if px < 0.5 else 1
        x = px * W + lado * (1 - e) * W * 0.8
        y = py * H - (t - t0) * 8 * u
        colar(cv, card, x, y, alpha=s, rot=rnd.uniform(-3, 3))
    return cv


def _card_comentario(c, u, ctx, chave):
    if chave in ctx.cache:
        return ctx.cache[chave]
    w = 330 * u
    fu, ft, fs = fonte("sans_bold", 14 * u), fonte("sans", 14 * u), fonte("sans", 11 * u)
    linhas, atual = [], ""
    for p in c.get("texto", "").split():
        teste = (atual + " " + p).strip()
        if ft.getlength(teste) > w - 70 * u and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = teste
    linhas.append(atual)
    h = 40 * u + 19 * u * len(linhas) + 16 * u
    img = retangulo(w, h, 12 * u, (255, 255, 255, 250))
    d = ImageDraw.Draw(img)
    d.ellipse([12 * u, 12 * u, 42 * u, 42 * u], fill=(*cor(c.get("cor_avatar"), "#9AA0A6"), 255))
    d.text((52 * u, 12 * u), c.get("usuario", "usuario"), font=fu, fill=(20, 20, 20))
    for k, ln in enumerate(linhas):
        d.text((52 * u, 32 * u + k * 19 * u), ln, font=ft, fill=(30, 30, 30))
    d.text((52 * u, h - 22 * u), c.get("rodape", "1 min   Responder"), font=fs, fill=(140, 140, 140))
    d.text((w - 26 * u, 18 * u), "♡", font=fonte("sans", 16 * u), fill=(140, 140, 140))
    ctx.cache[chave] = sombra(img, 14, 90, 5)
    return ctx.cache[chave]


@efeito("celular_flutuando", "Celular (mockup) entra flutuando com uma tela/imagem dentro.")
def celular_flutuando(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    ini, fim = ef["inicio"], ef["fim"]
    e_in = ease_back((t - ini) / 0.55, 1.2)
    e_out = ease_in((t - (fim - 0.35)) / 0.35)
    lado = 1 if ef.get("lado", "direita") == "direita" else -1
    chave = ("cel", id(ef))
    if chave not in ctx.cache:
        pw, ph = int(220 * u), int(450 * u)
        corpo = retangulo(pw, ph, 36 * u, (12, 12, 12, 255), (60, 60, 60, 255), 3 * u)
        sw, sh = pw - int(16 * u), ph - int(16 * u)
        if ef.get("midia"):
            tela = cobrir(miniatura(ef["midia"], 1.0, sw, sh), sw, sh)
        else:
            tela = Image.new("RGBA", (sw, sh), (20, 20, 22, 255))
            grad = Image.linear_gradient("L").resize((sw, sh))
            roxo = Image.new("RGBA", (sw, sh), (*cor(ef.get("cor_tela"), "#6B3FD1"), 255))
            roxo.putalpha(grad.point(lambda v: int(v * 0.8)))
            tela.alpha_composite(roxo)
            d = ImageDraw.Draw(tela)
            tit = ef.get("titulo", "Edição Viral")
            ft = fonte("serif", 30 * u)
            d.text(((sw - ft.getlength(tit)) / 2, sh * 0.68), tit, font=ft, fill=(255, 255, 255))
            sub = ef.get("subtitulo", "por Claude")
            fs = fonte("sans", 13 * u)
            d.text(((sw - fs.getlength(sub)) / 2, sh * 0.68 + 42 * u), sub, font=fs, fill=(220, 220, 220))
            d.rounded_rectangle([sw * 0.3, sh * 0.86, sw * 0.7, sh * 0.86 + 26 * u], radius=13 * u,
                                fill=(*COR["verde"], 255))
        tela.putalpha(retangulo(sw, sh, 28 * u, (0, 0, 0, 255)).getchannel("A"))
        corpo.alpha_composite(tela, (int(8 * u), int(8 * u)))
        ImageDraw.Draw(corpo).rounded_rectangle([pw * 0.36, 16 * u, pw * 0.64, 30 * u], radius=7 * u,
                                                fill=(0, 0, 0, 255))
        ctx.cache[chave] = sombra(corpo, 28, 130, 14)
    cel = ctx.cache[chave]
    bob = math.sin((t - ini) * 2.2) * 9 * u
    rot = math.sin((t - ini) * 1.4) * 3 - lado * 4
    x0 = W / 2 + lado * W * ef.get("x", 0.3)
    x = x0 + lado * (1 - e_in) * W * 0.6 + lado * e_out * W * 0.6
    colar(cv, cel, x, ef.get("y", 0.55) * H + bob, ef.get("tamanho", 1.0), rot=rot)
    return cv


@efeito("checklist", "Card escuro 'TUDO QUE VOCÊ PRECISA' com itens sendo marcados um a um.")
def checklist(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    ini, fim = ef["inicio"], ef["fim"]
    itens = ef.get("itens", ["Grava o vídeo", "Manda pro Claude", "Posta"])
    a = envelope(t, ini, fim, 0.35, 0.3)
    passo = ef.get("intervalo", (fim - ini - 0.8) / max(1, len(itens)))
    cw, lh = W * 0.66, 46 * u
    ch = 58 * u + lh * len(itens) + 10 * u
    card = retangulo(cw, ch, 18 * u, (*COR["card"], 215), (255, 255, 255, 30), 1)
    d = ImageDraw.Draw(card)
    fh = fonte("sans_bold", 14 * u)
    feitos = sum(1 for i in range(len(itens)) if t >= ini + 0.6 + (i + 0.5) * passo)
    x = 22 * u
    d.ellipse([x, 26 * u, x + 6 * u, 32 * u], fill=(*COR["amarelo"], 255))
    titulo = ef.get("titulo", "TUDO QUE VOCÊ PRECISA")
    x += 16 * u
    for ch_ in titulo:
        d.text((x, 21 * u), ch_, font=fh, fill=(170, 170, 170))
        x += fh.getlength(ch_) + 2.5 * u
    cont = f"{feitos} de {len(itens)}"
    d.text((cw - 22 * u - fh.getlength(cont), 21 * u), cont, font=fh, fill=(255, 255, 255))
    for i, item in enumerate(itens):
        y = 58 * u + i * lh
        t_ap = ini + 0.4 + i * passo
        t_ok = t_ap + passo * 0.5
        ok = t >= t_ok
        cx_, cy_ = 32 * u, y + lh / 2
        if ok:
            ic = check_icon(int(22 * u), fundo=cor(ef.get("cor_check"), "amarelo"), traco=(20, 20, 20))
            s = ease_back((t - t_ok) / 0.25)
            colar(card, ic, cx_, cy_, max(0.01, s))
        else:
            d.ellipse([cx_ - 10 * u, cy_ - 10 * u, cx_ + 10 * u, cy_ + 10 * u], outline=(110, 110, 110),
                      width=int(2 * u))
        if t >= t_ap:
            alpha = int(255 * ease_out((t - t_ap) / 0.3))
            fnt = fonte("serif", 20 * u)
            col = (130, 130, 130, alpha) if ok and ef.get("riscar", False) else (255, 255, 255, alpha)
            d.text((56 * u, cy_ - 15 * u), item, font=fnt, fill=col)
        else:
            d.rounded_rectangle([56 * u, cy_ - 4 * u, 56 * u + cw * 0.5, cy_ + 4 * u], radius=4 * u,
                                fill=(70, 70, 70, 255))
    colar(cv, sombra(card, 22, 120, 10), W / 2, ef.get("y", 0.6) * H + (1 - ease_out(a)) * 40 * u,
          0.94 + 0.06 * ease_out(a), alpha=a)
    return cv


@efeito("tela_claude", "Janela de chat do Claude: anexa o vídeo, digita o pedido e mostra as etapas concluídas.")
def tela_claude(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    ini, fim = ef["inicio"], ef["fim"]
    a = envelope(t, ini, fim, 0.35, 0.3)
    msg = ef.get("mensagem", "Acabei de gravar esse vídeo. Edita para mim.")
    arquivo = ef.get("arquivo", "meu-video.mp4")
    passos = ef.get("passos", ["Cortei as pausas", "Legenda e efeitos no lugar", "Postado no Instagram"])
    t_arq = ini + 0.35
    t_dig0 = ini + 0.7
    vel = ef.get("velocidade_digitacao", 28)  # caracteres por segundo
    t_dig1 = t_dig0 + len(msg) / vel
    passo = max(0.3, (fim - 0.4 - t_dig1 - 0.3) / max(1, len(passos)))
    ww = W * 0.7
    fm, fsm = fonte("sans", 13 * u), fonte("sans_bold", 13 * u)
    hh = 60 * u
    if t >= t_arq:
        hh += 36 * u
    if t >= t_dig0:
        hh += 40 * u
    visiveis = [i for i in range(len(passos)) if t >= t_dig1 + 0.3 + i * passo]
    hh += 26 * u * len(visiveis) + (10 * u if visiveis else 0)
    hh = max(hh, 130 * u)
    win = retangulo(ww, hh, 16 * u, (31, 31, 30, 245), (255, 255, 255, 25), 1)
    d = ImageDraw.Draw(win)
    win.alpha_composite(asterisco(int(14 * u), (*COR["laranja"], 255)), (int(16 * u), int(14 * u)))
    d.text((38 * u, 13 * u), ef.get("nome", "Claude"), font=fsm, fill=(240, 240, 240))
    y = 48 * u
    if t >= t_arq:
        s = ease_out((t - t_arq) / 0.25)
        cw = fm.getlength(arquivo) + 44 * u
        chip = retangulo(cw, 28 * u, 7 * u, (45, 45, 44, int(255 * s)))
        cd = ImageDraw.Draw(chip)
        cd.rectangle([8 * u, 6 * u, 24 * u, 22 * u], fill=(90, 90, 90, int(255 * s)))
        cd.text((32 * u, 6 * u), arquivo, font=fm, fill=(220, 220, 220, int(255 * s)))
        win.alpha_composite(chip, (int(ww - cw - 16 * u), int(y)))
        y += 36 * u
    if t >= t_dig0:
        n = int(clamp((t - t_dig0) / max(0.01, t_dig1 - t_dig0)) * len(msg))
        txt = msg[:n] + ("|" if t < t_dig1 + 0.4 and int(t * 3) % 2 == 0 else "")
        bw = fm.getlength(msg) + 28 * u
        bolha = retangulo(bw, 30 * u, 9 * u, (46, 46, 45, 255))
        ImageDraw.Draw(bolha).text((14 * u, 7 * u), txt, font=fm, fill=(235, 235, 235))
        win.alpha_composite(bolha, (int(ww - bw - 16 * u), int(y)))
        y += 40 * u
    for i in visiveis:
        ti = t_dig1 + 0.3 + i * passo
        s = ease_out((t - ti) / 0.25)
        ultimo = i == len(passos) - 1 and ef.get("destacar_ultimo", True)
        if ultimo:
            tw = fsm.getlength("✓ " + passos[i]) + 20 * u
            pill = retangulo(tw, 22 * u, 11 * u, (*COR["verde"], int(255 * s)))
            ImageDraw.Draw(pill).text((10 * u, 3 * u), "✓ " + passos[i], font=fsm, fill=(10, 40, 10))
            win.alpha_composite(pill, (int(16 * u), int(y)))
        else:
            win.alpha_composite(check_icon(int(16 * u)), (int(16 * u), int(y + 3 * u)))
            d.text((40 * u, y + 2 * u), passos[i], font=fm, fill=(225, 225, 225, int(255 * s)))
        y += 26 * u
    colar(cv, sombra(win, 24, 140, 10), W / 2, ef.get("y", 0.04) * H + hh / 2 + 24,
          0.92 + 0.08 * ease_back(a), alpha=a)
    return cv


@efeito("legenda", "Legenda palavra por palavra, em serifa, no peito da pessoa.")
def legenda(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    chave = ("leg", id(ef))
    if chave not in ctx.cache:
        if ef.get("palavras"):
            pal = [(p[0], float(p[1])) for p in ef["palavras"]]
        else:
            ws = ef.get("texto", "").split()
            pesos = [len(w) + 2 for w in ws]
            tot = sum(pesos) or 1
            acc, pal = ef["inicio"], []
            for w, pz in zip(ws, pesos):
                pal.append((w, acc))
                acc += (ef["fim"] - ef["inicio"]) * pz / tot
        ctx.cache[chave] = pal
    pal = ctx.cache[chave]
    atual = None
    for i, (w, ti) in enumerate(pal):
        tf = pal[i + 1][1] if i + 1 < len(pal) else ef["fim"]
        if ti <= t < tf:
            atual = (w, ti, i)
            break
    if not atual:
        return cv
    w, ti, i = atual
    destaques = set(x.lower() for x in ef.get("destaques", []))
    limpa = w.lower().strip(".,!?;:")
    col = COR["amarelo"] if limpa in destaques else cor(ef.get("cor"))
    img = texto_img(w, fonte("serif", ef.get("tamanho", 34) * u), (*col, 255))
    s = 0.86 + 0.14 * ease_back((t - ti) / 0.12)
    colar(cv, img, W / 2, ef.get("y", 0.475) * H, s)
    return cv


@efeito("titulo_lista", "Título grande em serifa ('11 efeitos que o Claude faz') com lista numerada e item ativo em amarelo.")
def titulo_lista(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    a = envelope(t, ef["inicio"], ef["fim"], 0.35, 0.25)
    if a <= 0:
        return cv
    linhas = ef.get("titulo", ["11 efeitos", "que o Claude faz"])
    destaque = ef.get("destaque", "11")
    y = ef.get("y", 0.045) * H
    fnt = fonte("serif", ef.get("tamanho", 54) * u)
    for k, ln in enumerate(linhas):
        partes = ln.split(" ")
        larg = sum(fnt.getlength(p + " ") for p in partes) - fnt.getlength(" ")
        x = W / 2 - larg / 2
        lay = camada(int(larg + 40), int(fnt.size * 1.4))
        d = ImageDraw.Draw(lay)
        xx = 4
        for p in partes:
            d.text((xx, 0), p, font=fnt, fill=(*(COR["amarelo"] if p == destaque else COR["branco"]), 255))
            xx += fnt.getlength(p + " ")
        lay = sombra(lay, 10, 140, 2)
        colar(cv, lay, x + lay.width / 2 - 28, y + k * fnt.size * 0.92 + lay.height / 2 - 28
              + (1 - ease_out(a)) * 20 * u, alpha=a)
    itens = ef.get("itens") or []
    if itens:
        ativo = ef.get("ativo")
        if isinstance(ativo, list):  # [[indice, tempo], ...] → muda o destaque ao longo do tempo
            cur = None
            for idx, tt in ativo:
                if t >= tt:
                    cur = idx
            ativo = cur
        meio = (len(itens) + 1) // 2
        cols = [itens[:meio], itens[meio:]]
        fi, fn = fonte("serif", 15.5 * u), fonte("sans", 9 * u)
        y0 = y + len(linhas) * fnt.size * 0.92 + 18 * u
        for c, col in enumerate(cols):
            if not col:
                continue
            cw = max(fi.getlength(s) for s in col) + 48 * u
            chh = len(col) * 22 * u + 16 * u
            card = retangulo(cw, chh, 8 * u, (20, 20, 20, 165))
            d = ImageDraw.Draw(card)
            for k, s in enumerate(col):
                idx = k + (0 if c == 0 else meio)
                on = ativo is not None and idx == ativo
                d.text((10 * u, 12 * u + k * 22 * u), f"{idx + 1:02d}", font=fn,
                       fill=(*(COR["amarelo"] if on else (140, 140, 140)), 255))
                d.text((28 * u, 6 * u + k * 22 * u), s, font=fi,
                       fill=(*(COR["amarelo"] if on else (235, 235, 235)), 255))
            xpos = W * 0.04 + cw / 2 if c == 0 else W * 0.96 - cw / 2
            colar(cv, card, xpos, y0 + chh / 2, alpha=a)
    return cv


@efeito("contador", "Card com ícone e número grande que conta (ex.: '0 cliques no mouse').")
def contador(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    a = envelope(t, ef["inicio"], ef["fim"], 0.3, 0.3)
    de, ate = ef.get("de", 0), ef.get("ate", 0)
    v = de + (ate - de) * ease_out((t - ef["inicio"] - 0.2) / ef.get("duracao_contagem", 1.0))
    num = f"{int(round(v))}{ef.get('sufixo', '')}"
    fnum, flab = fonte("serif", 38 * u), fonte("serif", 14 * u)
    rot = ef.get("rotulo", "cliques no mouse")
    cw = max(fnum.getlength(num), flab.getlength(rot)) + 96 * u
    card = retangulo(cw, 76 * u, 10 * u, (*COR["card"], 230))
    d = ImageDraw.Draw(card)
    d.ellipse([16 * u, 18 * u, 56 * u, 58 * u], outline=(200, 200, 200), width=int(2 * u))
    d.rounded_rectangle([29 * u, 26 * u, 43 * u, 50 * u], radius=7 * u, outline=(220, 220, 220), width=int(2 * u))
    d.line([(36 * u, 28 * u), (36 * u, 34 * u)], fill=(220, 220, 220), width=int(2 * u))
    d.text((72 * u, 4 * u), num, font=fnum, fill=(*COR["amarelo"], 255))
    d.text((72 * u, 50 * u), rot, font=flab, fill=(235, 235, 235))
    colar(cv, sombra(card, 16, 110, 6), W / 2, ef.get("y", 0.2) * H, 0.9 + 0.1 * ease_back(a), alpha=a)
    return cv


@efeito("logo_pop", "Ícone redondo (faísca do Claude por padrão) que aparece com 'pop' e um rótulo embaixo.")
def logo_pop(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    a = envelope(t, ef["inicio"], ef["fim"], 0.01, 0.25)
    s = ease_back((t - ef["inicio"]) / 0.35, 2.4)
    tam = int(64 * u)
    if ef.get("imagem"):
        ic = Image.open(ef["imagem"]).convert("RGBA").resize((tam, tam), Image.LANCZOS)
    else:
        ic = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
        ImageDraw.Draw(ic).ellipse([0, 0, tam - 1, tam - 1], fill=(*cor(ef.get("cor"), "laranja"), 255))
        st = asterisco(int(tam * 0.62))
        ic.alpha_composite(st, ((tam - st.width) // 2, (tam - st.height) // 2))
    x, y = ef.get("x", 0.5) * W, ef.get("y", 0.17) * H
    colar(cv, sombra(ic, 12, 100, 4), x, y, max(0.01, s), alpha=a)
    if ef.get("rotulo", "Claude"):
        tx = texto_img(ef.get("rotulo", "Claude"), fonte("serif", 16 * u), (255, 255, 255, 255))
        colar(cv, tx, x, y + tam * 0.75, alpha=a * clamp((t - ef["inicio"] - 0.15) / 0.2))
    return cv


@efeito("dm_link", "Notificação de DM ('Aqui está o seu link') + campo de mensagem com palavra-chave.")
def dm_link(cv, t, ef, ctx):
    W, H, u = cv.size[0], cv.size[1], ctx.u
    ini, fim = ef["inicio"], ef["fim"]
    a = envelope(t, ini, fim, 0.3, 0.3)
    t_not = ini + ef.get("atraso_notificacao", 0.6)
    bw = W * 0.74
    campo = retangulo(bw, 34 * u, 17 * u, (255, 255, 255, 255))
    d = ImageDraw.Draw(campo)
    pal = ef.get("palavra", "editar")
    n = int(clamp((t - ini - 0.2) / 0.4) * len(pal))
    d.text((14 * u, 7 * u), pal[:n], font=fonte("sans_bold", 15 * u), fill=(20, 20, 20))
    d.ellipse([bw - 30 * u, 6 * u, bw - 8 * u, 28 * u], fill=(20, 20, 20))
    d.line([(bw - 19 * u, 22 * u), (bw - 19 * u, 12 * u)], fill=(255, 255, 255), width=int(2 * u))
    d.line([(bw - 24 * u, 16 * u), (bw - 19 * u, 11 * u), (bw - 14 * u, 16 * u)], fill=(255, 255, 255),
           width=int(2 * u))
    y = ef.get("y", 0.86) * H
    if t >= t_not:
        s = ease_out((t - t_not) / 0.3)
        nb = retangulo(bw + 12 * u, 84 * u, 16 * u, (20, 20, 20, 235))
        nd = ImageDraw.Draw(nb)
        nd.ellipse([12 * u, 10 * u, 36 * u, 34 * u], fill=(*COR["laranja"], 255))
        nd.text((44 * u, 14 * u), ef.get("remetente", "voce · direct"), font=fonte("sans", 11 * u), fill=(160, 160, 160))
        msg = ef.get("mensagem", "Aqui está o seu link")
        fb = fonte("sans_bold", 14 * u)
        nd.text((bw - fb.getlength(msg) - 12 * u, 12 * u), msg, font=fb, fill=(255, 255, 255))
        colar(cv, sombra(nb, 18, 110, 6), W / 2, y - 22 * u + (1 - s) * 30 * u, alpha=a * s)
    colar(cv, sombra(campo, 12, 90, 4), W / 2, y + (1 - ease_out(a)) * 40 * u, alpha=a)
    return cv


# ---------------------------------------------------------------- render

def aplicar(frame_np, t, plano, ctx):
    ctx.frame_np, ctx.ts, ctx.mask = frame_np, int(t * 1000), None
    cv = Image.fromarray(frame_np, "RGB").convert("RGBA")
    for ef in plano["efeitos"]:
        if ef["inicio"] <= t <= ef["fim"]:
            cv = EFEITOS[ef["tipo"]](cv, t, ef, ctx)
    return cv.convert("RGB")


def carregar(path):
    with open(path, encoding="utf-8") as f:
        plano = json.load(f)
    base = os.path.dirname(os.path.abspath(path))
    plano["entrada"] = os.path.join(base, plano["entrada"])
    plano["saida"] = os.path.join(base, plano.get("saida", "editado.mp4"))
    for ef in plano["efeitos"]:
        if ef["tipo"] not in EFEITOS:
            sys.exit(f"Efeito desconhecido: {ef['tipo']}. Use: {', '.join(EFEITOS)}")
        for k in ("midia", "imagem"):
            if isinstance(ef.get(k), str):
                ef[k] = os.path.join(base, ef[k])
        if isinstance(ef.get("fundo"), str) and os.path.exists(os.path.join(base, ef["fundo"])):
            ef["fundo"] = os.path.join(base, ef["fundo"])
        if ef.get("midias"):
            ef["midias"] = [os.path.join(base, m) for m in ef["midias"]]
    return plano


def render(plano, inicio=None, fim=None):
    W, H, fps, dur = sonda(plano["entrada"])
    ctx = Contexto(plano, W, H, fps)
    ss = ["-ss", str(inicio)] if inicio else []
    tt = ["-t", str((fim or dur) - (inicio or 0))] if (fim or inicio) else []
    leitor = subprocess.Popen(["ffmpeg", "-v", "error", *ss, "-i", plano["entrada"], *tt,
                               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    escritor = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(fps), "-i", "-", *ss, "-i", plano["entrada"], *tt,
        "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", plano["saida"]],
        stdin=subprocess.PIPE)
    n, tam = 0, W * H * 3
    total = int(((fim or dur) - (inicio or 0)) * fps)
    while True:
        raw = leitor.stdout.read(tam)
        if len(raw) < tam:
            break
        t = (inicio or 0) + n / fps
        frame = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
        escritor.stdin.write(aplicar(frame, t, plano, ctx).tobytes())
        n += 1
        if n % int(fps * 2) == 0:
            print(f"  {n}/{total} quadros ({t:.1f}s)", flush=True)
    escritor.stdin.close()
    escritor.wait()
    print("Pronto:", plano["saida"])


def preview(plano, t, saida=None):
    W, H, fps, _ = sonda(plano["entrada"])
    ctx = Contexto(plano, W, H, fps)
    # aquece a máscara (o segmentador suaviza entre quadros)
    for k in (3, 2, 1, 0):
        tk = max(0.0, t - k / fps)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(tk), "-i", plano["entrada"], "-frames:v", "1",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        frame = np.frombuffer(raw[:W * H * 3], np.uint8).reshape(H, W, 3)
        img = aplicar(frame, tk, plano, ctx)
    saida = saida or os.path.splitext(plano["saida"])[0] + f"_preview_{t:.2f}.png"
    img.save(saida)
    print("Preview:", saida)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("render", "preview", "efeitos"):
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "efeitos":
        for k, fn in EFEITOS.items():
            print(f"{k:20s} {fn.descricao}")
        sys.exit(0)
    plano = carregar(sys.argv[2])
    if sys.argv[1] == "preview":
        preview(plano, float(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        args = sys.argv[3:]
        ini = float(args[0]) if len(args) > 0 else None
        fim = float(args[1]) if len(args) > 1 else None
        render(plano, ini, fim)
