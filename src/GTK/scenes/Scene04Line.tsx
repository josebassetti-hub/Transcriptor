import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts, SAFE } from "../theme";
import { equipment, lineFacts } from "../data";
import { FactBar, Kicker } from "../ui/Text";
import { MediaSlot } from "../MediaSlot";
import { EquipmentIcon } from "../equipment/EquipmentIcon";

const PER = 90; // frames por equipamento (7 x 90 = 630) + 42 de abertura

export const Scene04Line: React.FC = () => {
  const frame = useCurrentFrame();
  const t0 = 42;
  const idx = Math.min(equipment.length - 1, Math.max(0, Math.floor((frame - t0) / PER)));
  const local = frame - t0 - idx * PER;
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  const inT = interpolate(local, [0, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const outT = idx < equipment.length - 1 ? interpolate(local, [PER - 12, PER], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;
  const vis = Math.min(inT, outT);
  const eq = equipment[idx];
  const titleIn = interpolate(frame, [0, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: colors.ink }}>
      <AbsoluteFill style={{ opacity: 0.35, filter: "saturate(0.8)" }}>
        <MediaSlot id="video:xp350-operacao" trimSeconds={18} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(7,26,51,0.92) 0%, rgba(7,26,51,0.75) 55%, rgba(7,26,51,0.35) 100%)" }} />

      <div style={{ position: "absolute", left: SAFE.x, top: SAFE.y - 20, opacity: titleIn }}>
        <Kicker start={0}>A linha de produção</Kicker>
        <div style={{ fontFamily: fonts.heading, fontWeight: 900, fontSize: 64, color: colors.white, marginTop: 14 }}>
          Da dosagem ao pallet, em fluxo contínuo
        </div>
      </div>

      {/* card em destaque */}
      <div style={{ position: "absolute", left: SAFE.x, top: 300, display: "flex", gap: 44, alignItems: "stretch", opacity: vis }}>
        <div
          style={{
            width: 900,
            height: 520,
            borderRadius: 22,
            overflow: "hidden",
            background: colors.navy2,
            boxShadow: "0 30px 70px rgba(0,0,0,0.45)",
            border: `3px solid ${colors.yellow}`,
            translate: `${(1 - inT) * -40}px 0px`,
          }}
        >
          <MediaSlot
            id={eq.media}
            trimSeconds={6}
            fallback={
              <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <EquipmentIcon id={eq.id} width={600} />
              </div>
            }
          />
        </div>
        <div style={{ width: 700, display: "flex", flexDirection: "column", justifyContent: "center", gap: 18, translate: `${(1 - inT) * 40}px 0px` }}>
          <div style={{ fontFamily: fonts.body, fontWeight: 700, fontSize: 30, letterSpacing: 5, color: colors.yellow }}>
            ETAPA {idx + 1} DE {equipment.length}
          </div>
          <div style={{ fontFamily: fonts.heading, fontWeight: 900, fontSize: 60, lineHeight: 1.05, color: colors.white }}>{eq.name}</div>
          <div style={{ fontFamily: fonts.body, fontWeight: 500, fontSize: 36, lineHeight: 1.3, color: colors.concreteLight }}>{eq.desc}</div>
        </div>
      </div>

      {/* stepper */}
      <div style={{ position: "absolute", left: SAFE.x, right: SAFE.x, top: 860, display: "flex", gap: 10, alignItems: "center" }}>
        {equipment.map((e, i) => {
          const active = i === idx;
          const done = i < idx;
          return (
            <React.Fragment key={e.id}>
              <div
                style={{
                  flex: 1,
                  padding: "12px 10px",
                  borderRadius: 12,
                  background: active ? colors.yellow : done ? "rgba(247,181,0,0.25)" : "rgba(255,255,255,0.08)",
                  color: active ? colors.navyDeep : colors.white,
                  fontFamily: fonts.body,
                  fontWeight: 700,
                  fontSize: 26,
                  textAlign: "center",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {e.short}
              </div>
              {i < equipment.length - 1 && <div style={{ width: 0, height: 0, borderTop: "10px solid transparent", borderBottom: "10px solid transparent", borderLeft: `14px solid ${done || active ? colors.yellow : "rgba(255,255,255,0.3)"}` }} />}
            </React.Fragment>
          );
        })}
      </div>

      <div style={{ position: "absolute", left: SAFE.x, bottom: 40 }}>
        <FactBar items={lineFacts} start={24} />
      </div>
    </AbsoluteFill>
  );
};
