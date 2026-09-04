// Todos os textos, números e tempos do vídeo ficam aqui.
// Edite este arquivo e rode `npm run render` para gerar o MP4 de novo.

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const TOTAL_FRAMES = 60 * FPS; // 60 s

// Trilha a 100 bpm: 1 tempo = 18 frames. Todos os cortes caem em múltiplos de 18.
export const BEAT = 18;

// Duração de cada cena em frames (cortes no tempo da música). Soma = 1800.
export const SCENES = {
  abertura: 144, // 0.0 - 4.8 s
  oquefaz: 180, // 4.8 - 10.8 s
  financiamento: 360, // 10.8 - 22.8 s
  incentivos: 396, // 22.8 - 36.0 s
  porque: 216, // 36.0 - 43.2 s
  numeros: 216, // 43.2 - 50.4 s
  final: 288, // 50.4 - 60.0 s
};

// Duração (frames) da transição que liga cada cena à seguinte.
export const TRANSITION = 12;

export const EMPRESA = {
  nome: "Projet",
  tagline: "Consultoria & Investimentos",
  desde: "Desde 2011",
  anoFundacao: 2011,
  operacoes: 1000,
  operacoesLabel: "operações aprovadas",
  telefones: ["(27) 98142-8090", "(27) 3727-3251"],
  fraseFinal: "Do projeto à liberação do crédito.",
};

export const ABERTURA = {
  pre: "Toda empresa quer",
  palavra: "CRESCER.",
};

// Cena 2: o que a Projet faz (os dois pilares).
export const OQUEFAZ = {
  pre: "A Projet estrutura",
  pilar1: "FINANCIAMENTOS",
  mais: "+",
  pilar2: "INCENTIVOS FISCAIS",
  pos: "para a sua empresa crescer pagando menos",
};

// Capítulo 01
export const FINANCIAMENTO = {
  numero: "01",
  titulo: "Financiamento",
  sub: "BNB · FNE",
  kicker: "01 · Financiamento BNB · FNE",
  abertura: 36, // frames da abertura do capítulo
  hits: [
    { rotulo: "BNB · FNE", texto: "JUROS REDUZIDOS", desc: "custo menor para investir" },
    { rotulo: "BNB · FNE", texto: "PRAZOS LONGOS", desc: "para pagar com folga" },
    { rotulo: "BNB · FNE", texto: "CARÊNCIA", desc: "para começar a pagar depois" },
  ],
};

// Capítulo 02
export const INCENTIVOS = {
  numero: "02",
  titulo: "Incentivos fiscais",
  sub: "pague menos imposto para crescer",
  kicker: "02 · Incentivos fiscais",
  abertura: 72,
  hits: [
    { rotulo: "SUDENE", valor: 67.5, sufixo: "%", desc: "de redução do IRPJ" },
    { rotulo: "REINVESTIMENTO", valor: 27, sufixo: "%", desc: "do IRPJ reinvestido" },
    { rotulo: "INVEST-ES", texto: "ICMS", desc: "e incentivos estaduais e municipais" },
  ],
  rodape: "Percentuais conforme Lei Complementar 224/2025",
};

export const PORQUE = {
  titulo: "Por que a Projet",
  itens: [
    { titulo: "Enquadramento otimizado", desc: "A melhor linha, porte e condições" },
    { titulo: "Projeto defensável", desc: "Cada indicador com justificativa técnica" },
    { titulo: "Defesa junto ao banco", desc: "Respostas fundamentadas ao analista" },
    { titulo: "Acompanhamento completo", desc: "Da carta-consulta à liberação" },
  ],
};
