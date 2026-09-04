import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";

type Props = {
  to: number;
  from?: number;
  startFrame?: number;
  durationInFrames?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  style?: React.CSSProperties;
};

const formatBR = (n: number, decimals: number) =>
  n.toLocaleString("pt-BR", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

export const CountUp: React.FC<Props> = ({
  to,
  from = 0,
  startFrame = 0,
  durationInFrames = 50,
  decimals = 0,
  prefix = "",
  suffix = "",
  style,
}) => {
  const frame = useCurrentFrame();
  const value = interpolate(frame, [startFrame, startFrame + durationInFrames], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <span style={{ fontVariantNumeric: "tabular-nums", ...style }}>
      {prefix}
      {formatBR(value, decimals)}
      {suffix}
    </span>
  );
};
