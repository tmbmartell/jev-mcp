// ROTEIRO — o único arquivo (além de config.ts) que muda a cada vídeo.
// Este é o exemplo de referência: o primeiro Reel feito com o designe-01 (tema "ainda dá tempo de aprender tecnologia").
// Tempos em segundos, tirados de words.json. As cenas devem cobrir de 0 até o fim, sem buracos.
import { CARD, CIRCLE, END, FULL, Scene, Title, Feed, Compare, Stairs, Stack, Chips, Punch, End } from "./pecas";
import { VIDEO_SECONDS, END_SECONDS } from "./config";

export const SCENES: Scene[] = [
  { s: 0, e: 8.6, box: FULL(1) },
  { s: 8.6, e: 11.6, box: CARD, overlay: Title(null, "a grande maioria", "não se atualiza"), hideCaps: true },
  { s: 11.6, e: 20.0, box: FULL(1.14) },
  { s: 20.0, e: 27.5, box: CIRCLE, overlay: Feed(["01", "o caos"], "até quem é da área", "se perde",
      ["IA generativa", "novo modelo", "agentes", "automação", "app novo", "atualização", "no-code", "prompt", "chatbot", "API"], [0, 7]) },
  { s: 27.5, e: 37.4, box: FULL(1), badge: [{ s: 31.6, e: 36.4, kicker: "coisas que você nem", word: "imaginava" }] },
  { s: 37.4, e: 46.8, box: CARD, overlay: Title(null, "até quem está na ponta", "tem dificuldade", 100) },
  { s: 46.8, e: 53.3, box: FULL(1.14), badge: [{ s: 48.9, e: 53.0, kicker: "e o seu trabalho", word: "manual?" }] },
  { s: 53.3, e: 62.2, box: CIRCLE, overlay: Compare("talvez você não esteja", "tão atrasado", "você", "quem é como você", "mesmo nível") },
  { s: 62.2, e: 74.8, box: CIRCLE, overlay: Stairs(["02", "a escada"], "comparando com quem já é da área", "a diferença é grande", "você", "quem é da tecnologia") },
  { s: 74.8, e: 80.8, box: FULL(1), badge: [{ s: 78.2, e: 80.7, kicker: "passando", word: "rápido" }] },
  { s: 80.8, e: 91.2, box: CIRCLE, hideCaps: true, overlay: Stack(["03", "a virada"], "ainda", "dá tempo", [
      { s: 82.49, t: "de se atualizar" }, { s: 84.45, t: "de aprender coisas novas" }, { s: 86.75, t: "de construir um caminho" }]) },
  { s: 91.2, e: 105.0, box: FULL(1.14), badge: [{ s: 99.6, e: 104.6, kicker: "ferramentas", word: "de graça" }] },
  { s: 105.0, e: 116.0, box: FULL(1), badge: [{ s: 107.4, e: 110.8, kicker: "se sente", word: "perdido?" }, { s: 113.5, e: 115.9, kicker: "hoje é a", word: "IA" }] },
  { s: 116.0, e: 127.6, box: CIRCLE, overlay: Stairs(null, "IA daqui, IA de lá…", "tanto faz", "todo mundo", "quem é da tecnologia", true, "todo mundo no mesmo degrau") },
  { s: 127.6, e: 132.6, box: FULL(1.14) },
  { s: 132.6, e: 138.8, box: CARD, overlay: Title(["04", "o recado"], "esse é o momento", "aproveita") },
  { s: 138.8, e: 157.3, box: FULL(1), badge: [{ s: 147.9, e: 150.3, kicker: "", word: "acorda!" }, { s: 150.4, e: 153.0, kicker: "tem", word: "automação" }] },
  { s: 157.3, e: 163.0, box: CIRCLE, overlay: Chips("é como aprender", "uma nova língua", [
      { s: 160.03, t: "Português" }, { s: 161.13, t: "Inglês" }, { s: 161.67, t: "Matemática" }, { s: 162.57, t: "Ciência" }], "+ Tecnologia") },
  { s: 163.0, e: 172.0, box: FULL(1.14), badge: [{ s: 167.6, e: 171.6, kicker: "não deixe de", word: "seguir" }] },
  { s: 172.0, e: 181.4, box: FULL(1) },
  { s: 181.4, e: VIDEO_SECONDS, box: CARD, overlay: Punch("tarefa repetitiva?", "já tem um robô fazendo", "e você nem sabe", 187.83) },
  { s: VIDEO_SECONDS, e: VIDEO_SECONDS + END_SECONDS, box: END, hideCaps: true, overlay: End("não fica pra trás", "segue a gente", "todo dia tem coisa nova por aqui") },
];
