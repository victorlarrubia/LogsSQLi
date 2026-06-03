# LogsSQLi - Prompt de Teste do Dashboard no Google AI Studio

## Objetivo
Este prompt operacional é utilizado para enviar ao Gemini um recorte do dashboard do projeto **LogsSQLi**, permitindo gerar um parecer executivo baseado nos dados atuais.

Ele deve ser usado em conjunto com o **System Prompt** salvo em `prompts/system_prompt_gemini.md`.

---

## Prompt Base

Analise o seguinte recorte do projeto LogsSQLi e gere um parecer executivo rigorosamente baseado nos dados fornecidos.

Contexto:
Este projeto transforma logs HTTP em apoio à decisão para identificar padrões suspeitos de SQL Injection, priorizar endpoints críticos e apoiar ações operacionais e gerenciais.

Recorte atual do dashboard:
- Logs avaliados: [INSERIR]
- Logs com alerta SQLi: [INSERIR]
- Percentual de logs com alerta: [INSERIR]
- Parâmetros avaliados: [INSERIR]
- Parâmetros classificados como SQLi: [INSERIR]

Filtros aplicados:
- Métodos HTTP: [INSERIR]
- Status HTTP: [INSERIR]
- Endpoints: [INSERIR]
- Faixas de risco: [INSERIR]

Resumo adicional:
- Endpoint com maior concentração de alertas: [INSERIR]
- Outros pontos relevantes do dashboard: [INSERIR]
- A análise considera resultados do dashboard, da simulação OLAP e da classificação binária de parâmetros suspeitos

Instruções obrigatórias:
1. Separe claramente fatos observados e hipóteses.
2. Não afirme comprometimento, exploração bem-sucedida, vazamento de dados ou bypass de autenticação sem evidência explícita.
3. Quando algo depender de validação adicional, escreva isso de forma explícita.
4. Priorize linguagem executiva, objetiva e sem alarmismo.
5. Baseie-se apenas nas informações fornecidas neste prompt.

Formato da resposta:
- Fatos observados
- Hipóteses e pontos de atenção
- Prioridades de investigação
- Recomendações práticas
- Impacto potencial para o negócio

---

## Exemplo preenchido com o recorte atual

Analise o seguinte recorte do projeto LogsSQLi e gere um parecer executivo rigorosamente baseado nos dados fornecidos.

Contexto:
Este projeto transforma logs HTTP em apoio à decisão para identificar padrões suspeitos de SQL Injection, priorizar endpoints críticos e apoiar ações operacionais e gerenciais.

Recorte atual do dashboard:
- Logs avaliados: 3626
- Logs com alerta SQLi: 1083
- Percentual de logs com alerta: 29,87%
- Parâmetros avaliados: 3627
- Parâmetros classificados como SQLi: 1083

Filtros aplicados:
- Métodos HTTP: GET e POST
- Status HTTP: 200 e 401
- Endpoints: /rest/products/search e /rest/user/login
- Faixas de risco: Alto e Muito_baixo

Resumo adicional:
- Endpoint com maior concentração de alertas: GET /rest/products/search
- Há também eventos no endpoint /rest/user/login
- A análise considera resultados do dashboard, da simulação OLAP e da classificação binária de parâmetros suspeitos

Instruções obrigatórias:
1. Separe claramente fatos observados e hipóteses.
2. Não afirme comprometimento, exploração bem-sucedida, vazamento de dados ou bypass de autenticação sem evidência explícita.
3. Quando algo depender de validação adicional, escreva isso de forma explícita.
4. Priorize linguagem executiva, objetiva e sem alarmismo.
5. Baseie-se apenas nas informações fornecidas neste prompt.

Formato da resposta:
- Fatos observados
- Hipóteses e pontos de atenção
- Prioridades de investigação
- Recomendações práticas
- Impacto potencial para o negócio