import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts, SAFE } from "../theme";
import { company, products } from "../data";
import { Headline, Kicker } from "../ui/Text";
import { ProductIllustration } from "../ui/Products";
import { MediaSlot } from "../MediaSlot";

export const Scene03Products: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${colors.white} 0%, #E6EAF0 100%)` }}>
      <div style={{ position: "absolute", left: SAFE.x, top: SAFE.y, display: "flex", flexDirection: "column", gap: 20 }}>
        <Kicker start={2} color={colors.navy}>
          Produtos
        </Kicker>
        <Headline start={6} size={72} color={colors.navy} style={{ width: 1120 }}>
          Qualidade de norma para obras, revendas e prefeituras
        </Headline>
      </div>
      <div style={{ position: "absolute", left: SAFE.x, right: SAFE.x, top: 400, display: "flex", gap: 40 }}>
        {products.map((p, i) => {
          const s = 22 + i * 12;
          const t = interpolate(frame, [s, s + 26], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          });
          const float = Math.sin((frame + i * 25) / 22) * 6;
          return (
            <div
              key={p.id}
              style={{
                flex: 1,
                height: 520,
                background: colors.white,
                borderRadius: 24,
                boxShadow: "0 24px 60px rgba(11,37,69,0.18)",
                borderTop: `10px solid ${colors.yellow}`,
                padding: "26px 36px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 8,
                opacity: t,
                translate: `0px ${(1 - t) * 60}px`,
                scale: String(0.9 + 0.1 * t),
              }}
            >
              <div style={{ translate: `0px ${float}px` }}>
                <ProductIllustration id={p.id} size={330} />
              </div>
              <div style={{ fontFamily: fonts.heading, fontWeight: 900, fontSize: 54, color: colors.navy, marginTop: 6 }}>{p.title}</div>
              <div style={{ fontFamily: fonts.body, fontWeight: 700, fontSize: 32, color: colors.red }}>{p.subtitle}</div>
              <div style={{ fontFamily: fonts.body, fontWeight: 500, fontSize: 28, color: colors.steelDark }}>{p.detail}</div>
            </div>
          );
        })}
      </div>
      {/* foto de referência (pátio de blocos) no canto */}
      <div
        style={{
          position: "absolute",
          right: SAFE.x,
          top: SAFE.y - 10,
          width: 420,
          height: 220,
          borderRadius: 18,
          overflow: "hidden",
          boxShadow: "0 16px 40px rgba(11,37,69,0.25)",
          opacity: interpolate(frame, [10, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <MediaSlot id="cat:produtos" />
      </div>
      <div
        style={{
          position: "absolute",
          left: SAFE.x,
          bottom: 50,
          fontFamily: fonts.body,
          fontWeight: 700,
          fontSize: 30,
          letterSpacing: 2,
          color: colors.navy,
          opacity: interpolate(frame, [60, 80], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        {company.standards}
      </div>
    </AbsoluteFill>
  );
};
