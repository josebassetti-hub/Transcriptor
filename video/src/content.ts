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
  verbos: 180, // 4.8 - 10.8 s
  metodo: 162, // 10.8 - 16.2 s
  jornada: 342, // 16.2 - 27.6 s
  incentivos: 324, // 27.6 - 38.4 s
  porque: 234, // 38.4 - 46.2 s
  numeros: 180, // 46.2 - 52.2 s
  final: 234, // 52.2 - 60.0 s
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

export const VERBOS = {
  pre: "Sua empresa quer",
  palavras: ["EXPANDIR.", "MODERNIZAR.", "INVESTIR."],
};

export const METODO = {
  linha1: "Crédito de longo prazo",
  linha2a: "exige",
  linha2b: "MÉTODO.",
  pill: "BNB · FNE",
};

export const JORNADA = {
  titulo: "Estruturação de projetos",
  etapas: [
    { n: "01", titulo: "Diagnóstico", desc: "Viabilidade e linha de crédito" },
    { n: "02", titulo: "Cadastro e carta-consulta", desc: "Dossiê e enquadramento" },
    { n: "03", titulo: "Projeto econômico-financeiro", desc: "Memória de cálculo defensável" },
    { n: "04", titulo: "Defesa e aprovação", desc: "Resposta técnica ao analista" },
    { n: "05", titulo: "Contratação e liberação", desc: "Até a primeira parcela" },
  ],
};

export const INCENTIVOS = {
  titulo: "Incentivos fiscais",
  hits: [
    { rotulo: "SUDENE", valor: 67.5, sufixo: "%", desc: "de redução do IRPJ" },
    { rotulo: "REINVESTIMENTO", valor: 27, sufixo: "%", desc: "do IRPJ reinvestido" },
    { rotulo: "INVEST-ES", valor: null, texto: "ICMS", desc: "e incentivos estaduais e municipais" },
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
