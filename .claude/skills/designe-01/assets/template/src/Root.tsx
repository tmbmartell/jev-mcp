import React from "react";
import { Composition } from "remotion";
import { Reel, TOTAL_FRAMES } from "./kit";

export const Root: React.FC = () => (
  <Composition id="Reel" component={Reel} durationInFrames={TOTAL_FRAMES} fps={30} width={1080} height={1920} />
);
