import React from "react";
import { Easing, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import geo from "./geo.json";
import { COR, FONTE, H, W, geoPx, seg } from "./base";

type Cam = { t: number; cx: number; cy: number; z: number };

// layout vertical (1080x1920): o Brasil ocupa a metade de cima e os cards ficam embaixo
const BR: [number, number] = [1440, 1185];
/** Brasil com o centro na altura `y` da tela. */
const brEm = (z: number, y: number): Omit<Cam, "t"> => ({ cx: BR[0], cy: BR[1] + (H / 2 - y) / z, z });
const MUNDO = { cx: 1560, cy: 1060, z: 0.94 };
const BSB = geoPx(-47.93, -15.78);
const bsbEm = (z: number, y: number): Omit<Cam, "t"> => ({ cx: BSB[0], cy: BSB[1] + (H / 2 - y) / z, z });

const keys = (): Cam[] => {
  const s = (id: string) => seg(id).start;
  return [
    { t: 0, ...MUNDO },
    { t: 0.4, ...MUNDO },
    { t: 3.4, ...brEm(2.1, 860) },
    { t: s("s02") + 3, ...brEm(2.2, 880) },
    { t: s("s03") + 0.8, ...brEm(2.1, 600) },
    { t: s("s04") + 0.5, ...brEm(2.1, 600) },
    { t: s("s09") - 0.5, ...brEm(2.0, 620) },
    { t: s("s09") + 1.5, ...brEm(2.1, 600) },
    { t: s("s13") + 0.8, ...bsbEm(2.6, 860) },
    { t: s("s14") + 6, ...bsbEm(2.9, 860) },
    { t: s("s15") + 0.3, ...bsbEm(2.9, 860) },
    { t: s("s15") + 3.5, ...MUNDO },
    { t: 999, ...MUNDO },
  ];
};

export const camera = (t: number): Omit<Cam, "t"> => {
  const k = keys();
  let i = 0;
  while (i < k.length - 2 && t > k[i + 1].t) i++;
  const a = k[i], b = k[i + 1];
  const p = interpolate(t, [a.t, b.t], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  // zoom interpolado em escala logarítmica (movimento natural)
  const z = Math.exp(Math.log(a.z) + (Math.log(b.z) - Math.log(a.z)) * p);
  // pequena deriva contínua para o mapa nunca ficar parado
  const drift = 6 / z;
  return { cx: a.cx + (b.cx - a.cx) * p + Math.sin(t * 0.21) * drift, cy: a.cy + (b.cy - a.cy) * p + Math.cos(t * 0.17) * drift, z };
};

// capitais usadas nas rotas de moedas
const CIDADES: [number, number][] = [
  [-60.0, -3.1], [-48.5, -1.45], [-38.5, -3.7], [-34.9, -8.05], [-38.5, -12.97], [-43.9, -19.9], [-43.2, -22.9], [-46.6, -23.5],
  [-49.3, -25.4], [-51.2, -30.0], [-56.1, -15.6], [-63.9, -8.76], [-42.8, -5.1], [-44.3, -2.5], [-54.6, -20.4], [-49.25, -16.7],
].map(([lo, la]) => geoPx(lo, la));
const SP = geoPx(-46.6, -23.5);

const arco = (a: [number, number], b: [number, number], p: number, alt = 0.35): [number, number] => {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
  const d = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const c: [number, number] = [mx, my - d * alt];
  const q = 1 - p;
  return [q * q * a[0] + 2 * q * p * c[0] + p * p * b[0], q * q * a[1] + 2 * q * p * c[1] + p * p * b[1]];
};
const arcoD = (a: [number, number], b: [number, number], alt = 0.35) => {
  const d = Math.hypot(b[0] - a[0], b[1] - a[1]);
  return `M${a[0]},${a[1]} Q${(a[0] + b[0]) / 2},${(a[1] + b[1]) / 2 - d * alt} ${b[0]},${b[1]}`;
};

const MoedaSvg: React.FC<{ x: number; y: number; r: number; o?: number; cor?: string }> = ({ x, y, r, o = 1, cor = COR.ouro }) => (
  <g opacity={o}>
    <circle cx={x} cy={y} r={r} fill="#C98F12" />
    <circle cx={x} cy={y} r={r * 0.8} fill={cor} />
    <text x={x} y={y + r * 0.36} textAnchor="middle" fontSize={r * 1.1} fontWeight={900} fill="#8a5c00" fontFamily="Montserrat">$</text>
  </g>
);

const Pino: React.FC<{ x: number; y: number; s: number; t: number; rotulo?: string; o?: number }> = ({ x, y, s, t, rotulo, o = 1 }) => {
  const pulse = (t * 1.2) % 1;
  return (
    <g opacity={o}>
      <circle cx={x} cy={y} r={(8 + pulse * 30) * s} fill="none" stroke={COR.ouro} strokeWidth={3 * s} opacity={1 - pulse} />
      <circle cx={x} cy={y} r={8 * s} fill={COR.ouro} stroke="#fff" strokeWidth={2.5 * s} />
      {rotulo && (
        <text x={x + 16 * s} y={y - 14 * s} fontSize={26 * s} fontWeight={900} fill="#fff" fontFamily="Montserrat" style={{ paintOrder: "stroke" }} stroke="rgba(0,0,0,0.8)" strokeWidth={6 * s}>
          {rotulo}
        </text>
      )}
    </g>
  );
};

const janelaT = (t: number, a: number, b: number) => interpolate(t, [a, b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

export const Mapa: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const { cx, cy, z } = camera(t);
  const s = 1 / z; // converte px de tela -> px do mundo
  const vb = `${cx - W / 2 / z} ${cy - H / 2 / z} ${W / z} ${H / z}`;
  const S = (id: string) => seg(id).start;

  // intensidade do contorno do Brasil
  const brO = interpolate(t, [1.6, 3.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) * (1 - janelaT(t, S("s15") + 0.6, S("s15") + 3));

  // estados acendendo (70 milhões)
  const iniEst = S("s03") + 0.4;
  const fimEst = S("s04") - 0.3;
  const estOn = t > iniEst && t < S("s05") + 0.5;

  // moedas: ida (s01) e volta (s02)
  const ida = janelaT(t, S("s01") + 3.4, S("s01") + 5.2);
  const voltaIni = S("s02") + 0.2;

  // desafio (s13/s14)
  const dIni = S("s13") + 0.3;
  const dFim = S("s15") + 0.5;
  const desafio = t > dIni && t < dFim;

  return (
    <div style={{ position: "absolute", inset: 0, background: "#000", overflow: "hidden" }}>
      <Img
        src={staticFile("world.jpg")}
        style={{
          position: "absolute",
          left: W / 2 - cx * z,
          top: H / 2 - cy * z,
          width: 4096 * z,
          height: 2048 * z,
          filter: "brightness(0.5) contrast(1.15) saturate(0.85)",
          imageRendering: "auto",
        }}
      />
      <svg width={W} height={H} viewBox={vb} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation={7 * s} />
          </filter>
        </defs>
        {/* fronteiras vizinhas */}
        {geo.vizinhos.map((d, i) => (
          <path key={i} d={d} fill="none" stroke="rgba(255,255,255,0.22)" strokeWidth={1.2 * s} />
        ))}
        {/* estados */}
        {geo.estados.map((e, i) => {
          const ordem = (i * 7) % 27; // ordem "aleatória" estável
          const on = estOn ? janelaT(t, iniEst + (ordem / 27) * (fimEst - iniEst) * 0.5, iniEst + (ordem / 27) * (fimEst - iniEst) * 0.5 + 0.4) : 0;
          const off = janelaT(t, S("s05") - 0.2, S("s05") + 0.5);
          return (
            <path key={e.sigla} d={e.d} fill={`rgba(245,197,66,${0.28 * on * (1 - off)})`} stroke={`rgba(255,255,255,${0.12 + 0.35 * on * (1 - off)})`} strokeWidth={1 * s} opacity={brO} />
          );
        })}
        {/* Brasil com glow verde/amarelo */}
        <g opacity={brO}>
          <path d={geo.brasil} fill="rgba(124,252,106,0.07)" stroke={COR.verde} strokeWidth={9 * s} filter="url(#glow)" opacity={0.75} />
          <path d={geo.brasil} fill="none" stroke={COR.ouro} strokeWidth={2.6 * s} strokeLinejoin="round" />
        </g>

        {/* Brasília */}
        {t > S("s01") + 3 && t < S("s03") + 0.5 && <Pino x={BSB[0]} y={BSB[1]} s={s} t={t} rotulo="BRASÍLIA" o={janelaT(t, S("s01") + 3, S("s01") + 3.4) * (1 - janelaT(t, S("s03"), S("s03") + 0.5))} />}
        {desafio && <Pino x={BSB[0]} y={BSB[1]} s={s} t={t} rotulo="BRASÍLIA" o={janelaT(t, dIni, dIni + 0.4) * (1 - janelaT(t, dFim - 0.8, dFim))} />}

        {/* rota de ida: carrinho (SP) -> Brasília */}
        {t > S("s01") + 3.2 && t < S("s02") + 0.6 && (
          <g opacity={1 - janelaT(t, S("s02"), S("s02") + 0.4)}>
            <path d={arcoD(SP, BSB)} fill="none" stroke={COR.ouro} strokeWidth={2.5 * s} strokeDasharray={`${8 * s} ${8 * s}`} strokeDashoffset={-t * 40 * s} opacity={0.8} />
            {Array.from({ length: 6 }).map((_, k) => {
              const p = Math.min(1, Math.max(0, ida * 1.6 - k * 0.12));
              if (p <= 0 || p >= 1) return null;
              const [x, y] = arco(SP, BSB, p);
              return <MoedaSvg key={k} x={x} y={y} r={13 * s} />;
            })}
          </g>
        )}

        {/* rota de volta: Brasília -> cidades */}
        {t > voltaIni && t < S("s03") + 0.6 &&
          CIDADES.map((c, k) => {
            const p = janelaT(t, voltaIni + 0.6 + k * 0.08, voltaIni + 1.8 + k * 0.08);
            const o = 1 - janelaT(t, S("s03"), S("s03") + 0.5);
            const [x, y] = arco(BSB, c, Easing.out(Easing.cubic)(p), 0.25);
            return (
              <g key={k} opacity={o}>
                <path d={arcoD(BSB, c, 0.25)} fill="none" stroke={COR.ouro} strokeWidth={1.8 * s} opacity={0.5 * p} strokeDasharray={1} pathLength={1} strokeDashoffset={1 - p} />
                {p > 0 && <MoedaSvg x={x} y={y} r={11 * s} />}
              </g>
            );
          })}

        {/* desafio: algumas rotas falham */}
        {desafio &&
          CIDADES.map((c, k) => {
            const ciclo = 2.6;
            const base = dIni + 0.4 + k * 0.17;
            if (t < base) return null;
            const p = ((t - base) % ciclo) / ciclo;
            const falha = k % 3 === 1;
            const o = janelaT(t, dIni, dIni + 0.4) * (1 - janelaT(t, dFim - 0.8, dFim));
            const pf = falha ? Math.min(p, 0.55) : p;
            const [x, y] = arco(BSB, c, pf, 0.25);
            const caiu = falha && p > 0.55;
            return (
              <g key={k} opacity={o}>
                <path d={arcoD(BSB, c, 0.25)} fill="none" stroke={falha ? COR.vermelho : COR.ouro} strokeWidth={2 * s} opacity={falha ? 0.35 + 0.35 * Math.abs(Math.sin(t * 6)) : 0.45} strokeDasharray={falha ? `${6 * s} ${6 * s}` : undefined} />
                {!caiu && <MoedaSvg x={x} y={y} r={10 * s} />}
                {caiu && <MoedaSvg x={x} y={y + (p - 0.55) * 120 * s * 3} r={10 * s} o={1 - (p - 0.55) / 0.45} cor="#9a8a6a" />}
                {falha && p > 0.5 && (
                  <text x={arco(BSB, c, 0.55, 0.25)[0]} y={arco(BSB, c, 0.55, 0.25)[1] - 16 * s} textAnchor="middle" fontSize={30 * s} fontWeight={900} fill={COR.vermelho} fontFamily="Montserrat" stroke="#000" strokeWidth={3 * s} style={{ paintOrder: "stroke" }}>
                    ✕
                  </text>
                )}
              </g>
            );
          })}
      </svg>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 40%, rgba(0,0,0,0.8) 100%)" }} />
      {/* selo de fonte, discreto */}
      <div style={{ position: "absolute", right: 28, top: 22, fontFamily: FONTE, fontWeight: 600, fontSize: 16, color: "rgba(255,255,255,0.35)", letterSpacing: 1 }}>
        IMAGEM DE SATÉLITE: NASA BLUE MARBLE
      </div>
    </div>
  );
};

export { SP, BSB };
