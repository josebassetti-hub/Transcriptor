import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Camera } from "../components/Camera";
import { Particles, Shockwave, Flash } from "../components/Fx";
import { riseIn, slamIn } from "../components/anim";
import { BEAT, METODO, SCENES } from "../content";
import { font, theme } from "../theme";

/** Cena 3: "Crédito de longo prazo exige MÉTODO." com linha varrendo e selo BNB · FNE. */
export const Metodo: React.FC = () => {
  const frame = useCurrentFrame();
  const hit = BEAT * 2;
  const sweep = interpolate(frame, [hit, hit + 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const rings = [0, 1, 2, 3];
  return (
    <AbsoluteFill style={{ fontFamily: font.family, overflow: "hidden" }}>
      <Camera duration={SCENES.metodo} from={1.06} to={1} panX={20}>
        <Particles count={50} speed={1} seed="m" />
        {/* anéis concêntricos girando lentamente */}
        {rings.map((r) => (
          <div
            key={r}
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              width: 700 + r * 380,
              height: 700 + r * 380,
              marginLeft: -(700 + r * 380) / 2,
              marginTop: -(700 + r * 380) / 2,
              borderRadius: "50%",
              border: `2px ${r % 2 ? "dashed" : "solid"} rgba(95,179,232,${0.18 - r * 0.03})`,
              transform: `rotate(${frame * (0.15 + r * 0.05) * (r % 2 ? -1 : 1)}deg)`,
            }}
          />
        ))}
      </Camera>
      <div style={{ position: "absolute", left: 0, right: 0, top: 330, textAlign: "center", ...riseIn(frame, 0, 12, 40) }}>
        <div style={{ fontSize: 78, fontWeight: 600, color: theme.white, letterSpacing: -1 }}>{METODO.linha1}</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 440, textAlign: "center", display: "flex", justifyContent: "center", alignItems: "baseline", gap: 34 }}>
        <div style={{ fontSize: 78, fontWeight: 500, color: theme.muted, ...riseIn(frame, 8, 12, 40) }}>{METODO.linha2a}</div>
        <div style={{ ...slamIn(frame, hit), fontSize: 210, fontWeight: 900, color: theme.blueLight, letterSpacing: -8, lineHeight: 1, textShadow: `0 0 70px ${theme.glow}` }}>
          {METODO.linha2b}
        </div>
      </div>
      <div style={{ position: "absolute", left: "50%", top: 690, width: 1100 * sweep, marginLeft: -550, height: 5, background: `linear-gradient(90deg, transparent, ${theme.blueLight}, transparent)` }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 740, textAlign: "center", ...riseIn(frame, hit + 20, 14, 30) }}>
        <span style={{ display: "inline-block", padding: "14px 40px", borderRadius: 999, border: `2px solid ${theme.blueLight}`, color: theme.white, fontSize: 34, fontWeight: 700, letterSpacing: 6 }}>
          {METODO.pill}
        </span>
      </div>
      <Shockwave at={hit} />
      <Flash at={hit} strength={0.3} />
    </AbsoluteFill>
  );
};
