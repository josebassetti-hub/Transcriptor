import React from "react";
import { theme } from "../theme";

export const Card: React.FC<{ style?: React.CSSProperties; children: React.ReactNode }> = ({ style, children }) => (
  <div
    style={{
      background: theme.card,
      border: `1px solid ${theme.cardBorder}`,
      borderRadius: 24,
      padding: "36px 40px",
      backdropFilter: "blur(6px)",
      boxShadow: "0 20px 60px rgba(0,0,0,0.35)",
      ...style,
    }}
  >
    {children}
  </div>
);
