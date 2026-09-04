import React from "react";
import { AbsoluteFill } from "remotion";
import { Logo } from "./Logo";
import { colors } from "./theme";

/** Logomarca para exportação em PNG (fundo marinho ou transparente). */
export const LogoStill: React.FC<{ variant: "horizontal" | "vertical" | "mark"; background: "navy" | "white" | "transparent" }> = ({ variant, background }) => {
  const bg = background === "navy" ? colors.navyDeep : background === "white" ? "#FFFFFF" : "transparent";
  const mono = background === "white" ? "dark" : "none";
  return (
    <AbsoluteFill style={{ background: bg, alignItems: "center", justifyContent: "center" }}>
      <Logo variant={variant} height={variant === "horizontal" ? 420 : 760} mono={mono} />
    </AbsoluteFill>
  );
};
