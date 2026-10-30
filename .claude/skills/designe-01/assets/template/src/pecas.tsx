// Peças do designe-01. Não mude cores/fontes aqui: elas vêm de theme.ts.
import React from "react";
import { Easing, interpolate, spring, useCurrentFrame } from "remotion";
import { C, SANS, SERIF } from "./theme";

export const FPS = 30;
export const f = (s: number) => Math.round(s * FPS);

// ---------- layouts da "janela" do vídeo (canvas 1080x1920) ----------
export type Box = { x: number; y: number; w: number; h: number; r: number; ring: number; zoom: number };
export const FULL = (zoom = 1): Box => ({ x: 0, y: 0, w: 1080, h: 1920, r: 0, ring: 0, zoom });
export const CARD: Box = { x: 130, y: 600, w: 820, h: 1000, r: 64, ring: 1, zoom: 1.05 };
export const CIRCLE: Box = { x: 790, y: 130, w: 220, h: 220, r: 110, ring: 1, zoom: 1.3 };
export const END: Box = { x: 340, y: 520, w: 400, h: 400, r: 200, ring: 1, zoom: 1.3 };

export type BadgeT = { s: number; e: number; kicker: string; word: string };
export type Scene = { s: number; e: number; box: Box; overlay?: React.FC<{ t0: number }>; hideCaps?: boolean; badge?: BadgeT[] };

export const useEnter = (t0: number, delay = 0) => {
  const frame = useCurrentFrame();
  return spring({ frame: frame - f(t0) - delay, fps: FPS, config: { damping: 16, mass: 0.7 } });
};

// ---------- tipografia ----------
export const Chapter: React.FC<{ t0: number; n: string; label: string }> = ({ t0, n, label }) => {
  const p = useEnter(t0);
  return (
    <div style={{ position: "absolute", left: 80, top: 150, display: "flex", alignItems: "baseline", gap: 16, opacity: p, transform: `translateX(${(1 - p) * -40}px)` }}>
      <span style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 700, fontSize: 96, color: C.magenta }}>{n}</span>
      <span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 26, letterSpacing: 6, color: C.dim, textTransform: "uppercase" }}>{label}</span>
    </div>
  );
};

export const Headline: React.FC<{ t0: number; kicker?: string; big: string; top?: number; size?: number; delay?: number }> = ({ t0, kicker, big, top = 300, size = 110, delay = 4 }) => {
  const a = useEnter(t0, delay);
  const b = useEnter(t0, delay + 6);
  return (
    <div style={{ position: "absolute", left: 70, right: 70, top, textAlign: "center" }}>
      {kicker && <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 46, color: C.cream, opacity: a, transform: `translateY(${(1 - a) * 30}px)` }}>{kicker}</div>}
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 700, fontSize: size, lineHeight: 1.02, color: C.pink, marginTop: 10, opacity: b, transform: `translateY(${(1 - b) * 40}px) scale(${0.9 + b * 0.1})` }}>{big}</div>
    </div>
  );
};

export const Pill: React.FC<{ children: React.ReactNode; hot?: boolean; style?: React.CSSProperties }> = ({ children, hot, style }) => (
  <div style={{
    position: "absolute", padding: "18px 34px", borderRadius: 999, fontFamily: SANS, fontWeight: 800, fontSize: 40, whiteSpace: "nowrap",
    color: hot ? "#fff" : C.cream, background: hot ? C.magenta : "rgba(255,255,255,0.07)",
    border: `2px solid ${hot ? C.magenta : "rgba(255,179,214,0.35)"}`, boxShadow: hot ? "0 10px 40px rgba(255,46,138,0.45)" : "none", ...style,
  }}>{children}</div>
);

// ---------- overlays prontos (fábricas: recebem textos, devolvem a cena) ----------
// Regra de layout: com CIRCLE, headline em top >= 400 (a bolinha ocupa 130–350 à direita).
// Com CARD, headline em top 250–430 (o card começa em 600).

type Ch = [string, string] | null;

/** Título: capítulo opcional + kicker sem serifa + frase grande serifada. Use com CARD. */
export const Title = (chapter: Ch, kicker: string, big: string, size?: number): React.FC<{ t0: number }> => ({ t0 }) => (
  <>
    {chapter && <Chapter t0={t0} n={chapter[0]} label={chapter[1]} />}
    <Headline t0={t0} kicker={kicker} big={big} top={chapter ? 290 : 250} size={size} />
  </>
);

/** Parede de etiquetas que pipocam e sobem devagar (até ~10). Bom para "excesso", "caos", "lista de coisas". Use com CIRCLE. */
export const Feed = (chapter: Ch, kicker: string, big: string, items: string[], hotIdx: number[] = [0]): React.FC<{ t0: number }> => ({ t0 }) => {
  const frame = useCurrentFrame();
  return (
    <>
      {chapter && <Chapter t0={t0} n={chapter[0]} label={chapter[1]} />}
      <Headline t0={t0} kicker={kicker} big={big} top={410} />
      {items.slice(0, 10).map((txt, i) => {
        const p = spring({ frame: frame - f(t0) - 10 - i * 5, fps: FPS, config: { damping: 12 } });
        const col = i % 2, row = Math.floor(i / 2);
        const drift = (frame - f(t0)) * (0.25 + (i % 3) * 0.1);
        return (
          <Pill key={txt} hot={hotIdx.includes(i)} style={{
            left: col ? 560 + (row % 2) * 60 : 90 + (row % 2) * 70, top: 760 + row * 120 - drift,
            transform: `scale(${p}) rotate(${(i % 3 - 1) * 4}deg)`, opacity: p,
          }}>{txt}</Pill>
        );
      })}
    </>
  );
};

/** Duas barras lado a lado + selo. Para comparação "A vs B". equal=true deixa do mesmo tamanho. Use com CIRCLE. */
export const Compare = (kicker: string, big: string, a: string, b: string, seal: string, equal = true): React.FC<{ t0: number }> => ({ t0 }) => {
  const frame = useCurrentFrame();
  const grow = (d: number) => interpolate(frame - f(t0) - d, [0, 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const bar = (x: number, label: string, d: number, hot: boolean, h: number) => (
    <div style={{ position: "absolute", left: x, bottom: 560, width: 260, textAlign: "center" }}>
      <div style={{ height: h * grow(d), borderRadius: 32, background: hot ? `linear-gradient(${C.magenta}, #B0125E)` : "rgba(255,179,214,0.25)", border: `2px solid ${C.magenta}` }} />
      <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 40, color: C.cream, marginTop: 24 }}>{label}</div>
    </div>
  );
  const s = useEnter(t0, 40);
  return (
    <>
      <Headline t0={t0} kicker={kicker} big={big} top={410} />
      {bar(220, a, 10, true, 520)}
      {bar(600, b, 18, false, equal ? 520 : 260)}
      <Pill hot style={{ left: 330, top: 720, transform: `scale(${s})`, opacity: s }}>{seal}</Pill>
    </>
  );
};

const Dot: React.FC<{ t0: number; d: number; left?: number; right?: number; bottom: number; label: string; hot?: boolean }> = ({ t0, d, left, right, bottom, label, hot }) => {
  const p = useEnter(t0, d);
  return (
    <div style={{ position: "absolute", left, right, bottom, display: "flex", flexDirection: "column", alignItems: hot ? "flex-end" : "flex-start", opacity: p, transform: `translateY(${(1 - p) * 30}px)` }}>
      <span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 34, color: hot ? C.magenta : C.cream, whiteSpace: "nowrap" }}>{label}</span>
      <div style={{ width: 44, height: 44, borderRadius: 22, background: hot ? C.magenta : C.cream, marginTop: 10, boxShadow: hot ? "0 0 30px rgba(255,46,138,0.8)" : "none" }} />
    </div>
  );
};

/** Escada de 5 degraus com um ponto embaixo (low) e um no topo (high). crowd=true põe vários pontos no 2º degrau. Use com CIRCLE. */
export const Stairs = (chapter: Ch, kicker: string, big: string, low: string, high: string, crowd = false, sub?: string): React.FC<{ t0: number }> => ({ t0 }) => {
  const frame = useCurrentFrame();
  return (
    <>
      {chapter && <Chapter t0={t0} n={chapter[0]} label={chapter[1]} />}
      <Headline t0={t0} kicker={kicker} big={big} top={400} size={sub ? 110 : 92} />
      {sub && <Headline t0={t0} big={sub} top={610} size={64} delay={60} />}
      <div style={{ position: "absolute", left: 90, top: 720, width: 900, height: 720 }}>
        {Array.from({ length: 5 }).map((_, i) => {
          const p = spring({ frame: frame - f(t0) - 8 - i * 4, fps: FPS, config: { damping: 15 } });
          return (
            <div key={i} style={{
              position: "absolute", left: i * 180, bottom: 0, width: 172, height: (120 + i * 120) * p, borderRadius: "22px 22px 0 0",
              background: i === 4 ? `linear-gradient(${C.magenta}, #6B0A3A)` : `rgba(255,179,214,${0.1 + i * 0.05})`, borderTop: `4px solid ${C.magenta}`,
            }} />
          );
        })}
        {crowd && Array.from({ length: 10 }).map((_, i) => {
          const p = spring({ frame: frame - f(t0) - 40 - i * 2, fps: FPS, config: { damping: 10 } });
          return <div key={i} style={{ position: "absolute", left: 190 + (i % 5) * 32, bottom: 254 + Math.floor(i / 5) * 36, width: 26, height: 26, borderRadius: 13, background: C.cream, transform: `scale(${p})` }} />;
        })}
        <Dot t0={t0} d={30} left={crowd ? 170 : 60} bottom={crowd ? 310 : 140} label={low} />
        <Dot t0={t0} d={44} right={0} bottom={620} label={high} hot />
      </div>
    </>
  );
};

/** Frase gigante + linhas sublinhadas que entram nos tempos exatos da fala. Para repetições/listas faladas ("ainda dá tempo de… de… de…"). Use com CIRCLE e hideCaps. */
export const Stack = (chapter: Ch, kicker: string, big: string, lines: { s: number; t: string }[]): React.FC<{ t0: number }> => ({ t0 }) => {
  const frame = useCurrentFrame();
  return (
    <>
      {chapter && <Chapter t0={t0} n={chapter[0]} label={chapter[1]} />}
      <Headline t0={t0} kicker={kicker} big={big} top={420} size={190} />
      {lines.slice(0, 4).map((l, i) => {
        const p = spring({ frame: frame - f(l.s), fps: FPS, config: { damping: 14 } });
        return (
          <div key={l.t} style={{ position: "absolute", left: 0, right: 0, top: 900 + i * 130, textAlign: "center", opacity: p, transform: `translateY(${(1 - p) * 40}px)` }}>
            <span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 58, color: C.cream, borderBottom: `6px solid ${C.magenta}`, paddingBottom: 6 }}>{l.t}</span>
          </div>
        );
      })}
    </>
  );
};

/** Grade de até 4 chips que entram nos tempos da fala + 1 chip destaque. Use com CIRCLE. */
export const Chips = (kicker: string, big: string, chips: { s: number; t: string }[], hot: string): React.FC<{ t0: number }> => ({ t0 }) => {
  const frame = useCurrentFrame();
  const h = useEnter(t0, 6);
  return (
    <>
      <Headline t0={t0} kicker={kicker} big={big} top={410} />
      {chips.slice(0, 4).map((x, i) => {
        const p = spring({ frame: frame - f(x.s), fps: FPS, config: { damping: 12 } });
        return <Pill key={x.t} style={{ left: i % 2 ? 580 : 140, top: 720 + Math.floor(i / 2) * 140, transform: `scale(${p})`, opacity: p }}>{x.t}</Pill>;
      })}
      <Pill hot style={{ left: 300, top: 1010, fontSize: 52, transform: `scale(${h})`, opacity: h }}>{hot}</Pill>
    </>
  );
};

/** Título + tarja magenta que entra num tempo exato (o "soco" final de uma ideia). Use com CARD. */
export const Punch = (kicker: string, big: string, punch: string, punchAt: number): React.FC<{ t0: number }> => ({ t0 }) => {
  const frame = useCurrentFrame();
  const late = spring({ frame: frame - f(punchAt), fps: FPS, config: { damping: 12 } });
  return (
    <>
      <Headline t0={t0} kicker={kicker} big={big} top={190} size={96} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 500, textAlign: "center", opacity: late, transform: `scale(${0.8 + late * 0.2})` }}>
        <span style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 700, fontSize: 64, color: C.cream, background: C.magenta, padding: "4px 28px", borderRadius: 18 }}>{punch}</span>
      </div>
    </>
  );
};

/** Cartão final de CTA (vídeo congelado numa bolinha no centro). Use com END e hideCaps. */
export const End = (kicker: string, big: string, sub?: string): React.FC<{ t0: number }> => ({ t0 }) => (
  <>
    <Headline t0={t0} kicker={kicker} big={big} top={1010} size={130} />
    {sub && <Headline t0={t0} big={sub} top={1330} size={46} delay={14} />}
  </>
);
