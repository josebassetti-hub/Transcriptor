import "./index.css";
import { Composition, Folder, Still } from "remotion";
import { HelloWorld } from "./HelloWorld";
import { Logo } from "./HelloWorld/Logo";
import { GTKInstitutional, SCENES, TOTAL_FRAMES, gtkDefaultProps, gtkSchema } from "./GTK/GTKInstitutional";
import { LogoStill } from "./GTK/LogoStill";
import { Scene01Brand } from "./GTK/scenes/Scene01Brand";
import { Scene02Company } from "./GTK/scenes/Scene02Company";
import { Scene03Products } from "./GTK/scenes/Scene03Products";
import { Scene04Line } from "./GTK/scenes/Scene04Line";
import { Scene05Capacity } from "./GTK/scenes/Scene05Capacity";
import { Scene06Plant } from "./GTK/scenes/Scene06Plant";
import { Scene07Investment } from "./GTK/scenes/Scene07Investment";
import { Scene08Jobs } from "./GTK/scenes/Scene08Jobs";
import { Scene09Outro } from "./GTK/scenes/Scene09Outro";

const HD = { fps: 30, width: 1920, height: 1080 };

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Vídeo institucional GTK Pré-Moldados (90 s) */}
      <Composition
        id="GTKInstitutional"
        component={GTKInstitutional}
        durationInFrames={TOTAL_FRAMES}
        {...HD}
        schema={gtkSchema}
        defaultProps={gtkDefaultProps}
      />

      <Folder name="GTK-Cenas">
        <Composition id="GTK-01-Marca" component={Scene01Brand} durationInFrames={SCENES.brand} {...HD} />
        <Composition id="GTK-02-Empresa" component={Scene02Company} durationInFrames={SCENES.company} {...HD} />
        <Composition id="GTK-03-Produtos" component={Scene03Products} durationInFrames={SCENES.products} {...HD} />
        <Composition id="GTK-04-Linha" component={Scene04Line} durationInFrames={SCENES.line} {...HD} />
        <Composition id="GTK-05-Capacidade" component={Scene05Capacity} durationInFrames={SCENES.capacity} {...HD} />
        <Composition id="GTK-06-Planta3D" component={Scene06Plant} durationInFrames={SCENES.plant} {...HD} />
        <Composition
          id="GTK-07-Investimento"
          component={Scene07Investment}
          durationInFrames={SCENES.investment}
          {...HD}
          defaultProps={{ investmentBRL: gtkDefaultProps.investmentBRL }}
        />
        <Composition
          id="GTK-08-Empregos"
          component={Scene08Jobs}
          durationInFrames={SCENES.jobs}
          {...HD}
          defaultProps={{ directJobs: gtkDefaultProps.directJobs, indirectJobs: gtkDefaultProps.indirectJobs }}
        />
        <Composition
          id="GTK-09-Encerramento"
          component={Scene09Outro}
          durationInFrames={SCENES.outro}
          {...HD}
          defaultProps={{
            contactName: gtkDefaultProps.contactName,
            contactRole: gtkDefaultProps.contactRole,
            contactPhone: gtkDefaultProps.contactPhone,
          }}
        />
      </Folder>

      <Folder name="GTK-Logo">
        <Still id="GTKLogoHorizontal" component={LogoStill} width={2400} height={900} defaultProps={{ variant: "horizontal", background: "navy" }} />
        <Still id="GTKLogoVertical" component={LogoStill} width={1200} height={1200} defaultProps={{ variant: "vertical", background: "navy" }} />
        <Still id="GTKLogoBranco" component={LogoStill} width={2400} height={900} defaultProps={{ variant: "horizontal", background: "white" }} />
        <Still id="GTKLogoTransparente" component={LogoStill} width={2400} height={900} defaultProps={{ variant: "horizontal", background: "transparent" }} />
      </Folder>

      {/* Template Hello World original */}
      <Folder name="HelloWorld">
        <Composition
          id="HelloWorld"
          component={HelloWorld}
          durationInFrames={150}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{
            titleText: "Welcome to Remotion",
            titleColor: "#000000",
            logoColor1: "#91EAE4",
            logoColor2: "#86A8E7",
          }}
        />
        <Composition
          id="OnlyLogo"
          component={Logo}
          durationInFrames={150}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{
            logoColor1: "#91dAE2",
            logoColor2: "#86A8E7",
          }}
        />
      </Folder>
    </>
  );
};
