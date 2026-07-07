# Biblioteca de casos — memória de projetos (raciocínio por analogia)

Cada projeto trabalhado vira um caso consultável: os exemplos do professor E cada projeto
real futuro. É assim que a fábrica acumula a "experiência" de um consultor sênior — diante
de um projeto novo, os agentes consultam casos análogos antes de calcular.

## Template obrigatório (`casos/AAAA-MM-apelido.md`)

```markdown
# Caso: <apelido SEM nome real>            ← pseudonimizar SEMPRE (guarda LGPD no pytest)
- Origem: exemplo do professor (vídeo+mm:ss) | projeto real (data)
- Tomador: PF|PJ · porte · município/UF (região pode ficar)
- Atividades: ex. café conilon sequeiro 10ha + leite 50 matrizes
- Pedido: finalidade (investimento/custeio), valor, prazo/carência pretendidos

## Entradas (dados que o cliente forneceu)
## Enquadramento decidido (linha, porte, taxa — e POR QUÊ)
## Decisões técnicas (coeficientes usados + fonte; o que foi recotado)
## Saídas (números-chave do projeto: receitas, custos, capacidade, % utilização)
## Resultado no banco (aprovado/exigências/negado — preencher depois do protocolo)
## Lições (o que este caso ensina para os próximos)
```

## Regras
1. **Pseudonimização obrigatória**: nome/CPF/CNPJ reais NUNCA entram aqui (dados completos
   ficam fora do git, em materiais/ ou no arquivo do projetista). O teste
   `tests/test_lgpd.py` varre esta pasta.
2. Todo número com selo e fonte, como no resto da base.
3. O "Resultado no banco" é o campo mais valioso — voltar e preencher SEMPRE.
4. Casos derivados dos exemplos do professor: `2026-06-exemplo-leite-cafe.md` etc.,
   criados na Fase 2/4 a partir dos goldens.
