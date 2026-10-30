import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const C = {
  bg1: "#12061A",
  bg2: "#2B0A30",
  magenta: "#FF2E8A",
  pink: "#FFB3D6",
  cream: "#FFF4EC",
  dim: "rgba(255,244,236,0.55)",
};

export const SANS = "Jakarta";
export const SERIF = "Playfair";

export const fontsReady = Promise.all([
  loadFont({ family: SANS, url: staticFile("plus-jakarta-sans-latin-500-normal.woff2"), weight: "500" }),
  loadFont({ family: SANS, url: staticFile("plus-jakarta-sans-latin-800-normal.woff2"), weight: "800" }),
  loadFont({ family: SERIF, url: staticFile("playfair-display-latin-600-italic.woff2"), weight: "600", style: "italic" }),
  loadFont({ family: SERIF, url: staticFile("playfair-display-latin-700-italic.woff2"), weight: "700", style: "italic" }),
]);
