import { Composition, Still } from "remotion";
import "./base";
import { FPS, H, TOTAL, W } from "./base";
import { Capa } from "./Capa";
import { Video } from "./Video";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="CashbackTributario" component={Video} durationInFrames={Math.ceil(TOTAL * FPS)} fps={FPS} width={W} height={H} />
    <Still id="Capa" component={Capa} width={W} height={H} />
  </>
);
