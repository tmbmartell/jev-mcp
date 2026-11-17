import React from "react";
import { AbsoluteFill, Html5Audio, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { SEGS, f, janela, seg } from "./base";
import { Mapa } from "./Mapa";
import { C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15 } from "./Cenas";
import { Cena, Legendas } from "./UI";

const CENAS: Record<string, React.FC<{ dur: number }>> = { s01: C01, s02: C02, s03: C03, s04: C04, s05: C05, s06: C06, s07: C07, s08: C08, s09: C09, s10: C10, s11: C11, s12: C12, s13: C13, s14: C14, s15: C15 };

// efeitos sonoros: [arquivo, id do trecho, segundos após o início do trecho, volume]
const SFX: [string, string, number, number][] = [
  ["whoosh_grave", "s01", -0.6, 0.7],
  ["pop", "s01", 2.2, 0.6],
  ["whoosh", "s01", 3.3, 0.4],
  ["moedas", "s01", 3.5, 0.45],
  ["rewind", "s02", 0.1, 0.45],
  ["moedas", "s02", 0.8, 0.4],
  ["riser", "s02", 1.7, 0.3],
  ["whoosh", "s03", 0.2, 0.4],
  ["clique", "s03", 0.7, 0.4], ["clique", "s03", 1.1, 0.4], ["clique", "s03", 1.5, 0.4], ["clique", "s03", 1.9, 0.4], ["clique", "s03", 2.4, 0.4], ["clique", "s03", 3.0, 0.4],
  ["pop", "s03", 5.8, 0.55],
  ["whoosh", "s04", 0.1, 0.35],
  ["hit", "s04", 1.2, 0.35],
  ["scratch", "s05", 0.85, 0.5],
  ["carimbo", "s05", 2.4, 0.5],
  ["whoosh", "s06", 0.1, 0.35],
  ["pop", "s06", 0.7, 0.5], ["pop", "s06", 1.15, 0.5], ["pop", "s06", 1.6, 0.5], ["pop", "s06", 2.1, 0.5], ["pop", "s06", 2.9, 0.5],
  ["moeda", "s06", 4.4, 0.45],
  ["whoosh", "s07", 0.2, 0.35],
  ["pop", "s07", 1.6, 0.5],
  ["whoosh_grave", "s08", -0.5, 0.55],
  ["moeda", "s08", 3.0, 0.35],
  ["whoosh", "s09", -0.2, 0.4],
  ["clique", "s09", 1.5, 0.6], ["clique", "s09", 3.0, 0.6], ["clique", "s09", 5.1, 0.6],
  ["pop", "s10", 0.3, 0.5],
  ["clique", "s10", 2.3, 0.6],
  ["whoosh", "s10", 3.9, 0.35],
  ["carimbo", "s10", 4.9, 0.55],
  ["pop", "s11", 0.3, 0.5],
  ["tique", "s11", 1.2, 0.5], ["tique", "s11", 2.2, 0.5],
  ["pop", "s11", 3.3, 0.55],
  ["calculadora", "s12", 0.8, 0.45],
  ["calculadora", "s12", 4.6, 0.45],
  ["hit", "s12", 7.0, 0.4],
  ["hit", "s13", 0.2, 0.45],
  ["pop", "s13", 2.0, 0.45],
  ["moedas", "s14", 4.6, 0.4],
  ["whoosh_grave", "s15", 0.3, 0.55],
  ["hit", "s15", 4.4, 0.5],
  ["pop", "s15", 5.0, 0.55],
];

const Trilha: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const s08 = seg("s08"), s14 = seg("s14");
  // trilha baixa sob a voz; abaixa na cena histórica e "respira" (para) no início do s14
  return (
    <Html5Audio
      src={staticFile("sfx/trilha.wav")}
      volume={(fr) => {
        const tt = fr / 30;
        let v = 0.2;
        v *= interpolate(tt, [s08.start - 0.5, s08.start, s08.start + s08.duration, s08.start + s08.duration + 0.6], [1, 0.45, 0.45, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        v *= interpolate(tt, [s14.start - 0.2, s14.start, s14.start + 0.6, s14.start + 1.2], [1, 0, 0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return v + 0 * t;
      }}
    />
  );
};

export const Video: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Mapa />
      {SEGS.map((s) => {
        const Comp = CENAS[s.id];
        const { from, dur } = janela(s.id);
        return (
          <Sequence key={s.id} from={from} durationInFrames={dur} name={`Cena ${s.id}`} layout="none">
            <Cena dur={dur}>
              <Comp dur={dur} />
            </Cena>
          </Sequence>
        );
      })}
      <Legendas />
      {/* voz */}
      {SEGS.map((s) => (
        <Sequence key={"v" + s.id} from={f(s.start)} name={`Voz ${s.id}`} layout="none">
          <Html5Audio src={staticFile(`voz/${s.id}.wav`)} />
        </Sequence>
      ))}
      <Trilha />
      {SFX.map(([arq, id, dt, vol], i) => (
        <Sequence key={"sfx" + i} from={Math.max(0, f(seg(id).start + dt))} name={`SFX ${arq}`} layout="none">
          <Html5Audio src={staticFile(`sfx/${arq}.wav`)} volume={vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
