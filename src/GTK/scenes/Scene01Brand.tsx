import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { Logo } from "../Logo";
import { MediaSlot } from "../MediaSlot";
import { colors, fonts } from "../theme";
import { company } from "../data";

const DUST = Array.from({ length: 40 }, (_, i) => ({
  x: (i * 977) % 1920,
  y: (i * 613) % 1080,
  r: 2 + ((i * 7) % 5),
  v: 0.4 + ((i * 3) % 7) / 10,
}));

export const Scene01Brand: React.FC = () => {
  const frame = useCurrentFrame();
  const bgOpacity = interpolate(frame, [0, 30], [0, 0.32], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const tagline = interpolate(frame, [70, 95], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const lineW = interpolate(frame, [60, 100], [0, 520], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <AbsoluteFill style={{ background: `radial-gradient(1200px 800px at 50% 45%, ${colors.navy2} 0%, ${colors.navyDeep} 70%, #030A14 100%)` }}>
      <AbsoluteFill style={{ opacity: bgOpacity, filter: "saturate(0.7)" }}>
        <MediaSlot id="video:xp350-operacao" trimSeconds={4} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(3,10,20,0.2) 0%, rgba(3,10,20,0.75) 100%)" }} />
      {/* partículas de pó de cimento */}
      <AbsoluteFill>
        {DUST.map((p, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              left: p.x,
              top: p.y,
              width: p.r,
              height: p.r,
              borderRadius: p.r,
              background: colors.yellow,
              opacity: 0.25 + ((i * 13) % 6) / 20,
              translate: `${Math.sin((frame + i * 20) / 40) * 12}px ${-frame * p.v}px`,
            }}
          />
        ))}
      </AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: 36 }}>
        <Logo variant="horizontal" height={260} animateFrom={6} />
        <div style={{ width: lineW, height: 6, background: colors.yellow, borderRadius: 3 }} />
        <div
          style={{
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: 48,
            letterSpacing: 2,
            color: colors.concreteLight,
            opacity: tagline,
            translate: `0px ${(1 - tagline) * 30}px`,
          }}
        >
          {company.tagline}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
