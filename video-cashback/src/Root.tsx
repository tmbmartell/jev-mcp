import { Composition } from "remotion";
import "./base";
import { FPS, H, TOTAL, W } from "./base";
import { Video } from "./Video";

export const RemotionRoot: React.FC = () => (
  <Composition id="CashbackTributario" component={Video} durationInFrames={Math.ceil(TOTAL * FPS)} fps={FPS} width={W} height={H} />
);
