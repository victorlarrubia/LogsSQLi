# Validação do Agente de Insight no Google AI Studio

## Objetivo
Registrar a configuração, o teste funcional e a limitação observada no compartilhamento do agente de insight do projeto **LogsSQLi** no Google AI Studio.

---

## 1. Finalidade do agente
O agente foi configurado para atuar como um consultor de negócios e segurança, com foco em:

- análise de indicadores do dashboard do projeto LogsSQLi;
- interpretação de padrões suspeitos de SQL Injection (SQLi);
- priorização de endpoints críticos;
- apoio à tomada de decisão operacional e gerencial.

---

## 2. Configuração realizada
O agente foi configurado no **Google AI Studio** com:

- instrução de sistema específica para o projeto;
- resposta em português do Brasil;
- foco em linguagem executiva, objetiva e sem alarmismo;
- regra explícita para separar fatos observados e hipóteses;
- restrição para não afirmar comprometimento, vazamento ou bypass sem evidência.

O conteúdo da instrução de sistema foi versionado no repositório em:

```text
prompts/system_prompt_gemini.md