import React from "react";
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COR, FONTE, SEGS, f } from "./base";

/** Entrada com "pop" de escala (spring) a partir do frame `de`. */
export const usePop = (de: number, damping = 12) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - de, fps, config: { damping, stiffness: 180, mass: 0.7 } });
};

export const Pop: React.FC<{ de: number; children: React.ReactNode; style?: React.CSSProperties; dy?: number }> = ({ de, children, style, dy = 30 }) => {
  const s = usePop(de);
  return (
    <div style={{ transform: `translateY(${(1 - s) * dy}px) scale(${0.4 + 0.6 * s})`, opacity: Math.min(1, s * 1.5), ...style }}>
      {children}
    </div>
  );
};

/** Cartão escuro translúcido (glassmorphism). */
export const Vidro: React.FC<{ children: React.ReactNode; style?: React.CSSProperties; de?: number }> = ({ children, style, de = 0 }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - de, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <div
      style={{
        background: COR.vidro,
        backdropFilter: "blur(18px)",
        border: `1.5px solid ${COR.borda}`,
        borderRadius: 24,
        padding: "34px 44px",
        boxShadow: "0 30px 80px rgba(0,0,0,0.55)",
        opacity: p,
        transform: `translateY(${(1 - p) * 40}px) scale(${0.94 + 0.06 * p})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Título em caixa alta; trechos entre *asteriscos* ficam dourados. */
export const Titulo: React.FC<{ texto: string; size?: number; de?: number; style?: React.CSSProperties; cor?: string }> = ({ texto, size = 96, de = 0, style, cor = COR.branco }) => {
  const frame = useCurrentFrame();
  const partes = texto.split(/(\*[^*]+\*)/g).filter(Boolean);
  let idx = 0;
  return (
    <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: size, lineHeight: 1.05, textTransform: "uppercase", color: cor, letterSpacing: -1, textShadow: "0 6px 24px rgba(0,0,0,0.8)", ...style }}>
      {partes.map((p, i) => {
        const ouro = p.startsWith("*");
        const palavras = p.replace(/\*/g, "").split(/(\s+)/);
        return (
          <span key={i} style={{ color: ouro ? COR.ouro : undefined }}>
            {palavras.map((w, j) => {
              if (/^\s+$/.test(w)) return w;
              const k = idx++;
              const s = interpolate(frame - de - k * 3, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.back(2)) });
              return (
                <span key={j} style={{ display: "inline-block", opacity: s, transform: `translateY(${(1 - s) * 40}px)` }}>
                  {w}
                </span>
              );
            })}
          </span>
        );
      })}
    </div>
  );
};

export const Rotulo: React.FC<{ children: React.ReactNode; size?: number; cor?: string; style?: React.CSSProperties }> = ({ children, size = 30, cor = COR.cinza, style }) => (
  <div style={{ fontFamily: FONTE, fontWeight: 800, fontSize: size, color: cor, textTransform: "uppercase", letterSpacing: 2, ...style }}>{children}</div>
);

/** Fade de entrada e saída de uma cena (durInFrames = duração da Sequence). */
export const Cena: React.FC<{ dur: number; children: React.ReactNode; fadeIn?: number; fadeOut?: number }> = ({ dur, children, fadeIn = 6, fadeOut = 8 }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, fadeIn, dur - fadeOut, dur], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <div style={{ position: "absolute", inset: 0, opacity: o }}>{children}</div>;
};

// ---------------- Legendas dinâmicas ----------------
const DESTAQUES = /(\d|R\$|cashback|CBS|CPF|Cadastro|Único|derrama|quinto|automático|abril|janeiro|desafio|suficiente|menos)/i;

const quebrar = (texto: string) => {
  const palavras = texto.split(/\s+/);
  const blocos: string[][] = [];
  let atual: string[] = [];
  palavras.forEach((w, i) => {
    atual.push(w);
    const fimFrase = /[.,:?!;]$/.test(w);
    const resto = palavras.length - i - 1;
    if (atual.length >= 5 || (atual.length >= 3 && fimFrase) || (atual.length >= 4 && resto !== 1)) {
      blocos.push(atual);
      atual = [];
    }
  });
  if (atual.length) {
    if (atual.length === 1 && blocos.length) blocos[blocos.length - 1].push(...atual);
    else blocos.push(atual);
  }
  return blocos;
};

export const Legendas: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const s = SEGS.find((x) => t >= x.start && t < x.start + x.duration + 0.3);
  if (!s) return null;
  const blocos = quebrar(s.text);
  const pesos = blocos.map((b) => b.join(" ").length + 4);
  const soma = pesos.reduce((a, b) => a + b, 0);
  let acc = s.start;
  let ativo = blocos.length - 1;
  let iniBloco = s.start;
  for (let i = 0; i < blocos.length; i++) {
    const d = (pesos[i] / soma) * s.duration;
    if (t < acc + d) {
      ativo = i;
      iniBloco = acc;
      break;
    }
    acc += d;
    iniBloco = acc;
  }
  const local = frame - f(iniBloco);
  const p = interpolate(local, [0, 5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <div style={{ position: "absolute", left: 50, right: 50, bottom: 400, display: "flex", justifyContent: "center", pointerEvents: "none" }}>
      <div
        style={{
          fontFamily: FONTE,
          fontWeight: 800,
          fontSize: 60,
          lineHeight: 1.15,
          color: COR.branco,
          textAlign: "center",
          maxWidth: 960,
          textShadow: "0 3px 3px rgba(0,0,0,1), 0 6px 20px rgba(0,0,0,0.9)",
          opacity: p,
          transform: `translateY(${(1 - p) * 14}px) scale(${0.96 + 0.04 * p})`,
        }}
      >
        {blocos[ativo].map((w, i) => (
          <span key={i} style={{ color: DESTAQUES.test(w) ? COR.ouro : undefined }}>
            {w}{" "}
          </span>
        ))}
      </div>
    </div>
  );
};

/** Vinheta escura nas bordas. */
export const Vinheta: React.FC<{ forca?: number }> = ({ forca = 0.85 }) => (
  <div style={{ position: "absolute", inset: 0, background: `radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,${forca}) 100%)`, pointerEvents: "none" }} />
);
