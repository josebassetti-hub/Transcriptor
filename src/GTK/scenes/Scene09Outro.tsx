import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts } from "../theme";
import { company } from "../data";
import { Logo } from "../Logo";
import { MediaSlot } from "../MediaSlot";
import { PhoneIcon } from "../ui/Text";

export const Scene09Outro: React.FC<{ contactName: string; contactRole: string; contactPhone: string }> = ({ contactName, contactRole, contactPhone }) => {
  const frame = useCurrentFrame();
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  const card = interpolate(frame, [40, 66], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const foot = interpolate(frame, [70, 90], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: colors.navyDeep }}>
      <AbsoluteFill style={{ opacity: 0.22, filter: "blur(2px) saturate(0.6)" }}>
        <MediaSlot id="video:fabrica-tour" trimSeconds={60} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "radial-gradient(1000px 700px at 50% 40%, rgba(11,37,69,0.2) 0%, rgba(3,10,20,0.9) 100%)" }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", gap: 40 }}>
        <Logo variant="vertical" height={400} animateFrom={0} />
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 26,
            padding: "22px 44px",
            background: colors.yellow,
            borderRadius: 18,
            opacity: card,
            translate: `0px ${(1 - card) * 30}px`,
            boxShadow: "0 20px 60px rgba(0,0,0,0.45)",
          }}
        >
          <PhoneIcon size={54} color={colors.navyDeep} />
          <div style={{ fontFamily: fonts.body, color: colors.navyDeep }}>
            <div style={{ fontWeight: 700, fontSize: 28, letterSpacing: 4, textTransform: "uppercase" }}>{contactRole}</div>
            <div style={{ display: "flex", gap: 22, alignItems: "baseline" }}>
              <span style={{ fontWeight: 700, fontSize: 40 }}>{contactName}</span>
              <span style={{ fontFamily: fonts.heading, fontWeight: 900, fontSize: 50 }}>{contactPhone}</span>
            </div>
          </div>
        </div>
        <div style={{ fontFamily: fonts.body, fontWeight: 500, fontSize: 28, color: colors.concreteLight, opacity: foot, textAlign: "center", lineHeight: 1.5 }}>
          {company.legalName} · CNPJ {company.cnpj}
          <br />
          {company.address} · {company.city}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
