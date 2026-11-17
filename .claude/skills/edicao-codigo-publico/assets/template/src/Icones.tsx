import React from "react";
import { COR } from "./base";

type P = { size?: number; cor?: string };

const Base: React.FC<P & { children: React.ReactNode; vb?: string }> = ({ size = 120, children, vb = "0 0 100 100" }) => (
  <svg width={size} height={size} viewBox={vb} style={{ overflow: "visible", filter: "drop-shadow(0 6px 10px rgba(0,0,0,0.5))" }}>
    {children}
  </svg>
);

export const Carrinho: React.FC<P> = ({ size, cor = COR.branco }) => (
  <Base size={size}>
    <path d="M8 18 H22 L32 64 H80 L90 30 H27" fill="none" stroke={cor} strokeWidth={7} strokeLinejoin="round" strokeLinecap="round" />
    <rect x="30" y="34" width="54" height="24" rx="3" fill={COR.ouro} opacity={0.9} />
    <circle cx="38" cy="80" r="8" fill={cor} />
    <circle cx="74" cy="80" r="8" fill={cor} />
  </Base>
);

export const Moeda: React.FC<P> = ({ size = 60 }) => (
  <Base size={size}>
    <circle cx="50" cy="50" r="44" fill="#D9A21B" />
    <circle cx="50" cy="50" r="36" fill={COR.ouro} stroke="#FFE59A" strokeWidth={3} />
    <text x="50" y="66" textAnchor="middle" fontSize="44" fontWeight={900} fill="#9A6A00" fontFamily="Montserrat">$</text>
  </Base>
);

export const CasaRetorno: React.FC<P> = ({ size }) => (
  <Base size={size}>
    <path d="M18 50 L50 22 L82 50 V84 H18 Z" fill={COR.branco} />
    <rect x="42" y="60" width="16" height="24" fill="#1d2633" />
    <path d="M14 30 A40 40 0 0 1 70 10" fill="none" stroke={COR.ouro} strokeWidth={6} strokeLinecap="round" />
    <path d="M62 2 L74 10 L62 18" fill="none" stroke={COR.ouro} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
  </Base>
);

export const Gota: React.FC<P> = ({ size }) => (
  <Base size={size}>
    <path d="M50 8 C50 8 18 48 18 64 A32 32 0 0 0 82 64 C82 48 50 8 50 8 Z" fill={COR.azul} />
    <path d="M34 64 A16 16 0 0 0 50 80" fill="none" stroke="#fff" strokeWidth={5} strokeLinecap="round" opacity={0.7} />
  </Base>
);

export const Raio: React.FC<P> = ({ size }) => (
  <Base size={size}>
    <path d="M58 4 L20 56 H46 L38 96 L80 40 H54 Z" fill={COR.ouro} />
  </Base>
);

export const Esgoto: React.FC<P> = ({ size }) => (
  <Base size={size}>
    <rect x="8" y="20" width="56" height="22" rx="4" fill="#9fb3c8" />
    <rect x="44" y="20" width="22" height="60" rx="4" fill="#9fb3c8" />
    <rect x="38" y="76" width="34" height="10" rx="3" fill="#c9d6e3" />
    <path d="M30 92 q10 -8 20 0 t20 0 t20 0" fill="none" stroke={COR.azul} strokeWidth={5} strokeLinecap="round" />
  </Base>
);

export const Chama: React.FC<P> = ({ size }) => (
  <Base size={size}>
    <path d="M50 4 C62 26 82 38 82 62 A32 32 0 0 1 18 62 C18 46 28 38 34 26 C38 40 46 42 46 42 C44 26 46 14 50 4 Z" fill="#FF8A2B" />
    <path d="M50 46 C58 58 66 62 66 72 A16 16 0 0 1 34 72 C34 62 44 58 50 46 Z" fill={COR.ouro} />
  </Base>
);

export const Celular: React.FC<P> = ({ size }) => (
  <Base size={size}>
    <rect x="26" y="4" width="48" height="92" rx="9" fill="#e8eef5" />
    <rect x="31" y="14" width="38" height="66" rx="3" fill="#1d2633" />
    <circle cx="50" cy="88" r="4" fill="#1d2633" />
    <path d="M38 40 a16 16 0 0 1 24 0 M43 47 a8 8 0 0 1 14 0" fill="none" stroke={COR.verde} strokeWidth={4} strokeLinecap="round" />
  </Base>
);

export const Check: React.FC<P & { p?: number }> = ({ size = 60, p = 1 }) => (
  <Base size={size}>
    <circle cx="50" cy="50" r="44" fill={COR.verde} opacity={0.95} />
    <path d="M28 52 L44 68 L74 34" fill="none" stroke="#0c1a0a" strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={80} strokeDashoffset={80 * (1 - p)} />
  </Base>
);

export const Engrenagem: React.FC<P> = ({ size, cor = COR.branco }) => (
  <Base size={size}>
    <g fill={cor}>
      {Array.from({ length: 8 }).map((_, i) => (
        <rect key={i} x="44" y="4" width="12" height="20" rx="2" transform={`rotate(${i * 45} 50 50)`} />
      ))}
      <circle cx="50" cy="50" r="30" />
    </g>
    <circle cx="50" cy="50" r="12" fill="#1d2633" />
  </Base>
);

export const Alerta: React.FC<P> = ({ size }) => (
  <Base size={size}>
    <path d="M50 6 L94 88 H6 Z" fill={COR.vermelho} stroke="#fff" strokeWidth={4} strokeLinejoin="round" />
    <rect x="45" y="34" width="10" height="30" rx="4" fill="#fff" />
    <circle cx="50" cy="75" r="6" fill="#fff" />
  </Base>
);

export const Prato: React.FC<P> = ({ size }) => (
  <Base size={size} vb="0 0 140 100">
    <rect x="0" y="78" width="140" height="10" rx="4" fill="#8a5a33" />
    <ellipse cx="70" cy="70" rx="52" ry="12" fill="#e8eef5" />
    <ellipse cx="70" cy="66" rx="34" ry="7" fill="#cfd8e3" />
    <path d="M52 62 q6 -14 18 -8 q10 -10 18 6" fill="#c98b3a" />
    <path d="M14 30 v34 M8 30 v12 q6 6 12 0 v-12" fill="none" stroke="#cfd8e3" strokeWidth={4} strokeLinecap="round" />
    <path d="M128 30 q-10 10 0 24 v10" fill="none" stroke="#cfd8e3" strokeWidth={4} strokeLinecap="round" />
  </Base>
);

export const Pessoa: React.FC<P> = ({ size = 40, cor = COR.branco }) => (
  <svg width={size} height={size * 1.6} viewBox="0 0 50 80">
    <circle cx="25" cy="13" r="11" fill={cor} />
    <path d="M6 76 V42 a19 19 0 0 1 38 0 V76 Z" fill={cor} />
  </svg>
);

export const Calendario: React.FC<P & { mes: string; ano: string; destaque?: boolean }> = ({ size = 150, mes, ano, destaque }) => (
  <Base size={size}>
    <rect x="6" y="14" width="88" height="80" rx="10" fill={destaque ? COR.ouro : "#e8eef5"} />
    <rect x="6" y="14" width="88" height="26" rx="10" fill={destaque ? "#C9871A" : "#566579"} />
    <rect x="24" y="4" width="8" height="20" rx="3" fill="#2a3442" />
    <rect x="68" y="4" width="8" height="20" rx="3" fill="#2a3442" />
    <text x="50" y="34" textAnchor="middle" fontSize="16" fontWeight={900} fill="#fff" fontFamily="Montserrat">{ano}</text>
    <text x="50" y="78" textAnchor="middle" fontSize="30" fontWeight={900} fill="#141a22" fontFamily="Montserrat">{mes}</text>
  </Base>
);

export const IdCPF: React.FC<P> = ({ size = 220 }) => (
  <svg width={size} height={size * 0.62} viewBox="0 0 160 100" style={{ filter: "drop-shadow(0 8px 14px rgba(0,0,0,0.5))" }}>
    <rect x="2" y="2" width="156" height="96" rx="10" fill="#e9f0f7" />
    <rect x="2" y="2" width="156" height="24" rx="10" fill="#1f8a4c" />
    <text x="12" y="20" fontSize="14" fontWeight={900} fill="#fff" fontFamily="Montserrat">CPF</text>
    <circle cx="36" cy="58" r="16" fill="#9fb3c8" />
    <rect x="62" y="42" width="80" height="8" rx="3" fill="#9fb3c8" />
    <rect x="62" y="58" width="60" height="8" rx="3" fill="#c9d6e3" />
    <text x="62" y="88" fontSize="11" fontWeight={800} fill="#33414f" fontFamily="Montserrat">000.000.000-00</text>
  </svg>
);
