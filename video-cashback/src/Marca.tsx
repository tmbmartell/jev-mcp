import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { COR, FONTE, f, seg } from "./base";
import { Pop, usePop } from "./UI";

/**
 * IDENTIDADE "O CÓDIGO PÚBLICO"
 * - Wordmark: chaves de código em dourado envolvendo o nome { O CÓDIGO PÚBLICO }
 * - Assinatura fixa (canto superior) durante todo o vídeo
 * - Encerramento obrigatório: seguir + compartilhar com quem precisa saber
 */
export const HANDLE = "@ocodigopublico";
export const NOME = "O Código Público";

export const Wordmark: React.FC<{ size?: number }> = ({ size = 60 }) => (
  <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: size, color: COR.branco, textTransform: "uppercase", letterSpacing: -1, whiteSpace: "nowrap", lineHeight: 1 }}>
    <span style={{ color: COR.ouro }}>{"{ "}</span>
    O Código <span style={{ color: COR.ouro }}>Público</span>
    <span style={{ color: COR.ouro }}>{" }"}</span>
  </div>
);

/** Assinatura discreta no topo, presente do início ao fim (some no encerramento). */
export const Assinatura: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const fim = seg("s16").start;
  const o = interpolate(t, [0.3, 1.0, fim - 0.3, fim], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 70, display: "flex", justifyContent: "center", opacity: o * 0.85, pointerEvents: "none" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, background: "rgba(0,0,0,0.45)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 40, padding: "8px 22px 8px 14px", backdropFilter: "blur(8px)" }}>
        <div style={{ width: 34, height: 34, borderRadius: 17, background: COR.ouro, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONTE, fontWeight: 900, fontSize: 17, color: "#111" }}>{"{}"}</div>
        <div style={{ fontFamily: FONTE, fontWeight: 800, fontSize: 26, color: "#fff", letterSpacing: 0.5 }}>{HANDLE}</div>
      </div>
    </div>
  );
};

const Botao: React.FC<{ de: number; children: React.ReactNode; cor: string; texto: string; toque: number }> = ({ de, children, cor, texto, toque }) => {
  const frame = useCurrentFrame();
  const s = usePop(de);
  // "toque" simulado: o botão afunda e brilha
  const tap = interpolate(frame, [toque, toque + 4, toque + 10], [1, 0.9, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const brilho = interpolate(frame, [toque, toque + 4, toque + 24], [0, 1, 0.35], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ transform: `scale(${s * tap})`, opacity: Math.min(1, s * 1.5) }}>
      <div style={{ display: "flex", alignItems: "center", gap: 22, background: cor, borderRadius: 26, padding: "26px 40px", width: 760, boxShadow: `0 0 ${60 * brilho}px ${cor}, 0 20px 50px rgba(0,0,0,0.5)` }}>
        {children}
        <div style={{ fontFamily: FONTE, fontWeight: 900, fontSize: 50, color: "#111", textTransform: "uppercase", lineHeight: 1.05, whiteSpace: "pre-line" }}>{texto}</div>
      </div>
    </div>
  );
};

/** Cena final obrigatória: seguir + compartilhar. */
export const Encerramento: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const fundo = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  const brilho = interpolate(frame, [0, dur], [0, 1]);
  const linha = interpolate(frame, [f(0.2), f(1.0)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill style={{ opacity: fundo, background: `radial-gradient(ellipse at 50% 40%, #2b2006 0%, #05070b 72%)` }}>
      <AbsoluteFill
        style={{
          backgroundImage: "linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)",
          backgroundSize: "72px 72px",
          backgroundPosition: `0px ${(frame * 0.5) % 72}px`,
          WebkitMaskImage: "radial-gradient(ellipse at 50% 40%, black 20%, transparent 75%)",
        }}
      />
      {/* chaves gigantes de fundo */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 380, textAlign: "center", fontFamily: FONTE, fontWeight: 900, fontSize: 700, color: `rgba(245,197,66,${0.05 + 0.04 * brilho})`, letterSpacing: 40 }}>{"{ }"}</div>
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 300, gap: 0 }}>
        <Pop de={f(0.1)}>
          <Wordmark size={78} />
        </Pop>
        <div style={{ height: 6, width: 700 * linha, background: COR.ouro, borderRadius: 3, marginTop: 26, boxShadow: `0 0 20px ${COR.ouro}` }} />
        <Pop de={f(0.5)} style={{ marginTop: 26 }}>
          <div style={{ fontFamily: FONTE, fontWeight: 800, fontSize: 44, color: COR.cinza }}>{HANDLE}</div>
        </Pop>
        <div style={{ display: "flex", flexDirection: "column", gap: 34, marginTop: 110 }}>
          <Botao de={f(0.7)} toque={f(1.4)} cor={COR.ouro} texto="Siga o perfil">
            <svg width={70} height={70} viewBox="0 0 100 100">
              <circle cx="40" cy="32" r="18" fill="#111" />
              <path d="M8 90 a32 32 0 0 1 64 0 Z" fill="#111" />
              <path d="M80 30 v30 M65 45 h30" stroke="#111" strokeWidth={10} strokeLinecap="round" />
            </svg>
          </Botao>
          <Botao de={f(1.6)} toque={f(2.6)} cor="#ffffff" texto={"Envie para quem\nprecisa saber"}>
            <svg width={70} height={70} viewBox="0 0 100 100">
              <path d="M6 46 L94 8 L66 92 L48 58 Z" fill="#111" />
              <path d="M48 58 L94 8" stroke="#fff" strokeWidth={5} />
            </svg>
          </Botao>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};


