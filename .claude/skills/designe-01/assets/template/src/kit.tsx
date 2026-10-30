// Motor do designe-01: janela do vídeo que se transforma, legendas e selos. Não precisa editar por vídeo.
import React from "react";
import { AbsoluteFill, Freeze, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import captions from "./captions.json";
import { VIDEO_SECONDS, END_SECONDS } from "./config";
import { BadgeT, Box, CARD, CIRCLE, FPS, f } from "./pecas";
import { SCENES } from "./roteiro";
import { C, SANS, SERIF } from "./theme";

const VIDEO_FRAMES = Math.floor(VIDEO_SECONDS * FPS);
export const TOTAL_FRAMES = VIDEO_FRAMES + Math.round(END_SECONDS * FPS);

const lerpBox = (a: Box, b: Box, t: number): Box => ({
  x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t, w: a.w + (b.w - a.w) * t, h: a.h + (b.h - a.h) * t,
  r: a.r + (b.r - a.r) * t, ring: a.ring + (b.ring - a.ring) * t, zoom: a.zoom + (b.zoom - a.zoom) * t,
});

type Cap = { s: number; e: number; w: { t: string; s: number; k: boolean }[] };
const Captions: React.FC<{ y: number }> = ({ y }) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const cap = (captions as Cap[]).find((c) => t >= c.s && t < c.e);
  if (!cap) return null;
  const p = spring({ frame: frame - f(cap.s), fps: FPS, config: { damping: 14, mass: 0.5 } });
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: y, display: "flex", flexWrap: "wrap", justifyContent: "center", alignItems: "baseline", gap: "0 22px", transform: `scale(${0.85 + p * 0.15})`, opacity: p }}>
      {cap.w.map((w, i) => (
        <span key={i} style={w.k
          ? { fontFamily: SERIF, fontStyle: "italic", fontWeight: 700, fontSize: 104, color: C.pink, textTransform: "uppercase", textShadow: "0 6px 30px rgba(0,0,0,0.6)" }
          : { fontFamily: SANS, fontWeight: 800, fontSize: 76, color: C.cream, opacity: t >= w.s - 0.05 ? 1 : 0.45, textShadow: "0 4px 24px rgba(0,0,0,0.7)" }}>
          {w.t}
        </span>
      ))}
    </div>
  );
};

const Badge: React.FC<BadgeT> = ({ s, e, kicker, word }) => {
  const frame = useCurrentFrame();
  if (frame < f(s) || frame > f(e)) return null;
  const p = spring({ frame: frame - f(s), fps: FPS, config: { damping: 13 } });
  const out = interpolate(frame, [f(e) - 6, f(e)], [1, 0], { extrapolateLeft: "clamp" });
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 210, display: "flex", justifyContent: "center", opacity: p * out, transform: `translateY(${(1 - p) * -40}px)` }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 18, padding: "18px 44px", borderRadius: 999, background: "rgba(18,6,26,0.78)", border: `2px solid ${C.magenta}` }}>
        {kicker && <span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 44, color: C.cream }}>{kicker}</span>}
        <span style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 700, fontSize: 64, color: C.magenta }}>{word}</span>
      </div>
    </div>
  );
};

export const Reel: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const t = frame / FPS;
  const found = SCENES.findIndex((sc) => t >= sc.s && t < sc.e);
  const idx = found === -1 ? SCENES.length - 1 : found;
  const scene = SCENES[idx];
  const prev = idx > 0 ? SCENES[idx - 1].box : scene.box;
  const sameKind = prev.w === 1080 && scene.box.w === 1080; // tela cheia -> tela cheia = corte seco com zoom
  const k = sameKind ? 1 : spring({ frame: frame - f(scene.s), fps: FPS, config: { damping: 18, mass: 0.8 } });
  const box = lerpBox(prev, scene.box, Math.min(k, 1));
  const Overlay = scene.overlay;
  const overlayOut = frame >= durationInFrames - 1 ? 1 : interpolate(frame, [f(scene.e) - 6, f(scene.e)], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const isFull = scene.box.w === 1080;
  const capY = isFull ? 1360 : scene.box === CIRCLE ? 1560 : scene.box === CARD ? 1650 : 1560;

  const video = <OffthreadVideo src={staticFile("base.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 35%" }} />;

  return (
    <AbsoluteFill style={{ background: `radial-gradient(120% 70% at 20% 10%, ${C.bg2} 0%, ${C.bg1} 60%)` }}>
      <div style={{ position: "absolute", width: 900, height: 900, left: 400, top: 1100, borderRadius: 450, background: "radial-gradient(circle, rgba(255,46,138,0.22), transparent 70%)" }} />
      <div style={{
        position: "absolute", left: box.x, top: box.y, width: box.w, height: box.h, borderRadius: box.r, overflow: "hidden",
        boxShadow: box.ring > 0.01 ? `0 0 0 ${6 * box.ring}px ${C.magenta}, 0 30px 80px rgba(0,0,0,0.5)` : "none",
      }}>
        <div style={{ width: "100%", height: "100%", transform: `scale(${box.zoom})`, transformOrigin: "50% 35%" }}>
          {frame < VIDEO_FRAMES ? video : <Freeze frame={VIDEO_FRAMES - 2}>{video}</Freeze>}
        </div>
      </div>
      {isFull && <AbsoluteFill style={{ background: "linear-gradient(transparent 55%, rgba(18,6,26,0.65) 100%)" }} />}
      {Overlay && <AbsoluteFill style={{ opacity: overlayOut }}><Overlay t0={scene.s} /></AbsoluteFill>}
      {scene.badge?.map((b) => <Badge key={b.s} {...b} />)}
      {!scene.hideCaps && <Captions y={capY} />}
    </AbsoluteFill>
  );
};
