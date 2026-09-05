import React from "react";
import { C } from "../theme";
import { Reveal, Fade } from "./Text";

/**
 * Nome fantasia em duas linhas: a primeira palavra ("PEDREIRA") pequena em prata,
 * o resto ("VALE DO CRICARÉ") grande em prata metálica com o mesmo reveal do logo.
 */
export const BrandName: React.FC<{
  name: string;
  from: number;
  sizeSmall?: number;
  sizeBig?: number;
  align?: "left" | "center" | "right";
}> = ({ name, from, sizeSmall = 46, sizeBig = 120, align = "center" }) => {
  const [first, ...rest] = name.trim().split(/\s+/);
  const big = rest.join(" ");
  const items: React.CSSProperties["alignItems"] = align === "left" ? "flex-start" : align === "right" ? "flex-end" : "center";
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: items, gap: Math.round(sizeBig * 0.08) }}>
      <Fade text={first} from={from} size={sizeSmall} weight={500} color={C.silver} upper tracking={0.4} align={align} />
      <Reveal text={big} from={from + 4} size={sizeBig} metallic tracking={0.16} align={align} maxWidth={1700} duration={24} lineHeight={1.05} />
    </div>
  );
};
