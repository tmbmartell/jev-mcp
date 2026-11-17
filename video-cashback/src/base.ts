import { continueRender, delayRender, staticFile } from "remotion";
import tempos from "./tempos.json";

export const FPS = 30;
export const W = 1080;
export const H = 1920;

export const COR = {
  branco: "#FFFFFF",
  ouro: "#F5C542",
  verde: "#7CFC6A",
  vermelho: "#FF4D4D",
  azul: "#6EC3FF",
  vidro: "rgba(8,10,14,0.70)",
  borda: "rgba(255,255,255,0.14)",
  cinza: "rgba(255,255,255,0.65)",
};

export const FONTE = "Montserrat, sans-serif";
export const SERIFA = "'Playfair Display', serif";

export type Segmento = { id: string; text: string; start: number; duration: number };
export const SEGS = tempos.segments as Segmento[];
export const TOTAL = tempos.total;

export const f = (seg: number) => Math.round(seg * FPS);
export const seg = (id: string) => {
  const s = SEGS.find((x) => x.id === id);
  if (!s) throw new Error(id);
  return s;
};
/** Janela de uma cena: do início da fala até o início da próxima fala. */
export const janela = (id: string) => {
  const i = SEGS.findIndex((x) => x.id === id);
  const ini = SEGS[i].start;
  const fim = i < SEGS.length - 1 ? SEGS[i + 1].start : TOTAL;
  return { from: f(ini), dur: f(fim) - f(ini) };
};

// lon/lat -> pixel do mundo (mesma projeção da textura 4096x2048)
export const geoPx = (lon: number, lat: number): [number, number] => [
  ((lon + 180) / 360) * 4096,
  ((90 - lat) / 180) * 2048,
];

// ---------- fontes locais ----------
const fontes: [string, string, string, string][] = [
  ["Montserrat", "montserrat-latin-600-normal.woff2", "600", "normal"],
  ["Montserrat", "montserrat-latin-800-normal.woff2", "800", "normal"],
  ["Montserrat", "montserrat-latin-900-normal.woff2", "900", "normal"],
  ["Playfair Display", "playfair-display-latin-700-normal.woff2", "700", "normal"],
  ["Playfair Display", "playfair-display-latin-900-normal.woff2", "900", "normal"],
  ["Playfair Display", "playfair-display-latin-700-italic.woff2", "700", "italic"],
];
if (typeof document !== "undefined") {
  const h = delayRender("fontes");
  Promise.all(
    fontes.map(([fam, arq, weight, style]) =>
      new FontFace(fam, `url(${staticFile("fonts/" + arq)})`, { weight, style })
        .load()
        .then((ff) => document.fonts.add(ff)),
    ),
  )
    .then(() => continueRender(h))
    .catch((e) => {
      console.error(e);
      continueRender(h);
    });
}
