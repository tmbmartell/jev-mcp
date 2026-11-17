import React from "react";
import geo from "./geo.json";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { COR, FONTE, H, W, f, seg } from "./base";
import { camera, SP } from "./Mapa";
import { Alerta, CasaRetorno, Calendario, Carrinho, Celular, Chama, Check, Engrenagem, Esgoto, Gota, IdCPF, Pessoa, Prato, Raio } from "./Icones";
import { Pop, Rotulo, Titulo, Vidro, usePop } from "./UI";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const lado: React.CSSProperties = { position: "absolute", right: 110, top: 0, bottom: 150, width: 820, display: "flex", flexDirection: "column", justifyContent: "center", gap: 28 };

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
  <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 120 }}>
    <Titulo texto="O dinheiro *volta?*" size={120} de={f(0.9)} />
  </AbsoluteFill>
);

/** s03 — contador 70 milhões + cashback tributário */
export const C03: React.FC = () => {
  const frame = useCurrentFrame();
  const n = interpolate(frame, [f(0.6), f(3.2)], [0, 70], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill>
      <div style={lado}>
        <Vidro de={f(0.3)}>
          <Rotulo>A partir de janeiro de 2027</Rotulo>
          <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 150, color: COR.ouro, lineHeight: 1, marginTop: 8 }}>
            {Math.round(n)} <span style={{ fontSize: 80 }}>MILHÕES</span>
          </div>
          <Rotulo size={34} cor={COR.branco}>de brasileiros</Rotulo>
          <div style={{ display: "flex", gap: 6, marginTop: 22, flexWrap: "wrap", width: 700 }}>
            {Array.from({ length: 35 }).map((_, i) => {
              const o = interpolate(frame, [f(0.8) + i * 2, f(0.8) + i * 2 + 6], [0, 1], clamp);
              return (
                <div key={i} style={{ opacity: o, transform: `scale(${0.5 + 0.5 * o})` }}>
                  <Pessoa size={26} cor={i % 5 === 0 ? COR.ouro : "rgba(255,255,255,0.85)"} />
                </div>
              );
            })}
          </div>
        </Vidro>
        <Vidro de={f(5.6)} style={{ display: "flex", alignItems: "center", gap: 30, padding: "26px 40px" }}>
          <Pop de={f(5.8)}>
            <CasaRetorno size={110} />
          </Pop>
          <Titulo texto="Cashback *tributário*" size={58} de={f(6)} />
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s04 — peso do imposto: quem ganha menos x quem ganha mais */
export const C04: React.FC = () => {
  const frame = useCurrentFrame();
  const b1 = interpolate(frame, [f(1.2), f(2.6)], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const b2 = interpolate(frame, [f(2.0), f(3.2)], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const Barra: React.FC<{ p: number; alt: number; cor: string; rot: string }> = ({ p, alt, cor, rot }) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, width: 280 }}>
      <div style={{ height: 380, display: "flex", alignItems: "flex-end" }}>
        <div style={{ width: 150, height: alt * p, background: cor, borderRadius: "14px 14px 4px 4px", boxShadow: `0 0 40px ${cor}66` }} />
      </div>
      <Rotulo size={26} cor={COR.branco} style={{ textAlign: "center" }}>{rot}</Rotulo>
    </div>
  );
  return (
    <AbsoluteFill>
      <div style={lado}>
        <Vidro de={f(0.2)}>
          <Rotulo>Peso do imposto no orçamento</Rotulo>
          <div style={{ display: "flex", justifyContent: "space-around", marginTop: 26 }}>
            <Barra p={b1} alt={360} cor={COR.ouro} rot="Quem ganha menos" />
            <Barra p={b2} alt={140} cor="rgba(255,255,255,0.55)" rot="Quem ganha mais" />
          </div>
          <div style={{ marginTop: 22, opacity: interpolate(frame, [f(4.2), f(4.8)], [0, 1], clamp) }}>
            <Titulo texto="Meta: *diminuir a desigualdade*" size={40} de={f(4.2)} />
          </div>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s05 — nota fiscal: não é a compra, é o imposto */
export const C05: React.FC = () => {
  const frame = useCurrentFrame();
  const risco = interpolate(frame, [f(1.0), f(1.5)], [0, 1], clamp);
  const brilho = interpolate(frame, [f(2.3), f(2.8)], [0, 1], clamp);
  const linha = (a: string, b: string, extra?: React.CSSProperties) => (
    <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "monospace", fontSize: 30, color: "#222", padding: "6px 0", ...extra }}>
      <span>{a}</span>
      <span>{b}</span>
    </div>
  );
  return (
    <AbsoluteFill style={{ background: "rgba(0,0,0,0.45)", flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 90, paddingBottom: 120 }}>
      <Pop de={f(0.1)} dy={80}>
        <div style={{ width: 520, background: "#f4f1ea", padding: "34px 40px", borderRadius: 6, boxShadow: "0 30px 80px rgba(0,0,0,0.7)", transform: "rotate(-3deg)" }}>
          <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 30, textAlign: "center", color: "#222" }}>NOTA FISCAL</div>
          <div style={{ borderTop: "3px dashed #999", margin: "14px 0" }} />
          {linha("ARROZ 5KG", "R$ 30,00")}
          {linha("FEIJÃO 1KG", "R$ 9,00")}
          {linha("ÓLEO 900ML", "R$ 8,00")}
          {linha("OUTROS", "R$ 53,00")}
          <div style={{ borderTop: "3px dashed #999", margin: "14px 0" }} />
          <div style={{ position: "relative" }}>
            {linha("TOTAL", "R$ 100,00", { fontWeight: 900, fontSize: 34 })}
            <div style={{ position: "absolute", left: -10, top: "50%", height: 6, width: `${risco * 105}%`, background: COR.vermelho, transform: "rotate(-4deg)" }} />
          </div>
          <div style={{ background: `rgba(245,197,66,${brilho})`, boxShadow: `0 0 ${40 * brilho}px rgba(245,197,66,${brilho})`, borderRadius: 6, padding: "0 10px", marginTop: 6 }}>
            {linha("IMPOSTOS", "R$ XX,XX", { fontWeight: 900 })}
          </div>
          <div style={{ fontFamily: FONTE, fontSize: 16, color: "#888", marginTop: 12, textAlign: "center" }}>VALORES ILUSTRATIVOS</div>
        </div>
      </Pop>
      <div style={{ width: 900 }}>
        <Titulo texto="Não é a compra." size={78} de={f(0.9)} />
        <Titulo texto="É o *imposto.*" size={110} de={f(2.4)} style={{ marginTop: 10 }} />
      </div>
    </AbsoluteFill>
  );
};

/** s06 — contas com 100% da CBS */
export const C06: React.FC = () => {
  const itens: [React.ReactNode, string][] = [
    [<Gota size={92} />, "Água"],
    [<Raio size={92} />, "Energia"],
    [<Esgoto size={92} />, "Esgoto"],
    [<Chama size={92} />, "Gás canalizado"],
    [<Celular size={92} />, "Telefonia"],
  ];
  const tempos = [0.7, 1.15, 1.6, 2.1, 2.9];
  return (
    <AbsoluteFill>
      <div style={lado}>
        <Vidro de={f(0.2)}>
          <Rotulo>Contas essenciais</Rotulo>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 26 }}>
            {itens.map(([ic, nome], i) => (
              <Pop key={nome} de={f(tempos[i])}>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10, width: 140 }}>
                  {ic}
                  <Rotulo size={18} cor={COR.branco} style={{ textAlign: "center", letterSpacing: 1 }}>{nome}</Rotulo>
                </div>
              </Pop>
            ))}
          </div>
          <div style={{ marginTop: 34, display: "flex", alignItems: "baseline", gap: 22 }}>
            <Titulo texto="*100%*" size={140} de={f(4.4)} />
            <Titulo texto="da CBS de volta" size={46} de={f(4.7)} />
          </div>
          <Rotulo size={22} style={{ marginTop: 10, opacity: 0.8 }}>CBS = novo imposto federal sobre consumo</Rotulo>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s07 — outras compras: 20% */
export const C07: React.FC = () => {
  const frame = useCurrentFrame();
  const a = interpolate(frame, [f(0.3), f(1.0)], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const b = interpolate(frame, [f(1.6), f(2.2)], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const Linha: React.FC<{ p: number; v: number; rot: string; cor: string; icone: React.ReactNode }> = ({ p, v, rot, cor, icone }) => (
    <div style={{ display: "flex", alignItems: "center", gap: 22, marginTop: 22 }}>
      <div style={{ width: 90 }}>{icone}</div>
      <div style={{ flex: 1 }}>
        <Rotulo size={22} cor={COR.branco}>{rot}</Rotulo>
        <div style={{ height: 46, marginTop: 8, background: "rgba(255,255,255,0.08)", borderRadius: 10, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${v * p}%`, background: cor, borderRadius: 10 }} />
        </div>
      </div>
      <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 60, color: cor, width: 160, textAlign: "right" }}>{Math.round(v * p)}%</div>
    </div>
  );
  return (
    <AbsoluteFill>
      <div style={lado}>
        <Vidro de={f(0)}>
          <Rotulo>Devolução da CBS</Rotulo>
          <Linha p={a} v={100} rot="Contas essenciais" cor={COR.verde} icone={<Raio size={80} />} />
          <Linha p={b} v={20} rot="Outras compras elegíveis" cor={COR.ouro} icone={<Carrinho size={80} />} />
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s08 — quebra histórica: 1789, a Derrama (pergaminho sépia + Ken Burns) */
export const C08: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const kb = interpolate(frame, [0, dur], [1.0, 1.18]);
  const px = interpolate(frame, [0, dur], [0, -60]);
  const entrada = interpolate(frame, [0, 10], [0, 1], clamp);
  const barras = Array.from({ length: 5 });
  return (
    <AbsoluteFill style={{ opacity: entrada, background: "#1a120a" }}>
      <AbsoluteFill style={{ transform: `scale(${kb}) translateX(${px}px)`, transformOrigin: "60% 50%" }}>
        {/* papel */}
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #e6d3a8 0%, #cdb17c 45%, #8d6a3a 100%)" }} />
        <svg width={W} height={H} style={{ position: "absolute", inset: 0, mixBlendMode: "multiply", opacity: 0.55 }}>
          <filter id="papel">
            <feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves={4} seed={3} />
            <feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.32  0 0 0 0 0.18  0 0 0 0.9 0" />
          </filter>
          <rect width={W} height={H} filter="url(#papel)" />
        </svg>
        {/* mapa antigo de Minas: estado desenhado a nanquim */}
        <MapaAntigo />
        {/* rosa dos ventos */}
        <svg width={220} height={220} viewBox="-110 -110 220 220" style={{ position: "absolute", left: 110, bottom: 190, opacity: 0.75 }}>
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

      {/* textos fixos (não sofrem Ken Burns) */}
      <div style={{ position: "absolute", left: 110, top: 90 }}>
        <div style={{ fontFamily: "Playfair Display", fontWeight: 900, fontSize: 190, color: "#3b2610", lineHeight: 0.9, opacity: interpolate(frame, [f(0.8), f(1.6)], [0, 1], clamp) }}>1789</div>
        <div style={{ fontFamily: "Playfair Display", fontStyle: "italic", fontWeight: 700, fontSize: 64, color: "#5a3a17", opacity: interpolate(frame, [f(4.0), f(4.8)], [0, 1], clamp) }}>
          A Derrama
        </div>
      </div>
      {/* o quinto: 1 de cada 5 barras de ouro para a Coroa */}
      <div style={{ position: "absolute", right: 90, top: 330, width: 560, padding: "26px 30px", background: "rgba(240,225,190,0.82)", border: "2px solid #6b4c26", borderRadius: 8, boxShadow: "0 10px 30px rgba(40,20,0,0.35)", opacity: interpolate(frame, [f(2.0), f(2.8)], [0, 1], clamp) }}>
        <div style={{ fontFamily: "Playfair Display", fontWeight: 900, fontSize: 46, color: "#3b2610" }}>O Quinto</div>
        <div style={{ display: "flex", gap: 16, marginTop: 18 }}>
          {barras.map((_, i) => {
            const coroa = i === 4;
            const lev = coroa ? interpolate(frame, [f(3.0), f(3.8)], [0, -40], { ...clamp, easing: Easing.out(Easing.back(2)) }) : 0;
            return (
              <div key={i} style={{ transform: `translateY(${lev}px)`, display: "flex", flexDirection: "column", alignItems: "center" }}>
                <svg width={88} height={53} viewBox="0 0 100 60">
                  <path d="M14 8 H86 L98 52 H2 Z" fill={coroa ? "#E8B53A" : "#a88a55"} stroke="#4a3218" strokeWidth={3} />
                  <path d="M20 14 H80" stroke={coroa ? "#FFE7A0" : "#c9ad7a"} strokeWidth={4} />
                </svg>
              </div>
            );
          })}
        </div>
        <div style={{ fontFamily: "Playfair Display", fontStyle: "italic", fontWeight: 700, fontSize: 30, color: "#4a3218", marginTop: 14 }}>
          1/5 de todo o ouro ia para a Coroa
        </div>
        <div style={{ fontFamily: FONTE, fontWeight: 800, fontSize: 24, color: "#7a2a12", marginTop: 6, letterSpacing: 1, opacity: interpolate(frame, [f(5.4), f(6.0)], [0, 1], clamp) }}>
          1/5 = 20%. COINCIDÊNCIA?
        </div>
      </div>

      {/* granulação de filme + vinheta + leve flicker */}
      <svg width={W} height={H} style={{ position: "absolute", inset: 0, opacity: 0.22, mixBlendMode: "overlay" }}>
        <filter id="grao">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={1} seed={frame % 12} />
        </filter>
        <rect width={W} height={H} filter="url(#grao)" />
      </svg>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 35%, rgba(20,10,0,0.85) 100%)", opacity: 0.9 + 0.1 * Math.sin(frame * 1.7) }} />
    </AbsoluteFill>
  );
};


const MapaAntigo: React.FC = () => {
  const frame = useCurrentFrame();
  const desenho = interpolate(frame, [0, f(3)], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const mg = geo.estados.find((e) => e.sigla === "MG")!;
  const vizinhos = geo.estados.filter((e) => ["SP", "RJ", "ES", "BA", "GO", "DF", "MS"].includes(e.sigla));
  // enquadra MG: aprox. lon -51..-39, lat -23..-14
  const [x0, y0] = [((-53 + 180) / 360) * 4096, ((90 - -12.5) / 180) * 2048];
  const [x1, y1] = [((-38 + 180) / 360) * 4096, ((90 - -24.5) / 180) * 2048];
  return (
    <svg width={900} height={720} viewBox={`${x0} ${y0} ${x1 - x0} ${y1 - y0}`} style={{ position: "absolute", left: 300, top: 250 }}>
      <defs>
        <pattern id="hachura" width={2} height={2} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1={0} y1={0} x2={0} y2={2} stroke="#6b4c26" strokeWidth={0.5} />
        </pattern>
      </defs>
      {vizinhos.map((e) => (
        <path key={e.sigla} d={e.d} fill="none" stroke="#6b4c26" strokeWidth={0.5} opacity={0.6 * desenho} />
      ))}
      <path d={mg.d} fill="url(#hachura)" stroke="#3b2610" strokeWidth={1.4} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - desenho} fillOpacity={interpolate(frame, [f(2.2), f(3.2)], [0, 0.55], clamp)} />
      <text x={((-45.5 + 180) / 360) * 4096} y={((90 - -18) / 180) * 2048} textAnchor="middle" fontFamily="Playfair Display" fontStyle="italic" fontWeight={700} fontSize={7} fill="#3b2610" opacity={interpolate(frame, [f(2.6), f(3.4)], [0, 1], clamp)}>
        Capitania de Minas Gerais
      </text>
      <circle cx={((-43.5 + 180) / 360) * 4096} cy={((90 - -20.38) / 180) * 2048} r={1.6} fill="#7a2a12" opacity={interpolate(frame, [f(3.4), f(3.8)], [0, 1], clamp)} />
      <text x={((-43.5 + 180) / 360) * 4096 + 3} y={((90 - -20.38) / 180) * 2048 + 6} fontFamily="Playfair Display" fontWeight={700} fontSize={4.5} fill="#7a2a12" opacity={interpolate(frame, [f(3.4), f(3.8)], [0, 1], clamp)}>
        Vila Rica
      </text>
    </svg>
  );
};

/** s09 — checklist de requisitos */
export const C09: React.FC = () => {
  const itens = ["Inscrito no Cadastro Único", "Renda de até ½ salário mínimo por pessoa", "CPF regular"];
  const t = [1.4, 2.9, 5.0];
  return (
    <AbsoluteFill>
      <div style={lado}>
        <Vidro de={f(0.1)}>
          <Titulo texto="Quem *recebe?*" size={64} de={f(0.2)} />
          <div style={{ marginTop: 26, display: "flex", flexDirection: "column", gap: 24 }}>
            {itens.map((it, i) => (
              <ItemCheck key={it} de={f(t[i])} texto={it} />
            ))}
          </div>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};
const ItemCheck: React.FC<{ de: number; texto: string }> = ({ de, texto }) => {
  const frame = useCurrentFrame();
  const s = usePop(de);
  const p = interpolate(frame, [de + 4, de + 12], [0, 1], clamp);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 24, opacity: 0.35 + 0.65 * Math.min(1, s), transform: `translateX(${(1 - s) * 30}px)` }}>
      <div style={{ width: 66, height: 66, borderRadius: 33, border: "3px solid rgba(255,255,255,0.4)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        {frame >= de && <Check size={60} p={p} />}
      </div>
      <div style={{ fontFamily: FONTE, fontWeight: 800, fontSize: 36, color: COR.branco, textTransform: "uppercase", lineHeight: 1.15 }}>{texto}</div>
    </div>
  );
};

/** s10 — automático + CPF na nota */
export const C10: React.FC = () => {
  const frame = useCurrentFrame();
  const enc = interpolate(frame, [f(4.0), f(4.9)], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  return (
    <AbsoluteFill>
      <div style={lado}>
        <Vidro de={f(0)} style={{ display: "flex", alignItems: "center", gap: 26, padding: "24px 40px" }}>
          <Pop de={f(0.3)}>
            <Engrenagem size={80} cor={COR.verde} />
          </Pop>
          <Titulo texto="Benefício *automático*" size={54} de={f(0.4)} />
        </Vidro>
        <Vidro de={f(1.8)}>
          <Rotulo>Mas não esqueça</Rotulo>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 20, height: 260 }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              <ItemCheck de={f(2.2)} texto="Cadastro atualizado" />
              <ItemCheck de={f(4.6)} texto="CPF na nota" />
            </div>
            <div style={{ position: "relative", width: 260, height: 260 }}>
              <div style={{ position: "absolute", right: 0, top: 10, width: 180, height: 240, background: "#f4f1ea", borderRadius: 6, padding: 16, boxShadow: "0 12px 30px rgba(0,0,0,0.5)" }}>
                <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 18, color: "#222" }}>NOTA FISCAL</div>
                {[0, 1, 2, 3].map((i) => (
                  <div key={i} style={{ height: 8, background: "#ccc", marginTop: 14, borderRadius: 4, width: `${90 - i * 12}%` }} />
                ))}
                <div style={{ marginTop: 20, fontFamily: FONTE, fontWeight: 900, fontSize: 18, color: enc > 0.95 ? "#1f8a4c" : "#999" }}>CPF: {enc > 0.95 ? "✓" : "____"}</div>
              </div>
              <div style={{ position: "absolute", left: interpolate(enc, [0, 1], [-300, 40]), top: interpolate(enc, [0, 1], [-60, 120]), transform: `rotate(${interpolate(enc, [0, 1], [-18, 0])}deg) scale(${interpolate(enc, [0, 1], [1, 0.55])})`, transformOrigin: "0 0", opacity: interpolate(frame, [f(3.6), f(3.9)], [0, 1], clamp) }}>
                <IdCPF size={220} />
              </div>
            </div>
          </div>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s11 — linha do tempo jan -> abr 2027 */
export const C11: React.FC = () => {
  const frame = useCurrentFrame();
  const linha = interpolate(frame, [f(1.2), f(3.4)], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  return (
    <AbsoluteFill>
      <div style={lado}>
        <Vidro de={f(0)}>
          <Rotulo>Calendário</Rotulo>
          <div style={{ position: "relative", height: 330, marginTop: 20 }}>
            <div style={{ position: "absolute", left: 80, right: 80, top: 120, height: 8, background: "rgba(255,255,255,0.15)", borderRadius: 4 }} />
            <div style={{ position: "absolute", left: 80, width: `calc(${linha} * (100% - 160px))`, top: 120, height: 8, background: COR.ouro, borderRadius: 4, boxShadow: `0 0 20px ${COR.ouro}` }} />
            {["FEV", "MAR"].map((m, i) => (
              <div key={m} style={{ position: "absolute", left: `calc(80px + ${(i + 1) / 3} * (100% - 160px) - 30px)`, top: 150, opacity: linha > (i + 1) / 3 ? 0.8 : 0.25, fontFamily: FONTE, fontWeight: 800, fontSize: 24, color: "#fff" }}>
                {m}
              </div>
            ))}
            <div style={{ position: "absolute", left: 0, top: 30 }}>
              <Pop de={f(0.3)}>
                <Calendario mes="JAN" ano="2027" size={170} />
              </Pop>
              <Rotulo size={22} cor={COR.branco} style={{ width: 200, textAlign: "center", marginTop: 6 }}>Começa o programa</Rotulo>
            </div>
            <div style={{ position: "absolute", right: 0, top: 30 }}>
              <Pop de={f(3.3)}>
                <Calendario mes="ABR" ano="2027" size={170} destaque />
              </Pop>
              <Rotulo size={22} cor={COR.ouro} style={{ width: 200, textAlign: "center", marginTop: 6 }}>1ª devolução em dinheiro</Rotulo>
            </div>
          </div>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s12 — R$ 10 bi ÷ 70 mi = ~R$ 12/mês */
export const C12: React.FC = () => {
  const frame = useCurrentFrame();
  const bi = interpolate(frame, [f(0.8), f(3.0)], [0, 10], { ...clamp, easing: Easing.out(Easing.cubic) });
  const div = interpolate(frame, [f(4.6), f(5.2)], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <div style={lado}>
        <Vidro de={f(0)}>
          <Rotulo>Estimativa para 2027</Rotulo>
          <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 112, color: COR.branco, lineHeight: 1.05, whiteSpace: "nowrap" }}>
            R$ {bi.toFixed(0)} <span style={{ fontSize: 62, color: COR.ouro }}>BILHÕES</span>
          </div>
          <div style={{ opacity: div, display: "flex", alignItems: "center", gap: 20, marginTop: 8 }}>
            <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 70, color: COR.cinza }}>÷</div>
            <div style={{ display: "flex", gap: 4 }}>
              {Array.from({ length: 14 }).map((_, i) => (
                <div key={i} style={{ opacity: interpolate(frame, [f(4.6) + i * 2, f(4.6) + i * 2 + 5], [0, 1], clamp) }}>
                  <Pessoa size={26} />
                </div>
              ))}
            </div>
            <Rotulo size={30} cor={COR.branco}>70 mi</Rotulo>
          </div>
          <div style={{ borderTop: `2px solid ${COR.borda}`, margin: "22px 0 14px" }} />
          <div style={{ display: "flex", alignItems: "baseline", gap: 18 }}>
            <Titulo texto="≈ *R$ 12*" size={120} de={f(7.0)} />
            <Titulo texto="por mês, por pessoa" size={38} de={f(7.6)} />
          </div>
          <Rotulo size={18} style={{ marginTop: 8, opacity: interpolate(frame, [f(8.0), f(8.5)], [0, 0.7], clamp) }}>
            Conta simples: R$ 10 bi ÷ 70 mi ÷ 12 meses ≈ R$ 11,90
          </Rotulo>
        </Vidro>
      </div>
    </AbsoluteFill>
  );
};

/** s13 — o desafio: sistemas */
export const C13: React.FC = () => (
  <AbsoluteFill>
    <div style={{ position: "absolute", left: 110, top: 110, display: "flex", alignItems: "center", gap: 26 }}>
      <Pop de={f(0.2)}>
        <Alerta size={110} />
      </Pop>
      <Titulo texto="O *desafio*" size={100} de={f(0.3)} />
    </div>
    <div style={{ position: "absolute", right: 120, top: 120, display: "flex", gap: 20 }}>
      <Pop de={f(2.0)}>
        <Engrenagem size={90} />
      </Pop>
      <Pop de={f(2.3)}>
        <Engrenagem size={60} cor={COR.vermelho} />
      </Pop>
    </div>
    <div style={{ position: "absolute", right: 120, top: 250 }}>
      <Rotulo size={26} cor={COR.branco} style={{ textAlign: "right" }}>
        Sistemas prontos?
        <br />
        <span style={{ color: COR.ouro }}>Dinheiro chegando?</span>
      </Rotulo>
    </div>
  </AbsoluteFill>
);

/** s14 — prometer ≠ entregar, à mesa de quem precisa */
export const C14: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 110, top: 110 }}>
        <Titulo texto="Prometer" size={92} de={f(0.3)} />
        <Titulo texto="≠ *entregar*" size={92} de={f(2.6)} />
      </div>
      <div style={{ position: "absolute", right: 140, bottom: 210 }}>
        <Pop de={f(3.8)}>
          <div style={{ position: "relative" }}>
            <Prato size={300} />
            {[0, 1, 2].map((i) => {
              const p = interpolate(frame, [f(4.6) + i * 6, f(5.2) + i * 6], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) });
              return (
                <svg key={i} width={46} height={46} viewBox="0 0 100 100" style={{ position: "absolute", left: 110 + i * 40, top: interpolate(p, [0, 1], [-260, 120]), opacity: p > 0 ? 1 : 0 }}>
                  <circle cx={50} cy={50} r={44} fill="#C98F12" />
                  <circle cx={50} cy={50} r={36} fill={COR.ouro} />
                </svg>
              );
            })}
          </div>
        </Pop>
        <Rotulo size={24} cor={COR.branco} style={{ textAlign: "center", marginTop: -40 }}>À mesa de quem precisa</Rotulo>
      </div>
    </AbsoluteFill>
  );
};

/** s15 — CTA */
export const C15: React.FC = () => {
  const s = usePop(f(5.0));
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", paddingBottom: 140, background: "rgba(0,0,0,0.35)" }}>
      <Titulo texto="Devolver parte do imposto" size={72} de={f(0.6)} style={{ textAlign: "center" }} />
      <Titulo texto="é *suficiente?*" size={100} de={f(1.6)} style={{ textAlign: "center" }} />
      <Titulo texto="Ou o básico deveria" size={62} de={f(3.0)} style={{ textAlign: "center", marginTop: 34 }} />
      <Titulo texto="*custar menos?*" size={120} de={f(4.4)} style={{ textAlign: "center" }} />
      <div style={{ marginTop: 34, transform: `scale(${s})`, background: COR.ouro, color: "#141a22", fontFamily: FONTE, fontWeight: 900, fontSize: 40, padding: "14px 38px", borderRadius: 50 }}>
        COMENTA AÍ ↓
      </div>
    </AbsoluteFill>
  );
};
