import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import geo from "./geo.json";
import { COR, FONTE, H, W, geoPx } from "./base";
import { Moeda } from "./Icones";

/** Capa vertical (1080x1920). O texto principal fica no miolo 3:4 (y 240–1680), que é o recorte do perfil. */
export const Capa: React.FC = () => {
  const z = 2.35;
  const [cx, cy] = [1440, 1185 + (H / 2 - 1080) / z];
  const vb = `${cx - W / 2 / z} ${cy - H / 2 / z} ${W / z} ${H / z}`;
  const BSB = geoPx(-47.93, -15.78);
  const moedas: [number, number, number, number][] = [
    [90, 360, 120, -20], [900, 300, 150, 15], [850, 1420, 110, 25], [60, 1250, 95, -10], [960, 760, 80, 30], [40, 820, 70, 10], [700, 1560, 90, -25], [200, 1600, 120, 20],
  ];
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <Img src={staticFile("world.jpg")} style={{ position: "absolute", left: W / 2 - cx * z, top: H / 2 - cy * z, width: 4096 * z, height: 2048 * z, filter: "brightness(0.42) contrast(1.15) saturate(0.85) blur(1px)" }} />
      <svg width={W} height={H} viewBox={vb} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <filter id="g" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation={9 / z} />
          </filter>
          <radialGradient id="rg">
            <stop offset="0" stopColor={COR.ouro} stopOpacity={0.55} />
            <stop offset="1" stopColor={COR.ouro} stopOpacity={0} />
          </radialGradient>
        </defs>
        {geo.estados.map((e) => (
          <path key={e.sigla} d={e.d} fill="rgba(245,197,66,0.16)" stroke="rgba(255,255,255,0.25)" strokeWidth={1 / z} />
        ))}
        <path d={geo.brasil} fill="none" stroke={COR.verde} strokeWidth={12 / z} filter="url(#g)" opacity={0.85} />
        <path d={geo.brasil} fill="none" stroke={COR.ouro} strokeWidth={3.5 / z} />
        <circle cx={BSB[0]} cy={BSB[1]} r={90 / z} fill="url(#rg)" />
      </svg>
      {/* escurece atrás do texto */}
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.25) 35%, rgba(0,0,0,0.25) 60%, rgba(0,0,0,0.85) 100%)" }} />
      {moedas.map(([x, y, s, r], i) => (
        <div key={i} style={{ position: "absolute", left: x, top: y, transform: `rotate(${r}deg)`, filter: i % 3 === 0 ? "blur(2px)" : undefined }}>
          <Moeda size={s} />
        </div>
      ))}
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 300, fontFamily: FONTE, textTransform: "uppercase", textAlign: "center" }}>
        <div style={{ background: COR.ouro, color: "#111", fontWeight: 900, fontSize: 40, padding: "12px 34px", borderRadius: 60, letterSpacing: 2 }}>Reforma tributária · 2027</div>
        <div style={{ fontWeight: 900, fontSize: 230, color: COR.ouro, lineHeight: 0.95, marginTop: 40, textShadow: "0 10px 40px rgba(0,0,0,0.9)", letterSpacing: -6 }}>70 MI</div>
        <div style={{ fontWeight: 900, fontSize: 70, color: "#fff", lineHeight: 1, textShadow: "0 6px 24px rgba(0,0,0,0.9)" }}>de brasileiros</div>
        <div style={{ fontWeight: 900, fontSize: 70, color: "#fff", lineHeight: 1.1, textShadow: "0 6px 24px rgba(0,0,0,0.9)" }}>vão receber</div>
        <div style={{ marginTop: 18, background: "#fff", color: "#111", fontWeight: 900, fontSize: 120, lineHeight: 1, padding: "14px 30px 6px", transform: "rotate(-3deg)", boxShadow: "0 20px 60px rgba(0,0,0,0.6)" }}>Dinheiro</div>
        <div style={{ marginTop: 8, background: COR.vermelho, color: "#fff", fontWeight: 900, fontSize: 120, lineHeight: 1, padding: "14px 30px 6px", transform: "rotate(-3deg)", boxShadow: "0 20px 60px rgba(0,0,0,0.6)" }}>de volta</div>
        <div style={{ marginTop: 70, fontWeight: 900, fontSize: 58, color: "#fff", textShadow: "0 6px 24px rgba(0,0,0,0.9)" }}>
          Você está na <span style={{ color: COR.ouro }}>lista?</span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
