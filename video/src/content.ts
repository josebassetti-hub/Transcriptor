// Todos os textos, números e tempos do vídeo ficam aqui.
// Edite este arquivo e rode `npm run render` para gerar o MP4 de novo.

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const TOTAL_FRAMES = 60 * FPS; // 60 s

const s = (sec: number) => Math.round(sec * FPS);

// Início e duração de cada cena, em frames.
export const SCENES = {
  abertura: { from: s(0), duration: s(5) },
  desafio: { from: s(5), duration: s(8) },
  estruturacao: { from: s(13), duration: s(13) },
  incentivos: { from: s(26), duration: s(12) },
  diferenciais: { from: s(38), duration: s(10) },
  numeros: { from: s(48), duration: s(6) },
  encerramento: { from: s(54), duration: s(6) },
};

export const EMPRESA = {
  nome: "Projet",
  tagline: "Consultoria & Investimentos",
  descricao: "Estruturação de projetos e incentivos fiscais",
  desde: "Desde 2011",
  anoFundacao: 2011,
  operacoes: 1000,
  operacoesLabel: "operações aprovadas",
  telefones: ["(27) 98142-8090", "(27) 3727-3251"],
  fraseFinal: "Do projeto à liberação do crédito.",
};

export const DESAFIO = {
  linha1: "Investir exige capital.",
  linha2: "Acessar crédito de longo prazo exige método.",
  itens: ["Expansão", "Modernização", "Capital de giro estrutural"],
};

export const ESTRUTURACAO = {
  titulo: "Estruturação de projetos",
  subtitulo: "Financiamento BNB · FNE",
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
  subtitulo: "que reduzem o custo de crescer",
  cards: [
    { rotulo: "SUDENE", valor: 67.5, sufixo: "%", desc: "de redução do IRPJ" },
    { rotulo: "REINVESTIMENTO", valor: 27, sufixo: "%", desc: "do IRPJ reinvestido" },
    { rotulo: "INVEST-ES", valor: null, sufixo: "", desc: "e incentivos estaduais e municipais" },
  ],
  rodape: "Percentuais conforme Lei Complementar 224/2025",
};

export const DIFERENCIAIS = {
  titulo: "Por que a Projet",
  itens: [
    { titulo: "Enquadramento otimizado", desc: "A melhor linha, porte e condições para o seu caso" },
    { titulo: "Projeto defensável", desc: "Cada indicador com justificativa técnica" },
    { titulo: "Defesa junto ao banco", desc: "Respostas fundamentadas ao analista" },
    { titulo: "Acompanhamento completo", desc: "Da carta-consulta à liberação dos recursos" },
  ],
};
