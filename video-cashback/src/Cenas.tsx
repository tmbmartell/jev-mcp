import React from "react";
import geo from "./geo.json";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { COR, FONTE, H, W, f, seg } from "./base";
import { camera, SP } from "./Mapa";
import { Alerta, CasaRetorno, Calendario, Carrinho, Celular, Chama, Check, Engrenagem, Esgoto, Gota, IdCPF, Pessoa, Prato, Raio } from "./Icones";
import { Pop, Rotulo, Titulo, Vidro, usePop } from "./UI";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ---- layout vertical 1080x1920 ----
// Cenas com mapa: Brasil em cima, card embaixo (acima das legendas, que ficam em y≈1450).
const blocoMapa: React.CSSProperties = { position: "absolute", left: 60, right: 60, top: 1040, display: "flex", flexDirection: "column", gap: 24 };
// Cenas sem mapa: conteúdo centralizado na área útil.
const blocoCentro: React.CSSProperties = { position: "absolute", left: 60, right: 60, top: 220, bottom: 520, display: "flex", flexDirection: "column", justifyContent: "center", gap: 34 };

// ================= Fundos das cenas SEM mapa =================
type Fundo = { id: string; cor: string; marca: string };
const FUNDOS_A: Fundo[] = [
  { id: "s04", cor: "#0d1a33", marca: "%" },
  { id: "s05", cor: "#2a160c", marca: "R$" },
  { id: "s06", cor: "#06262b", marca: "CBS" },
  { id: "s07", cor: "#1c1233", marca: "20%" },
];
const FUNDOS_B: Fundo[] = [
  { id: "s10", cor: "#082417", marca: "CPF" },
  { id: "s11", cor: "#121833", marca: "2027" },
  { id: "s12", cor: "#2b2006", marca: "R$" },
];

const CamadaFundo: React.FC<{ fundos: Fundo[]; fim: string }> = ({ fundos, fim }) => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const ini = seg(fundos[0].id).start;
  const tf = seg(fim).start;
  const o = interpolate(t, [ini - 0.25, ini + 0.1, tf - 0.25, tf + 0.1], [0, 1, 1, 0], clamp);
  if (o <= 0) return null;
  return (
    <AbsoluteFill style={{ opacity: o }}>
      {fundos.map((fu, i) => {
        const a = seg(fu.id).start;
        const b = i < fundos.length - 1 ? seg(fundos[i + 1].id).start : tf + 1;
        const oi = i === 0 ? interpolate(t, [b - 0.2, b + 0.2], [1, 0], clamp) : interpolate(t, [a - 0.2, a + 0.2, b - 0.2, b + 0.2], [0, 1, 1, i === fundos.length - 1 ? 1 : 0], clamp);
        if (oi <= 0) return null;
        const local = t - a;
        return (
          <AbsoluteFill key={fu.id} style={{ opacity: oi, background: `radial-gradient(ellipse at 50% 35%, ${fu.cor} 0%, #05070b 75%)` }}>
            {/* marca d'água gigante, deslizando devagar */}
            <div
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                top: 420,
                textAlign: "center",
                fontFamily: FONTE,
                fontWeight: 900,
                fontSize: fu.marca.length > 3 ? 360 : 560,
                color: "rgba(255,255,255,0.045)",
                transform: `translateY(${-local * 18}px) rotate(-8deg)`,
                letterSpacing: -10,
              }}
            >
              {fu.marca}
            </div>
          </AbsoluteFill>
        );
      })}
      {/* grade técnica em movimento */}
      <AbsoluteFill
        style={{
          backgroundImage: "linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)",
          backgroundSize: "72px 72px",
          backgroundPosition: `0px ${(t * 14) % 72}px`,
          maskImage: "radial-gradient(ellipse at 50% 40%, black 20%, transparent 75%)",
          WebkitMaskImage: "radial-gradient(ellipse at 50% 40%, black 20%, transparent 75%)",
        }}
      />
      {/* partículas douradas flutuando */}
      {Array.from({ length: 18 }).map((_, i) => {
        const x = (i * 197) % W;
        const y = (H - ((t * (20 + (i % 5) * 8) + i * 233) % (H + 100))) | 0;
        return <div key={i} style={{ position: "absolute", left: x, top: y, width: 6 + (i % 3) * 3, height: 6 + (i % 3) * 3, borderRadius: 10, background: COR.ouro, opacity: 0.18 + (i % 4) * 0.05, filter: "blur(1px)" }} />;
      })}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 50%, rgba(0,0,0,0.75) 100%)" }} />
    </AbsoluteFill>
  );
};

export const Fundos: React.FC = () => (
  <>
    <CamadaFundo fundos={FUNDOS_A} fim="s08" />
    <CamadaFundo fundos={FUNDOS_B} fim="s13" />
  </>
);

// ================= Cenas =================

/** s01 — carrinho surge sobre São Paulo (acompanha a câmera). */
export const C01: React.FC = () => {
  const frame = useCurrentFrame();
  const tAbs = seg("s01").start + frame / 30;
  const { cx, cy, z } = camera(tAbs);
  const x = (SP[0] - cx) * z + W / 2;
  const y = (SP[1] - cy) * z + H / 2;
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: x - 70, top: y - 150 }}>
        <Pop de={f(2.2)}>
          <Carrinho size={130} />
        </Pop>
      </div>
    </AbsoluteFill>
  );
};

/** s02 — "O DINHEIRO VOLTA?" */
export const C02: React.FC = () => (
  <AbsoluteFill style={{ alignItems: "center", paddingTop: 210 }}>
    <Titulo texto="O dinheiro *volta?*" size={112} de={f(0.9)} style={{ textAlign: "center", width: 960 }} />
  </AbsoluteFill>
);

/** s03 — contador 70 milhões + cashback tributário */
export const C03: React.FC = () => {
  const frame = useCurrentFrame();
  const n = interpolate(frame, [f(0.6), f(3.2)], [0, 70], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 150, left: 60, right: 60, display: "flex", alignItems: "center", justifyContent: "center", gap: 24 }}>
        <Pop de={f(5.2)}>
          <CasaRetorno size={110} />
        </Pop>
        <Titulo texto="Cashback *tributário*" size={70} de={f(5.4)} />
      </div>
      <div style={blocoMapa}>
        <Vidro de={f(0.3)}>
          <Rotulo>A partir de janeiro de 2027</Rotulo>
          <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 130, color: COR.ouro, lineHeight: 1, marginTop: 8, whiteSpace: "nowrap" }}>
            {Math.round(n)} <span style={{ fontSize: 76 }}>MILHÕES</span>
          </div>
          <Rotulo size={34} cor={COR.branco}>de brasileiros</Rotulo>
          <div style={{ display: "flex", gap: 6, marginTop: 18, flexWrap: "wrap" }}>
            {Array.from({ length: 50 }).map((_, i) => {
              const o = interpolate(frame, [f(0.8) + i * 1.5, f(0.8) + i * 1.5 + 6], [0, 1], clamp);
              return (
                <div key={i} style={{ opacity: o, transform: `scale(${0.5 + 0.5 * o})` }}>
                  <Pessoa size={26} cor={i % 5 === 0 ? COR.ouro : "rgba(255,255,255,0.85)"} />
                </div>
              );
            })}
          </div>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s04 — peso do imposto: quem ganha menos x quem ganha mais (sem mapa) */
export const C04: React.FC = () => {
  const frame = useCurrentFrame();
  const b1 = interpolate(frame, [f(1.2), f(2.6)], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const b2 = interpolate(frame, [f(2.0), f(3.2)], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const Barra: React.FC<{ p: number; alt: number; cor: string; rot: string }> = ({ p, alt, cor, rot }) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16, width: 340 }}>
      <div style={{ height: 470, display: "flex", alignItems: "flex-end" }}>
        <div style={{ width: 190, height: alt * p, background: cor, borderRadius: "16px 16px 4px 4px", boxShadow: `0 0 50px ${cor}66` }} />
      </div>
      <Rotulo size={30} cor={COR.branco} style={{ textAlign: "center" }}>{rot}</Rotulo>
    </div>
  );
  return (
    <AbsoluteFill>
      <div style={blocoCentro}>
        <Titulo texto="Quem ganha menos *sente mais*" size={76} de={f(0.2)} style={{ textAlign: "center" }} />
        <Vidro de={f(0.4)}>
          <Rotulo style={{ textAlign: "center" }}>Peso do imposto no orçamento</Rotulo>
          <div style={{ display: "flex", justifyContent: "space-around", marginTop: 26 }}>
            <Barra p={b1} alt={450} cor={COR.ouro} rot="Quem ganha menos" />
            <Barra p={b2} alt={170} cor="rgba(255,255,255,0.55)" rot="Quem ganha mais" />
          </div>
        </Vidro>
        <div style={{ opacity: interpolate(frame, [f(4.0), f(4.5)], [0, 1], clamp) }}>
          <Titulo texto="Meta: *diminuir a desigualdade*" size={44} de={f(4.0)} style={{ textAlign: "center" }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** s05 — nota fiscal: não é a compra, é o imposto (sem mapa) */
export const C05: React.FC = () => {
  const frame = useCurrentFrame();
  const risco = interpolate(frame, [f(1.0), f(1.5)], [0, 1], clamp);
  const brilho = interpolate(frame, [f(2.3), f(2.8)], [0, 1], clamp);
  const linha = (a: string, b: string, extra?: React.CSSProperties) => (
    <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "monospace", fontSize: 36, color: "#222", padding: "7px 0", ...extra }}>
      <span>{a}</span>
      <span>{b}</span>
    </div>
  );
  return (
    <AbsoluteFill>
      <div style={{ ...blocoCentro, alignItems: "center" }}>
        <Pop de={f(0.1)} dy={80}>
          <div style={{ width: 640, background: "#f4f1ea", padding: "40px 46px", borderRadius: 6, boxShadow: "0 30px 80px rgba(0,0,0,0.7)", transform: "rotate(-3deg)" }}>
            <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 36, textAlign: "center", color: "#222" }}>NOTA FISCAL</div>
            <div style={{ borderTop: "3px dashed #999", margin: "16px 0" }} />
            {linha("ARROZ 5KG", "R$ 30,00")}
            {linha("FEIJÃO 1KG", "R$ 9,00")}
            {linha("ÓLEO 900ML", "R$ 8,00")}
            {linha("OUTROS", "R$ 53,00")}
            <div style={{ borderTop: "3px dashed #999", margin: "16px 0" }} />
            <div style={{ position: "relative" }}>
              {linha("TOTAL", "R$ 100,00", { fontWeight: 900, fontSize: 40 })}
              <div style={{ position: "absolute", left: -10, top: "50%", height: 7, width: `${risco * 105}%`, background: COR.vermelho, transform: "rotate(-4deg)" }} />
            </div>
            <div style={{ background: `rgba(245,197,66,${brilho})`, boxShadow: `0 0 ${50 * brilho}px rgba(245,197,66,${brilho})`, borderRadius: 6, padding: "0 12px", marginTop: 8 }}>
              {linha("IMPOSTOS", "R$ XX,XX", { fontWeight: 900 })}
            </div>
            <div style={{ fontFamily: FONTE, fontSize: 18, color: "#888", marginTop: 14, textAlign: "center" }}>VALORES ILUSTRATIVOS</div>
          </div>
        </Pop>
        <div style={{ textAlign: "center", marginTop: 20 }}>
          <Titulo texto="Não é a compra." size={74} de={f(0.9)} />
          <Titulo texto="É o *imposto.*" size={112} de={f(2.4)} style={{ marginTop: 6 }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** s06 — contas com 100% da CBS (sem mapa) */
export const C06: React.FC = () => {
  const itens: [React.ReactNode, string][] = [
    [<Gota size={120} />, "Água"],
    [<Raio size={120} />, "Energia"],
    [<Esgoto size={120} />, "Esgoto"],
    [<Chama size={120} />, "Gás canalizado"],
    [<Celular size={120} />, "Telefonia"],
  ];
  const tempos = [0.6, 1.0, 1.4, 1.85, 2.6];
  return (
    <AbsoluteFill>
      <div style={blocoCentro}>
        <Titulo texto="Contas *essenciais*" size={80} de={f(0.1)} style={{ textAlign: "center" }} />
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "40px 50px" }}>
          {itens.map(([ic, nome], i) => (
            <Pop key={nome} de={f(tempos[i])}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, width: 250 }}>
                {ic}
                <Rotulo size={26} cor={COR.branco} style={{ textAlign: "center", letterSpacing: 1 }}>{nome}</Rotulo>
              </div>
            </Pop>
          ))}
        </div>
        <Vidro de={f(3.9)} style={{ textAlign: "center" }}>
          <Titulo texto="*100%*" size={190} de={f(4.0)} />
          <Titulo texto="da CBS de volta" size={56} de={f(4.3)} />
          <Rotulo size={22} style={{ marginTop: 10, opacity: 0.8 }}>CBS = novo imposto federal sobre consumo</Rotulo>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s07 — outras compras: 20% (sem mapa) */
export const C07: React.FC = () => {
  const frame = useCurrentFrame();
  const a = interpolate(frame, [f(0.3), f(1.0)], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const b = interpolate(frame, [f(1.4), f(2.0)], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const Coluna: React.FC<{ p: number; v: number; rot: string; cor: string; icone: React.ReactNode }> = ({ p, v, rot, cor, icone }) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, width: 360 }}>
      <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 96, color: cor }}>{Math.round(v * p)}%</div>
      <div style={{ height: 420, width: 170, background: "rgba(255,255,255,0.07)", borderRadius: 16, display: "flex", alignItems: "flex-end", overflow: "hidden" }}>
        <div style={{ width: "100%", height: `${v * p}%`, background: cor, borderRadius: 16, boxShadow: `0 0 40px ${cor}` }} />
      </div>
      {icone}
      <Rotulo size={26} cor={COR.branco} style={{ textAlign: "center" }}>{rot}</Rotulo>
    </div>
  );
  return (
    <AbsoluteFill>
      <div style={blocoCentro}>
        <Titulo texto="Devolução *da CBS*" size={80} de={f(0)} style={{ textAlign: "center" }} />
        <Vidro de={f(0.1)} style={{ display: "flex", justifyContent: "space-around" }}>
          <Coluna p={a} v={100} rot="Contas essenciais" cor={COR.verde} icone={<Raio size={90} />} />
          <Coluna p={b} v={20} rot="Outras compras elegíveis" cor={COR.ouro} icone={<Carrinho size={90} />} />
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s08 — quebra histórica: 1789, a Derrama (pergaminho sépia + Ken Burns) */
export const C08: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const kb = interpolate(frame, [0, dur], [1.0, 1.16]);
  const py = interpolate(frame, [0, dur], [0, -50]);
  const entrada = interpolate(frame, [0, 10], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ opacity: entrada, background: "#1a120a" }}>
      <AbsoluteFill style={{ transform: `scale(${kb}) translateY(${py}px)`, transformOrigin: "50% 45%" }}>
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 42%, #e6d3a8 0%, #cdb17c 45%, #8d6a3a 100%)" }} />
        <svg width={W} height={H} style={{ position: "absolute", inset: 0, mixBlendMode: "multiply", opacity: 0.55 }}>
          <filter id="papel">
            <feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves={4} seed={3} />
            <feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.32  0 0 0 0 0.18  0 0 0 0.9 0" />
          </filter>
          <rect width={W} height={H} filter="url(#papel)" />
        </svg>
        <MapaAntigo />
        <svg width={180} height={180} viewBox="-110 -110 220 220" style={{ position: "absolute", right: 70, top: 470, opacity: 0.75 }}>
          <circle r={90} fill="none" stroke="#4a3218" strokeWidth={2} />
          <circle r={70} fill="none" stroke="#4a3218" strokeWidth={1} />
          {[0, 90, 180, 270].map((a) => (
            <path key={a} d="M0,-100 L14,0 L0,14 L-14,0 Z" fill={a === 0 ? "#4a3218" : "#8a6a3a"} transform={`rotate(${a})`} />
          ))}
          {[45, 135, 225, 315].map((a) => (
            <path key={a} d="M0,-62 L8,0 L-8,0 Z" fill="#6b4c26" transform={`rotate(${a})`} />
          ))}
          <text y={-104} textAnchor="middle" fontFamily="Playfair Display" fontWeight={900} fontSize={24} fill="#4a3218">N</text>
        </svg>
      </AbsoluteFill>

      <div style={{ position: "absolute", left: 70, top: 190 }}>
        <div style={{ fontFamily: "Playfair Display", fontWeight: 900, fontSize: 200, color: "#3b2610", lineHeight: 0.9, opacity: interpolate(frame, [f(0.8), f(1.6)], [0, 1], clamp) }}>1789</div>
        <div style={{ fontFamily: "Playfair Display", fontStyle: "italic", fontWeight: 700, fontSize: 72, color: "#5a3a17", opacity: interpolate(frame, [f(3.6), f(4.4)], [0, 1], clamp) }}>A Derrama</div>
      </div>
      <div style={{ position: "absolute", left: 60, right: 60, top: 1150, padding: "24px 30px", background: "rgba(240,225,190,0.85)", border: "2px solid #6b4c26", borderRadius: 8, boxShadow: "0 10px 30px rgba(40,20,0,0.35)", opacity: interpolate(frame, [f(1.8), f(2.6)], [0, 1], clamp) }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ fontFamily: "Playfair Display", fontWeight: 900, fontSize: 50, color: "#3b2610" }}>O Quinto</div>
          <div style={{ display: "flex", gap: 10 }}>
            {Array.from({ length: 5 }).map((_, i) => {
              const coroa = i === 4;
              const lev = coroa ? interpolate(frame, [f(2.8), f(3.6)], [0, -30], { ...clamp, easing: Easing.out(Easing.back(2)) }) : 0;
              return (
                <svg key={i} width={96} height={58} viewBox="0 0 100 60" style={{ transform: `translateY(${lev}px)` }}>
                  <path d="M14 8 H86 L98 52 H2 Z" fill={coroa ? "#E8B53A" : "#a88a55"} stroke="#4a3218" strokeWidth={3} />
                  <path d="M20 14 H80" stroke={coroa ? "#FFE7A0" : "#c9ad7a"} strokeWidth={4} />
                </svg>
              );
            })}
          </div>
        </div>
        <div style={{ fontFamily: "Playfair Display", fontStyle: "italic", fontWeight: 700, fontSize: 34, color: "#4a3218", marginTop: 10 }}>1/5 de todo o ouro ia para a Coroa</div>
        <div style={{ fontFamily: FONTE, fontWeight: 800, fontSize: 28, color: "#7a2a12", marginTop: 6, letterSpacing: 1, opacity: interpolate(frame, [f(5.0), f(5.6)], [0, 1], clamp) }}>1/5 = 20%. COINCIDÊNCIA?</div>
      </div>

      <svg width={W} height={H} style={{ position: "absolute", inset: 0, opacity: 0.22, mixBlendMode: "overlay" }}>
        <filter id="grao">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={1} seed={frame % 12} />
        </filter>
        <rect width={W} height={H} filter="url(#grao)" />
      </svg>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 40%, rgba(20,10,0,0.85) 100%)", opacity: 0.9 + 0.1 * Math.sin(frame * 1.7) }} />
    </AbsoluteFill>
  );
};

const MapaAntigo: React.FC = () => {
  const frame = useCurrentFrame();
  const desenho = interpolate(frame, [0, f(3)], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const mg = geo.estados.find((e) => e.sigla === "MG")!;
  const vizinhos = geo.estados.filter((e) => ["SP", "RJ", "ES", "BA", "GO", "DF", "MS"].includes(e.sigla));
  const [x0, y0] = [((-52 + 180) / 360) * 4096, ((90 - -13) / 180) * 2048];
  const [x1, y1] = [((-39 + 180) / 360) * 4096, ((90 - -24) / 180) * 2048];
  const lx = (lon: number) => ((lon + 180) / 360) * 4096;
  const ly = (lat: number) => ((90 - lat) / 180) * 2048;
  return (
    <svg width={1000} height={850} viewBox={`${x0} ${y0} ${x1 - x0} ${y1 - y0}`} style={{ position: "absolute", left: 40, top: 430 }}>
      <defs>
        <pattern id="hachura" width={2} height={2} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1={0} y1={0} x2={0} y2={2} stroke="#6b4c26" strokeWidth={0.5} />
        </pattern>
      </defs>
      {vizinhos.map((e) => (
        <path key={e.sigla} d={e.d} fill="none" stroke="#6b4c26" strokeWidth={0.5} opacity={0.6 * desenho} />
      ))}
      <path d={mg.d} fill="url(#hachura)" stroke="#3b2610" strokeWidth={1.4} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - desenho} fillOpacity={interpolate(frame, [f(2.2), f(3.2)], [0, 0.55], clamp)} />
      <text x={lx(-45.5)} y={ly(-17.2)} textAnchor="middle" fontFamily="Playfair Display" fontStyle="italic" fontWeight={700} fontSize={6.5} fill="#3b2610" opacity={interpolate(frame, [f(2.6), f(3.4)], [0, 1], clamp)}>
        Capitania de Minas Gerais
      </text>
      <circle cx={lx(-43.5)} cy={ly(-20.38)} r={1.6} fill="#7a2a12" opacity={interpolate(frame, [f(3.4), f(3.8)], [0, 1], clamp)} />
      <text x={lx(-43.5) + 3} y={ly(-20.38) + 6} fontFamily="Playfair Display" fontWeight={700} fontSize={4.5} fill="#7a2a12" opacity={interpolate(frame, [f(3.4), f(3.8)], [0, 1], clamp)}>
        Vila Rica
      </text>
    </svg>
  );
};

/** s09 — checklist de requisitos (com mapa) */
export const C09: React.FC = () => {
  const itens = ["Inscrito no Cadastro Único", "Renda de até ½ salário mínimo por pessoa", "CPF regular"];
  const t = [1.3, 2.6, 4.5];
  return (
    <AbsoluteFill>
      <div style={blocoMapa}>
        <Vidro de={f(0.1)} style={{ padding: "28px 40px" }}>
          <Titulo texto="Quem *recebe?*" size={58} de={f(0.2)} />
          <div style={{ marginTop: 20, display: "flex", flexDirection: "column", gap: 18 }}>
            {itens.map((it, i) => (
              <ItemCheck key={it} de={f(t[i])} texto={it} />
            ))}
          </div>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};
const ItemCheck: React.FC<{ de: number; texto: string; size?: number }> = ({ de, texto, size = 34 }) => {
  const frame = useCurrentFrame();
  const s = usePop(de);
  const p = interpolate(frame, [de + 4, de + 12], [0, 1], clamp);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 22, opacity: 0.35 + 0.65 * Math.min(1, s), transform: `translateX(${(1 - s) * 30}px)` }}>
      <div style={{ width: 62, height: 62, flexShrink: 0, borderRadius: 31, border: "3px solid rgba(255,255,255,0.4)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        {frame >= de && <Check size={58} p={p} />}
      </div>
      <div style={{ fontFamily: FONTE, fontWeight: 800, fontSize: size, color: COR.branco, textTransform: "uppercase", lineHeight: 1.15 }}>{texto}</div>
    </div>
  );
};

/** s10 — automático + CPF na nota (sem mapa) */
export const C10: React.FC = () => {
  const frame = useCurrentFrame();
  const enc = interpolate(frame, [f(3.6), f(4.5)], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  return (
    <AbsoluteFill>
      <div style={blocoCentro}>
        <Vidro de={f(0)} style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 26 }}>
          <Pop de={f(0.3)}>
            <Engrenagem size={100} cor={COR.verde} />
          </Pop>
          <Titulo texto="Benefício *automático*" size={62} de={f(0.4)} />
        </Vidro>
        <Vidro de={f(1.6)}>
          <Rotulo>Mas não esqueça</Rotulo>
          <div style={{ display: "flex", flexDirection: "column", gap: 20, marginTop: 20 }}>
            <ItemCheck de={f(2.0)} texto="Cadastro atualizado" size={40} />
            <ItemCheck de={f(4.2)} texto="CPF na nota" size={40} />
          </div>
          <div style={{ position: "relative", height: 380, marginTop: 20 }}>
            <div style={{ position: "absolute", right: 70, top: 10, width: 260, height: 350, background: "#f4f1ea", borderRadius: 6, padding: 22, boxShadow: "0 12px 30px rgba(0,0,0,0.5)", transform: "rotate(3deg)" }}>
              <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 26, color: "#222" }}>NOTA FISCAL</div>
              {[0, 1, 2, 3, 4].map((i) => (
                <div key={i} style={{ height: 10, background: "#ccc", marginTop: 18, borderRadius: 4, width: `${90 - i * 10}%` }} />
              ))}
              <div style={{ marginTop: 28, fontFamily: FONTE, fontWeight: 900, fontSize: 28, color: enc > 0.95 ? "#1f8a4c" : "#999" }}>CPF: {enc > 0.95 ? "✓" : "____"}</div>
            </div>
            <div style={{ position: "absolute", left: interpolate(enc, [0, 1], [20, 470]), top: interpolate(enc, [0, 1], [40, 190]), transform: `rotate(${interpolate(enc, [0, 1], [-14, 3])}deg) scale(${interpolate(enc, [0, 1], [1, 0.6])})`, transformOrigin: "0 0", opacity: interpolate(frame, [f(3.0), f(3.3)], [0, 1], clamp) }}>
              <IdCPF size={320} />
            </div>
          </div>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s11 — linha do tempo jan -> abr 2027 (sem mapa) */
export const C11: React.FC = () => {
  const frame = useCurrentFrame();
  const linha = interpolate(frame, [f(1.0), f(3.0)], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const meses = ["JAN", "FEV", "MAR", "ABR"];
  return (
    <AbsoluteFill>
      <div style={blocoCentro}>
        <Titulo texto="*Quando* chega?" size={90} de={f(0)} style={{ textAlign: "center" }} />
        <Vidro de={f(0.2)} style={{ position: "relative", height: 760, padding: 0 }}>
          {/* linha vertical */}
          <div style={{ position: "absolute", left: 200, top: 110, height: 540, width: 10, background: "rgba(255,255,255,0.15)", borderRadius: 5 }} />
          <div style={{ position: "absolute", left: 200, top: 110, height: 540 * linha, width: 10, background: COR.ouro, borderRadius: 5, boxShadow: `0 0 20px ${COR.ouro}` }} />
          {meses.map((m, i) => {
            const y = 110 + (i / 3) * 540;
            const ativo = linha >= i / 3 - 0.001;
            const ponta = i === 0 || i === 3;
            return (
              <div key={m} style={{ position: "absolute", left: 0, right: 0, top: y - 85, height: 170, display: "flex", alignItems: "center" }}>
                {ponta ? (
                  <div style={{ position: "absolute", left: 120 }}>
                    <Pop de={i === 0 ? f(0.3) : f(3.0)}>
                      <Calendario mes={m} ano="2027" size={170} destaque={i === 3} />
                    </Pop>
                  </div>
                ) : (
                  <div style={{ position: "absolute", left: 186, width: 38, height: 38, borderRadius: 19, background: ativo ? COR.ouro : "#333", border: "4px solid #fff" }} />
                )}
                <div style={{ position: "absolute", left: ponta ? 340 : 270 }}>
                  {i === 0 && <Rotulo size={40} cor={COR.branco}>Começa o programa</Rotulo>}
                  {i === 3 && <Rotulo size={40} cor={COR.ouro} style={{ opacity: interpolate(frame, [f(3.0), f(3.4)], [0, 1], clamp) }}>1ª devolução em dinheiro</Rotulo>}
                  {!ponta && <Rotulo size={30} style={{ opacity: ativo ? 0.8 : 0.3 }}>{m}</Rotulo>}
                </div>
              </div>
            );
          })}
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s12 — R$ 10 bi ÷ 70 mi = ~R$ 12/mês (sem mapa) */
export const C12: React.FC = () => {
  const frame = useCurrentFrame();
  const bi = interpolate(frame, [f(0.6), f(2.6)], [0, 10], { ...clamp, easing: Easing.out(Easing.cubic) });
  const div = interpolate(frame, [f(4.0), f(4.6)], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <div style={blocoCentro}>
        <Vidro de={f(0)} style={{ textAlign: "center" }}>
          <Rotulo>Estimativa para 2027</Rotulo>
          <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 150, color: COR.branco, lineHeight: 1.05, whiteSpace: "nowrap" }}>R$ {bi.toFixed(0)}</div>
          <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 80, color: COR.ouro, lineHeight: 1 }}>BILHÕES</div>
        </Vidro>
        <div style={{ opacity: div, display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
          <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 80, color: COR.cinza, lineHeight: 1 }}>÷</div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "center", width: 760 }}>
            {Array.from({ length: 30 }).map((_, i) => (
              <div key={i} style={{ opacity: interpolate(frame, [f(4.0) + i * 1.2, f(4.0) + i * 1.2 + 5], [0, 1], clamp) }}>
                <Pessoa size={30} />
              </div>
            ))}
          </div>
          <Rotulo size={36} cor={COR.branco}>70 milhões de pessoas</Rotulo>
        </div>
        <Vidro de={f(6.2)} style={{ textAlign: "center", border: `2px solid ${COR.ouro}` }}>
          <Titulo texto="≈ *R$ 12*" size={150} de={f(6.3)} />
          <Titulo texto="por mês, por pessoa" size={48} de={f(6.8)} />
          <Rotulo size={20} style={{ marginTop: 10, opacity: 0.7 }}>R$ 10 bi ÷ 70 mi ÷ 12 meses ≈ R$ 11,90</Rotulo>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s13 — o desafio: sistemas (com mapa) */
export const C13: React.FC = () => (
  <AbsoluteFill>
    <div style={{ position: "absolute", left: 0, right: 0, top: 170, display: "flex", alignItems: "center", justifyContent: "center", gap: 26 }}>
      <Pop de={f(0.2)}>
        <Alerta size={120} />
      </Pop>
      <Titulo texto="O *desafio*" size={110} de={f(0.3)} />
    </div>
    <div style={{ ...blocoMapa, top: 1130 }}>
      <Vidro de={f(1.6)} style={{ display: "flex", alignItems: "center", gap: 28, padding: "26px 40px" }}>
        <Pop de={f(1.8)}>
          <Engrenagem size={90} />
        </Pop>
        <Pop de={f(2.1)}>
          <Engrenagem size={60} cor={COR.vermelho} />
        </Pop>
        <Rotulo size={36} cor={COR.branco}>
          Sistemas prontos?
          <br />
          <span style={{ color: COR.ouro }}>Dinheiro chegando?</span>
        </Rotulo>
      </Vidro>
    </div>
  </AbsoluteFill>
);

/** s14 — prometer ≠ entregar, à mesa de quem precisa (com mapa) */
export const C14: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 0, right: 0, top: 170, textAlign: "center" }}>
        <Titulo texto="Prometer" size={110} de={f(0.3)} />
        <Titulo texto="≠ *entregar*" size={110} de={f(2.4)} />
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 1060, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <Pop de={f(3.4)}>
          <div style={{ position: "relative" }}>
            <Prato size={340} />
            {[0, 1, 2].map((i) => {
              const p = interpolate(frame, [f(4.2) + i * 6, f(4.8) + i * 6], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) });
              return (
                <svg key={i} width={52} height={52} viewBox="0 0 100 100" style={{ position: "absolute", left: 125 + i * 44, top: interpolate(p, [0, 1], [-300, 140]), opacity: p > 0 ? 1 : 0 }}>
                  <circle cx={50} cy={50} r={44} fill="#C98F12" />
                  <circle cx={50} cy={50} r={36} fill={COR.ouro} />
                </svg>
              );
            })}
          </div>
        </Pop>
        <Rotulo size={30} cor={COR.branco} style={{ textAlign: "center", marginTop: -50 }}>À mesa de quem precisa</Rotulo>
      </div>
    </AbsoluteFill>
  );
};

/** s15 — CTA */
export const C15: React.FC = () => {
  const s = usePop(f(4.6));
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", paddingBottom: 380, background: "rgba(0,0,0,0.4)", textAlign: "center" }}>
      <Titulo texto="Devolver parte" size={74} de={f(0.5)} />
      <Titulo texto="do imposto é" size={74} de={f(1.0)} />
      <Titulo texto="*suficiente?*" size={118} de={f(1.5)} />
      <Titulo texto="Ou o básico deveria" size={62} de={f(2.8)} style={{ marginTop: 40 }} />
      <Titulo texto="*custar menos?*" size={112} de={f(3.8)} />
      <div style={{ marginTop: 40, transform: `scale(${s})`, background: COR.ouro, color: "#141a22", fontFamily: FONTE, fontWeight: 900, fontSize: 46, padding: "16px 44px", borderRadius: 50 }}>
        COMENTA AÍ ↓
      </div>
    </AbsoluteFill>
  );
};
