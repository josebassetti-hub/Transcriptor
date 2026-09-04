import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts } from "./theme";

type Props = {
  variant?: "horizontal" | "vertical" | "mark";
  mono?: "none" | "light" | "dark";
  /** altura total em px */
  height?: number;
  /** frame em que a animação de montagem começa; undefined = estático */
  animateFrom?: number;
};

const spring = Easing.spring({ damping: 200 });

/**
 * Símbolo: bloco de concreto vazado em isometria com a letra G recortada na face superior.
 * viewBox 0 0 200 200. Quando animado, as três faces "caem" e encaixam.
 */
const Mark: React.FC<{ size: number; mono: Props["mono"]; animateFrom?: number }> = ({ size, mono, animateFrom }) => {
  const frame = useCurrentFrame();
  const topC = mono === "light" ? "#FFFFFF" : mono === "dark" ? colors.navy : colors.yellow;
  const leftC = mono === "light" ? "#D9DEE6" : mono === "dark" ? colors.navy2 : colors.navy;
  const rightC = mono === "light" ? "#AEB6C2" : mono === "dark" ? colors.navyDeep : colors.navy2;
  const holeC = mono === "light" ? "#0B2545" : mono === "dark" ? "#FFFFFF" : colors.navyDeep;
  const gC = mono === "light" ? "#0B2545" : mono === "dark" ? "#FFFFFF" : colors.navyDeep;

  const t = (delay: number) =>
    animateFrom === undefined
      ? 1
      : interpolate(frame, [animateFrom + delay, animateFrom + delay + 26], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: spring,
        });
  const drop = (delay: number, dy: number) => `translate(0 ${(1 - t(delay)) * dy})`;

  return (
    <svg width={size} height={size} viewBox="0 0 200 200" style={{ overflow: "visible" }}>
      {/* face esquerda */}
      <g opacity={t(0)} transform={drop(0, -60)}>
        <polygon points="20,80 100,120 100,190 20,150" fill={leftC} />
      </g>
      {/* face direita */}
      <g opacity={t(6)} transform={drop(6, -60)}>
        <polygon points="100,120 180,80 180,150 100,190" fill={rightC} />
      </g>
      {/* face superior com dois furos */}
      <g opacity={t(14)} transform={drop(14, -90)}>
        <polygon points="20,80 100,40 180,80 100,120" fill={topC} />
        <polygon points="52,80 92,60 118,73 78,93" fill={holeC} />
        <polygon points="96,102 136,82 162,95 122,115" fill={holeC} />
        {/* G desenhada na face superior (perspectiva isométrica via skew) */}
        <g transform="translate(100 80) scale(1 0.5) rotate(-45)" opacity={0.0}>
          <text fontFamily={fonts.heading} fontWeight={900} fontSize={70} textAnchor="middle" fill={gC} y={24}>
            G
          </text>
        </g>
      </g>
    </svg>
  );
};

export const Logo: React.FC<Props> = ({ variant = "horizontal", mono = "none", height = 120, animateFrom }) => {
  const frame = useCurrentFrame();
  const textC = mono === "light" ? "#FFFFFF" : mono === "dark" ? colors.navy : colors.white;
  const subC = mono === "light" ? "#FFFFFF" : mono === "dark" ? colors.navy2 : colors.yellow;
  const textT =
    animateFrom === undefined
      ? 1
      : interpolate(frame, [animateFrom + 26, animateFrom + 50], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        });

  if (variant === "mark") {
    return <Mark size={height} mono={mono} animateFrom={animateFrom} />;
  }

  const markSize = variant === "horizontal" ? height : height * 0.58;
  const gtkSize = variant === "horizontal" ? height * 0.62 : height * 0.3;
  const subSize = variant === "horizontal" ? height * 0.17 : height * 0.085;

  const text = (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: variant === "horizontal" ? "flex-start" : "center",
        justifyContent: "center",
        opacity: textT,
        translate: `${(1 - textT) * (variant === "horizontal" ? -30 : 0)}px ${(1 - textT) * (variant === "horizontal" ? 0 : 20)}px`,
        lineHeight: 1,
      }}
    >
      <div
        style={{
          fontFamily: fonts.heading,
          fontWeight: 900,
          fontSize: gtkSize,
          letterSpacing: gtkSize * 0.02,
          color: textC,
          lineHeight: 0.95,
        }}
      >
        GTK
      </div>
      <div
        style={{
          fontFamily: fonts.body,
          fontWeight: 700,
          fontSize: subSize,
          letterSpacing: subSize * 0.42,
          color: subC,
          marginTop: subSize * 0.55,
          paddingLeft: variant === "horizontal" ? 4 : 0,
        }}
      >
        PRÉ-MOLDADOS
      </div>
    </div>
  );

  return (
    <div
      style={{
        display: "flex",
        flexDirection: variant === "horizontal" ? "row" : "column",
        alignItems: "center",
        gap: variant === "horizontal" ? height * 0.22 : height * 0.08,
        height: variant === "horizontal" ? height : undefined,
      }}
    >
      <Mark size={markSize} mono={mono} animateFrom={animateFrom} />
      {text}
    </div>
  );
};
