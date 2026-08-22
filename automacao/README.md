# Automação de consulta empresarial — JUCEES e fontes públicas

Guia para automatizar a pesquisa de empresas **sem entregar sua senha gov.br a
ninguém — nem a uma IA**.

---

## 1. A regra da senha (leia antes de tudo)

**Nunca digite sua senha gov.br numa conversa com IA.** Nem aqui, nem em nenhuma
outra. Três motivos:

1. **A conversa é um registro.** O que você escreve num chat vai para o
   histórico, e pode ir para logs, backups e transcripts. Não existe "cofre"
   dentro de um chat.
2. **A conta gov.br é sua identidade civil.** O Termo de Uso responsabiliza
   você por tudo que for praticado com ela — assinatura eletrônica, INSS,
   Receita, e-CAC. Não é a senha de um site qualquer.
3. **Não é necessário.** A IA escreve o *código*; o *código* lê a credencial de
   um cofre local, na sua máquina, na hora de rodar. A senha nunca atravessa o
   modelo.

Nesta pasta a regra é ainda mais simples: **nenhum script pede senha.** O login
é feito por você, à mão, numa janela de navegador de verdade.

### Se algum dia precisar guardar uma credencial em script

Ordem de preferência:

| Onde | Como | Quando usar |
|---|---|---|
| Chaveiro do sistema | `keyring` (Python), Credential Manager, Keychain | melhor opção |
| Variável de ambiente | `export MINHA_SENHA=...` na sessão do shell | scripts pontuais |
| Arquivo `.env` | fora do Git, permissão `600` | último recurso |
| **Código-fonte** | — | **nunca** |
| **Chat com IA** | — | **nunca** |

E jamais para o gov.br: lá o login é sempre manual (veja o item 3).

---

## 2. Primeiro pergunte: você precisa mesmo do login?

Boa parte do que se usa num dossiê de prospecção **não exige login nenhum**. Os
Dados Abertos de CNPJ da Receita Federal são públicos e têm API gratuita.

| Dado | Fonte pública (sem login) | Só na Junta (exige login) |
|---|:---:|:---:|
| Razão social, nome fantasia | ✅ | |
| Situação cadastral e data | ✅ | |
| Natureza jurídica, porte | ✅ | |
| Capital social | ✅ | |
| CNAE principal e secundários | ✅ | |
| Quadro societário (QSA) | ✅ | |
| Endereço, telefone, e-mail | ✅ | |
| Data de abertura | ✅ | |
| **NIRE** | | ✅ |
| **Nº e data dos arquivamentos** | | ✅ |
| **Ficha cadastral completa** | | ✅ |
| **Certidão simplificada** | | ✅ |
| **Imagem do contrato social** | | ✅ |

Use `consulta_publica.py` para a coluna da esquerda. É instantâneo, gratuito,
sem risco e sem termo de uso a violar:

```bash
python3 consulta_publica.py 12345678000199
python3 consulta_publica.py --lista cnpjs.txt --csv saida/empresas.csv
```

Zero dependências — só Python 3. Fontes: BrasilAPI, com MinhaReceita de reserva.

**Vá para o item 3 apenas pelo que está na coluna da direita.**

---

## 3. O que o gov.br permite (e o que não permite)

Desde **05/12/2023** o gov.br implementou bloqueio anti-robô na tela de login:
quando suspeita de acesso automatizado, exige um CAPTCHA de imagem. A restrição
chegou ao e-CAC em 18/12/2023. E o Termo de Uso proíbe expressamente robôs,
raspagem e "qualquer método automatizado" de acesso sem autorização escrita.

Traduzindo para a prática:

| | |
|---|---|
| ❌ **Não faça** | script que digita CPF e senha e passa pelo CAPTCHA sozinho |
| ❌ **Não faça** | rodar centenas de consultas em rajada num servidor público |
| ✅ **Pode fazer** | logar você mesmo e automatizar a repetição depois disso |
| ✅ **Pode fazer** | consultar as fontes públicas de CNPJ à vontade (item 2) |
| ✅ **Melhor ainda** | pedir credenciamento/convênio à JUCEES se o volume for alto |

É a diferença entre *burlar a porta* e *usar a porta e automatizar o corredor*.
Só o segundo está neste repositório.

---

## 4. O caminho recomendado: sessão manual + repetição automática

Você loga uma vez, à mão. O Chromium guarda os cookies num perfil local. O
script reaproveita a sessão e faz só a parte chata: abrir a consulta, digitar
o CNPJ, salvar o resultado.

### Instalação (uma vez)

```bash
pip install playwright
playwright install chromium
```

### Passo 1 — logar (você, com os próprios dedos)

```bash
python3 jucees_lote.py login
```

Abre uma janela real. Faça o login no gov.br, resolva CAPTCHA e 2FA
normalmente, chegue na tela de Consulta Empresa e aperte ENTER no terminal.
A sessão fica salva em `perfil-jucees/`.

### Passo 2 — descobrir os seletores (uma vez só)

O script não sabe onde fica o campo de CNPJ no site da JUCEES. Descubra assim:

```bash
python3 jucees_lote.py gravar
```

Abre o gravador do Playwright. Faça **uma** consulta clicando normalmente; ele
imprime o código com os seletores. Copie-os para `config.json`:

```json
{
  "url_consulta": "https://...",
  "seletor_campo_cnpj": "#cnpj",
  "seletor_botao_pesquisar": "button:has-text('Pesquisar')",
  "seletor_resultado": ".resultado-consulta",
  "pausa_entre_consultas": 5,
  "timeout_ms": 30000
}
```

Refaça este passo quando a JUCEES atualizar o site e o script parar de achar
os campos.

### Passo 3 — rodar o lote

```bash
python3 jucees_lote.py consultar --lista cnpjs.txt
```

Para cada CNPJ salva `.png` (página inteira) e `.html` em
`saida/AAAA-MM-DD_HHMM/`. Se a sessão expirar no meio, o script **para e pede
que você relogue à mão** — nunca tenta logar sozinho.

Pausa padrão de 5 segundos entre consultas. Não reduza: é servidor público, e
rajada é exatamente o que dispara o bloqueio anti-robô.

---

## 5. Onde a IA entra (e onde não entra)

| A IA faz bem | A IA não deve fazer |
|---|---|
| escrever e corrigir estes scripts | receber sua senha |
| descobrir e atualizar seletores | logar por você |
| normalizar e cruzar os dados coletados | resolver CAPTCHA |
| transformar o resultado em dossiê/planilha | acessar sua conta gov.br |

O padrão mental: **a IA é o programador, não o operador.** Ela escreve a
ferramenta; quem gira a chave é você.

---

## 6. Arquivos

| Arquivo | O que faz |
|---|---|
| `consulta_publica.py` | consulta CNPJ em fontes públicas — sem login, sem senha |
| `jucees_lote.py` | login manual + consulta em lote na JUCEES |
| `config.json` | URL e seletores do site (gerado no 1º uso) |
| `cnpjs.txt.exemplo` | modelo de lista de entrada |
| `perfil-jucees/` | sessão do navegador — **fora do Git**, contém seus cookies |
| `saida/` | resultados — **fora do Git**, contém dados de clientes |

⚠️ `perfil-jucees/` guarda cookies de sessão da sua conta gov.br. Trate a pasta
como uma senha: não versione, não suba para nuvem, não envie por e-mail nem
WhatsApp. O `.gitignore` da raiz já a exclui.

---

## Fontes

- [GOV.BR limita acesso robotizado — Governo Digital](https://www.gov.br/governodigital/pt-br/noticias/gov-br-limita-acesso-robotizado-para-garantir-maior-disponibilidade-de-servicos-digitais)
- [GOV.BR limita acesso robotizado — Receita Federal](https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2023/dezembro/gov-br-limita-acesso-robotizado-para-garantir-a-disponibilidade-dos-servicos-publicos-digitais)
- [Termo de Uso e Privacidade da Conta gov.br](https://acesso.gov.br/faq/_perguntasdafaq/termodeusoeprivacidade.html)
- [JUCEES — Serviços](https://jucees.es.gov.br/servicos)
- [JUCEES — Certidão Web](https://www.jucees.es.gov.br/certidaowebn/)
