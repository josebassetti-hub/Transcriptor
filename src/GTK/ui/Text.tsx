import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts } from "../theme";

const ease = Easing.bezier(0.16, 1, 0.3, 1);

/** Entrada padrão: sobe 40px e aparece. */
export const useReveal = (start: number, duration = 18) => {
  const frame = useCurrentFrame();
  return {
    opacity: interpolate(frame, [start, start + duration], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: ease,
    }),
    translate: interpolate(frame, [start, start + duration], ["0px 40px", "0px 0px"], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: ease,
    }),
  };
};

export const Kicker: React.FC<{
  children: React.ReactNode;
  start?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ children, start = 0, color = colors.yellow, style }) => {
  const r = useReveal(start);
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 18,
        fontFamily: fonts.body,
        fontWeight: 700,
        fontSize: 30,
        letterSpacing: 6,
        textTransform: "uppercase",
        color,
        ...r,
        ...style,
      }}
    >
      <span style={{ width: 54, height: 8, background: color, borderRadius: 4 }} />
      {children}
    </div>
  );
};

export const Headline: React.FC<{
  children: React.ReactNode;
  start?: number;
  size?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ children, start = 6, size = 92, color = colors.white, style }) => {
  const r = useReveal(start);
  return (
    <div
      style={{
        fontFamily: fonts.heading,
        fontWeight: 900,
        fontSize: size,
        lineHeight: 1.04,
        letterSpacing: -1,
        color,
        ...r,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export const Body: React.FC<{
  children: React.ReactNode;
  start?: number;
  size?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ children, start = 12, size = 44, color = colors.concreteLight, style }) => {
  const r = useReveal(start);
  return (
    <div
      style={{
        fontFamily: fonts.body,
        fontWeight: 500,
        fontSize: size,
        lineHeight: 1.3,
        color,
        ...r,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Faixa inferior com fatos separados por pontos. */
export const FactBar: React.FC<{ items: string[]; start?: number; size?: number }> = ({ items, start = 20, size = 34 }) => {
  const r = useReveal(start);
  return (
    <div
      style={{
        display: "flex",
        gap: 28,
        alignItems: "center",
        flexWrap: "wrap",
        fontFamily: fonts.body,
        fontWeight: 700,
        fontSize: size,
        color: colors.white,
        ...r,
      }}
    >
      {items.map((t, i) => (
        <React.Fragment key={t}>
          {i > 0 && <span style={{ width: 12, height: 12, borderRadius: 6, background: colors.yellow }} />}
          <span>{t}</span>
        </React.Fragment>
      ))}
    </div>
  );
};

/** Rodapé discreto de contato. */
export const ContactFooter: React.FC<{ role: string; name: string; phone: string; start?: number }> = ({
  role,
  name,
  phone,
  start = 30,
}) => {
  const r = useReveal(start);
  return (
    <div
      style={{
        position: "absolute",
        left: 140,
        bottom: 60,
        display: "flex",
        alignItems: "center",
        gap: 18,
        fontFamily: fonts.body,
        fontSize: 30,
        color: colors.concreteLight,
        ...r,
      }}
    >
      <PhoneIcon size={34} color={colors.yellow} />
      <span style={{ fontWeight: 700, color: colors.white }}>{role}:</span>
      <span>{name}</span>
      <span style={{ fontWeight: 800, color: colors.yellow, letterSpacing: 1 }}>{phone}</span>
    </div>
  );
};

export const PhoneIcon: React.FC<{ size?: number; color?: string }> = ({ size = 40, color = colors.yellow }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path
      d="M6.6 2.8c.5-.5 1.3-.5 1.8 0l2.2 2.3c.5.5.5 1.3 0 1.8L9.3 8.2c-.3.3-.4.8-.1 1.2a13 13 0 0 0 5.4 5.4c.4.2.9.2 1.2-.1l1.3-1.3c.5-.5 1.3-.5 1.8 0l2.3 2.2c.5.5.5 1.3 0 1.8l-1.5 1.5c-1.3 1.3-3.3 1.6-5 .8A21 21 0 0 1 4.3 9.4c-.8-1.7-.5-3.7.8-5L6.6 2.8Z"
      fill={color}
    />
  </svg>
);
