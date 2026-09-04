import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts } from "../theme";
import {
  PX_PER_M,
  access,
  annex,
  curingRacks,
  equipmentPlacements,
  expansion,
  road,
  shed,
  shedColumns,
  shedCure,
  terrain,
  yard,
  yardPallets,
} from "./PlantLayout";
import { Box3D, Cylinder3D, FloorFace, WallFace, shade } from "./Box3D";
import { MediaSlot } from "../MediaSlot";

export type CameraKeyframe = {
  frame: number;
  /** ponto de interesse em metros */
  px: number;
  py: number;
  /** inclinação (0 = vista de cima, 90 = horizonte) */
  rx: number;
  /** giro em torno do eixo vertical */
  rz: number;
  scale: number;
};

const ease = Easing.bezier(0.45, 0, 0.2, 1);

const useCamera = (keys: CameraKeyframe[]) => {
  const frame = useCurrentFrame();
  const frames = keys.map((k) => k.frame);
  const get = (sel: (k: CameraKeyframe) => number) =>
    interpolate(frame, frames, keys.map(sel), {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: ease,
    });
  return { px: get((k) => k.px), py: get((k) => k.py), rx: get((k) => k.rx), rz: get((k) => k.rz), scale: get((k) => k.scale) };
};

/** Projeta um ponto do mundo (metros) para coordenadas de tela, replicando a cadeia de transforms CSS. */
const project = (cam: { px: number; py: number; rx: number; rz: number; scale: number }, x: number, y: number, z: number) => {
  const P = 2600; // perspective
  const ox = 960; // origem da perspectiva (centro do AbsoluteFill)
  const oy = 540;
  const wx = 960; // posição do palco 3D (left 50%, top 54%)
  const wy = 1080 * 0.54;
  const x0 = (x - cam.px) * PX_PER_M;
  const y0 = (y - cam.py) * PX_PER_M;
  const z0 = z * PX_PER_M;
  const rz = (cam.rz * Math.PI) / 180;
  const rx = (cam.rx * Math.PI) / 180;
  const x1 = x0 * Math.cos(rz) - y0 * Math.sin(rz);
  const y1 = x0 * Math.sin(rz) + y0 * Math.cos(rz);
  const y2 = y1 * Math.cos(rx) - z0 * Math.sin(rx);
  const z2 = y1 * Math.sin(rx) + z0 * Math.cos(rx);
  const x3 = x1 * cam.scale;
  const y3 = y2 * cam.scale;
  const f = 1 / (1 - z2 / P);
  return { x: ox + (wx - ox + x3) * f, y: oy + (wy - oy + y3) * f };
};

/** Rótulo 2D ancorado num ponto 3D (linha-guia até o equipamento). */
const Label2D: React.FC<{ sx: number; sy: number; opacity: number; text: string; lift?: number }> = ({ sx, sy, opacity, text, lift = 70 }) => (
  <div style={{ position: "absolute", left: sx, top: sy, opacity, pointerEvents: "none" }}>
    <div style={{ position: "absolute", left: -1, top: -lift, width: 2, height: lift, background: colors.yellow }} />
    <div style={{ position: "absolute", left: -6, top: -6, width: 12, height: 12, borderRadius: 6, background: colors.yellow, boxShadow: "0 0 0 4px rgba(247,181,0,0.3)" }} />
    <div
      style={{
        position: "absolute",
        left: 0,
        top: -lift,
        translate: "-50% -100%",
        display: "inline-flex",
        padding: "8px 16px",
        background: "rgba(7,26,51,0.9)",
        border: `2px solid ${colors.yellow}`,
        borderRadius: 8,
        color: colors.white,
        fontFamily: fonts.body,
        fontWeight: 700,
        fontSize: 26,
        whiteSpace: "nowrap",
      }}
    >
      {text}
    </div>
  </div>
);

const Ground: React.FC = () => (
  <>
    {/* terreno */}
    <FloorFace
      x={0}
      y={0}
      w={terrain.w}
      d={terrain.d}
      z={0}
      style={{
        background: `repeating-linear-gradient(90deg, ${colors.grass} 0 40px, ${colors.grassDark} 40px 44px)`,
        outline: `3px solid ${colors.yellow}`,
        outlineOffset: -3,
      }}
    />
    {/* rodovia BR-381 */}
    <FloorFace x={-40} y={road.y} w={terrain.w + 80} d={road.d} z={0.02} style={{ background: colors.asphalt }} />
    <FloorFace x={-40} y={road.y + road.d / 2 - 0.15} w={terrain.w + 80} d={0.3} z={0.03} style={{ background: colors.yellow }} />
    {/* acesso */}
    <FloorFace x={access.x} y={access.y} w={access.w} d={access.d} z={0.02} style={{ background: "#7A7F88" }} />
    {/* pátio */}
    <FloorFace x={yard.x} y={yard.y} w={yard.w} d={yard.d} z={0.02} style={{ background: "#9AA0AA" }} />
    {/* área de expansão (hachurada) */}
    <FloorFace
      x={expansion.x}
      y={expansion.y}
      w={expansion.w}
      d={expansion.d}
      z={0.03}
      style={{
        background: `repeating-linear-gradient(45deg, rgba(247,181,0,0.32) 0 10px, rgba(247,181,0,0.06) 10px 22px)`,
        outline: `3px dashed ${colors.yellow}`,
        outlineOffset: -3,
      }}
    />
    {/* piso do galpão + anexo */}
    <FloorFace x={shed.x} y={shed.y} w={shed.w + shedCure.w} d={shed.d} z={0.04} style={{ background: colors.floor }} />
    <FloorFace x={annex.x} y={annex.y} w={annex.w} d={annex.d} z={0.04} style={{ background: "#C4C8CF" }} />
  </>
);

const Building: React.FC<{ roofOpacity: number }> = ({ roofOpacity }) => {
  const total = { x: shed.x, y: shed.y, w: shed.w + shedCure.w, d: shed.d, h: shed.h };
  const wall: React.CSSProperties = {
    background: `linear-gradient(180deg, rgba(200,206,214,${0.55 * roofOpacity}) 0%, rgba(200,206,214,${0.25 * roofOpacity}) 100%)`,
  };
  return (
    <>
      {shedColumns.map((c, i) => (
        <Box3D key={i} box={c} color="#5B6472" />
      ))}
      {/* paredes translúcidas (fundo e laterais) */}
      <WallFace ax={total.x + total.w} ay={total.y} bx={total.x} by={total.y} z={0} h={total.h} style={wall} />
      <WallFace ax={total.x} ay={total.y} bx={total.x} by={total.y + total.d} z={0} h={total.h} style={wall} />
      <WallFace ax={total.x + total.w} ay={total.y + total.d} bx={total.x + total.w} by={total.y} z={0} h={total.h} style={wall} />
      {/* cobertura translúcida com terças */}
      <FloorFace
        x={total.x}
        y={total.y}
        w={total.w}
        d={total.d}
        z={total.h}
        style={{
          background: `repeating-linear-gradient(90deg, rgba(11,37,69,${0.55 * roofOpacity}) 0 6px, rgba(60,80,110,${0.35 * roofOpacity}) 6px 48px)`,
          borderTop: `4px solid rgba(247,181,0,${roofOpacity})`,
          borderBottom: `4px solid rgba(247,181,0,${roofOpacity})`,
        }}
      />
      {/* testeira com o nome */}
      <WallFace ax={total.x} ay={total.y + total.d} bx={total.x + total.w} by={total.y + total.d} z={total.h - 1.6} h={1.6} style={{ background: colors.navy }}>
        <div
          style={{
            width: "100%",
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: fonts.heading,
            fontWeight: 900,
            fontSize: 9,
            letterSpacing: 2,
            color: colors.yellow,
          }}
        >
          GTK PRÉ-MOLDADOS
        </div>
      </WallFace>
    </>
  );
};

const Hopper: React.FC<{ box: { x: number; y: number; w: number; d: number; h: number }; color: string; accent: string }> = ({ box, color, accent }) => {
  // central de agregados: 4 cubas sobre estrutura amarela
  const n = 4;
  const cw = box.w / n;
  return (
    <>
      <Box3D box={{ x: box.x, y: box.y, w: box.w, d: box.d, h: 1.4 }} color={accent} />
      {Array.from({ length: n }, (_, i) => (
        <Box3D
          key={i}
          box={{ x: box.x + i * cw + 0.15, y: box.y + 0.1, w: cw - 0.3, d: box.d - 0.2, h: box.h - 1.4, z: 1.4 }}
          color={color}
          accent={shade(color, -0.4)}
        />
      ))}
    </>
  );
};

export const Plant3D: React.FC<{
  camera: CameraKeyframe[];
  /** frame em que cada equipamento (por `order`) acende; -1 = todos ligados */
  lightFrom?: number;
  lightEvery?: number;
  showLabels?: boolean;
  /** opacidade global dos rótulos (para esconder na visão geral) */
  labelOpacity?: number;
  roofFadeAt?: [number, number];
}> = ({ camera, lightFrom = -1, lightEvery = 18, showLabels = true, labelOpacity = 1, roofFadeAt }) => {
  const frame = useCurrentFrame();
  const cam = useCamera(camera);
  const roofOpacity = roofFadeAt
    ? interpolate(frame, roofFadeAt, [1, 0.12], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease })
    : 1;

  const lit = (order: number) => {
    if (lightFrom < 0) return 1;
    const s = lightFrom + (order - 1) * lightEvery;
    return interpolate(frame, [s, s + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  };

  return (
    <AbsoluteFill style={{ perspective: 2600, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "54%",
          width: 0,
          height: 0,
          transformStyle: "preserve-3d",
          transform: `scale(${cam.scale}) rotateX(${cam.rx}deg) rotateZ(${cam.rz}deg) translate(${-cam.px * PX_PER_M}px, ${-cam.py * PX_PER_M}px)`,
        }}
      >
        <div style={{ position: "absolute", left: 0, top: 0, transformStyle: "preserve-3d" }}>
          <Ground />
          {/* cura */}
          {curingRacks.map((b, i) => (
            <Box3D
              key={`r${i}`}
              box={b}
              color="#4B5563"
              topStyle={{ background: `repeating-linear-gradient(0deg, #6B7280 0 3px, #374151 3px 8px)` }}
            />
          ))}
          {yardPallets.map((b, i) => (
            <Box3D key={`p${i}`} box={b} color="#C9CFD8" accent="#DFE3E8" />
          ))}
          {/* equipamentos */}
          {equipmentPlacements.map((e) => {
            const glow = lit(e.order);
            const dim = 0.35 + 0.65 * glow;
            if (e.kind === "cylinder") {
              return <Cylinder3D key={e.id} box={e.box} color={e.color} accent={e.accent} opacity={dim} />;
            }
            if (e.kind === "hopper") {
              return (
                <div key={e.id} style={{ opacity: dim, transformStyle: "preserve-3d", position: "absolute" }}>
                  <Hopper box={e.box} color={e.color} accent={e.accent ?? colors.yellow} />
                </div>
              );
            }
            const front = e.media ? (
              <div style={{ width: "100%", height: "100%", transform: "scaleY(1)" }}>
                <MediaSlot id={e.media} trimSeconds={8} fit="cover" />
              </div>
            ) : undefined;
            return (
              <div key={e.id} style={{ opacity: dim, transformStyle: "preserve-3d", position: "absolute" }}>
                <Box3D box={e.box} color={e.color} accent={e.accent} front={front} />
                {/* tremonha amarela sobre a vibroprensa e o misturador */}
                {(e.id === "vibroprensa" || e.id === "misturador") && (
                  <Box3D
                    box={{ x: e.box.x + 0.4, y: e.box.y + 0.3, w: e.box.w - 0.8, d: e.box.d - 0.6, h: 1.1, z: (e.box.z ?? 0) + e.box.h }}
                    color={colors.yellow}
                  />
                )}
              </div>
            );
          })}
          <Building roofOpacity={roofOpacity} />
        </div>
      </div>
      {/* rótulos 2D projetados, um de cada vez na ordem do fluxo */}
      {showLabels &&
        equipmentPlacements
          .filter((e) => ["silo", "central", "misturador", "vibroprensa", "elevador", "paletizador"].includes(e.id))
          .map((e) => {
            const zTop = (e.box.z ?? 0) + (e.id === "silo" ? e.box.h * 0.7 : e.box.h);
            const p = project(cam, e.box.x + e.box.w / 2, e.box.y + e.box.d / 2, zTop);
            const s0 = lightFrom < 0 ? 0 : lightFrom + (e.order - 1) * lightEvery;
            const win = lightEvery * 1.6;
            const o =
              lightFrom < 0
                ? 1
                : interpolate(frame, [s0, s0 + 8, s0 + win - 8, s0 + win], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return <Label2D key={`l${e.id}`} sx={p.x} sy={p.y} opacity={o * labelOpacity} text={e.label} lift={70} />;
          })}
    </AbsoluteFill>
  );
};
