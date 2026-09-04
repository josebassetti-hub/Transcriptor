// Todos os textos e números do roteiro. Fonte: Cartão CNPJ + Estudo de Mercado (ago/2026)
// e instruções do cliente (investimento total, contato, terreno e coordenadas).

export const company = {
  name: "GTK PRÉ-MOLDADOS",
  legalName: "GTK Pré-Moldados Ltda",
  cnpj: "66.492.016/0001-77",
  founded: "2026",
  city: "São Mateus – ES",
  address: "Rodovia BR-381 (Miguel Curry Carneiro), km 35 · Zona Rural",
  gps: "18°43'08.9\"S 40°09'53.4\"W",
  lat: -18.71914,
  lon: -40.16483,
  tagline: "Concreto que constrói o Norte Capixaba",
  claim: "A primeira fábrica automática de blocos e pisos intertravados do interior norte-capixaba",
  standards: "Blocos, canaletas e pavers certificados · NBR 6136 / NBR 9781",
};

export const contact = {
  role: "Vendas e Parcerias",
  name: "Kauã Boldrini",
  phone: "(27) 99978-3098",
};

export const site = {
  terrainM2: 25000,
  shedM2: 1500,
  terrainLabel: "Terreno de 25.000 m²",
  shedLabel: "Galpão industrial ≈ 1.500 m²",
  expansionLabel: "Área reservada para ampliações",
};

export const capacity = [
  { value: 7000, suffix: "", label: "blocos por turno", note: "bloco 14×19×39" },
  { value: 1.85, suffix: " mi", label: "blocos por ano", note: "1 turno · 22 dias/mês", decimals: 2 },
  { value: 530, suffix: " m²", label: "de paver por turno", note: "piso intertravado" },
  { value: 2, suffix: "×", label: "com o 2º turno", note: "sem novo investimento" },
];

export const products = [
  {
    id: "bloco",
    title: "Blocos",
    subtitle: "Vedação e estruturais",
    detail: "9 · 14 · 19 cm · NBR 6136",
  },
  {
    id: "canaleta",
    title: "Canaletas",
    subtitle: "Vergas e cintas",
    detail: "9 · 14 · 19 cm",
  },
  {
    id: "paver",
    title: "Pavers",
    subtitle: "Piso intertravado",
    detail: "6 cm · 35 MPa  |  8 cm · 50 MPa",
  },
];

export type EquipmentId =
  | "silo"
  | "central"
  | "misturador"
  | "esteiras"
  | "vibroprensa"
  | "elevador"
  | "paletizador";

export const equipment: {
  id: EquipmentId;
  name: string;
  short: string;
  desc: string;
  media: string;
}[] = [
  {
    id: "silo",
    name: "Silo de cimento 90 t",
    short: "Silo",
    desc: "Cimento a granel com rosca transportadora de 7 m e balança de dosagem",
    media: "cat:silo",
  },
  {
    id: "central",
    name: "Central de agregados 4 cubas",
    short: "Central",
    desc: "Dosagem automática de areia, pó de pedra e pedrisco com erro inferior a 1 %",
    media: "cat:central-agregados",
  },
  {
    id: "misturador",
    name: "Misturador MXS-1000",
    short: "Misturador",
    desc: "Mistura homogênea com automação de água e aditivo",
    media: "cat:misturador",
  },
  {
    id: "esteiras",
    name: "Esteiras transportadoras 6 m e 12 m",
    short: "Esteiras",
    desc: "Alimentação contínua da vibroprensa",
    media: "cat:carro-aereo",
  },
  {
    id: "vibroprensa",
    name: "Vibroprensa Gervasi XP350",
    short: "Vibroprensa",
    desc: "Ciclo abaixo de 15 s · 2.000 bandejas por turno · até 15 % menos cimento",
    media: "video:xp350-ciclo",
  },
  {
    id: "elevador",
    name: "Acumulador e descarregador de bandejas AM02 / DM02",
    short: "Elevador",
    desc: "Circulação automática das bandejas entre a máquina e a cura",
    media: "cat:elevador-bandejas",
  },
  {
    id: "paletizador",
    name: "Sistema de paletização automático ST800",
    short: "Paletizador",
    desc: "Pallets montados automaticamente para estoque e expedição",
    media: "cat:paletizador",
  },
];

export const lineFacts = [
  "Linha automática Gervasi XP350",
  "ciclo < 15 s",
  "2.000 bandejas/turno",
  "até 15 % menos cimento",
];

export const marketCities = [
  { name: "São Mateus", lat: -18.72, lon: -39.86, major: true },
  { name: "Nova Venécia", lat: -18.71, lon: -40.4, major: true },
  { name: "Jaguaré", lat: -18.91, lon: -40.08 },
  { name: "Boa Esperança", lat: -18.54, lon: -40.3 },
  { name: "Conceição da Barra", lat: -18.59, lon: -39.73 },
  { name: "Pinheiros", lat: -18.41, lon: -40.22 },
  { name: "Vila Valério", lat: -18.99, lon: -40.39 },
  { name: "S. Gabriel da Palha", lat: -19.02, lon: -40.54 },
  { name: "Sooretama", lat: -19.19, lon: -40.1 },
  { name: "Linhares", lat: -19.39, lon: -40.07 },
  { name: "Vitória", lat: -20.32, lon: -40.34, capital: true },
];

export const narration: { scene: string; text: string }[] = [
  { scene: "01 Abertura", text: "GTK Pré-Moldados. Uma nova indústria nasce no coração do norte do Espírito Santo." },
  { scene: "02 Empresa", text: "Instalada no km 35 da rodovia Miguel Curry Carneiro, entre São Mateus e Nova Venécia, a GTK será a primeira fábrica automática de blocos e pisos intertravados do interior norte-capixaba." },
  { scene: "03 Produtos", text: "Blocos de vedação e estruturais, canaletas e pavers de alta resistência, com qualidade de norma para obras, revendas e prefeituras." },
  { scene: "04 Linha", text: "O coração da fábrica é a linha automática Gervasi XP350: dosagem, mistura, vibroprensagem, cura e paletização em fluxo contínuo, com supervisório em tempo real." },
  { scene: "05 Capacidade", text: "São mais de sete mil blocos por turno, quase dois milhões por ano, com capacidade de dobrar sem novo investimento." },
  { scene: "06 Planta 3D", text: "Em um terreno de vinte e cinco mil metros quadrados, o galpão industrial abriga a linha em fluxo contínuo, pátio de cura e estoque, com área reservada para as próximas ampliações." },
  { scene: "07 Investimento", text: "Um investimento total de cinco milhões de reais em equipamentos, obras e infraestrutura." },
  { scene: "08 Empregos", text: "Doze empregos diretos e cerca de trinta e seis indiretos, movimentando pedreiras, transporte, revendas e a construção civil da região." },
  { scene: "09 Encerramento", text: "GTK Pré-Moldados. Construindo o futuro do norte capixaba. Vendas e parcerias: fale com Kauã Boldrini." },
];
