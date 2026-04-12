# LogsSQLi

Projeto acadêmico da disciplina **Análise de Dados** da **Faculdade Engenheiro Salvador Arena**, com foco na **detecção de SQL Injection (SQLi)** a partir de parâmetros extraídos de logs HTTP do **Nginx** associados à aplicação vulnerável **OWASP Juice Shop**.

> **Status atual:** o projeto já contempla as etapas de **ETL (M1)**, **EDA (M2)** e **Modelagem Preditiva (M3)**. A entrega final da etapa de Machine Learning foi concentrada na **classificação binária** entre `SQLi` e `Nao_SQLi`.

---

## 1. Resumo do problema

O projeto busca transformar **logs HTTP brutos** em uma base analítica capaz de apoiar a identificação de padrões suspeitos relacionados a **SQL Injection**.

Na prática, o objetivo é prever se um parâmetro observado em uma requisição HTTP deve ser classificado como:

- `SQLi`
- `Nao_SQLi`

Para isso, o trabalho foi estruturado em três etapas integradas:

- **M1 — Engenharia de Dados (ETL):** leitura dos logs, parsing da requisição HTTP, expansão da query string, normalização textual e persistência das bases tratadas.
- **M2 — Análise Exploratória de Dados (EDA):** estatística descritiva, análise de distribuições, correlações, outliers e comparação de estratégias iniciais de detecção.
- **M3 — Modelagem Preditiva (ML):** construção das bases supervisionadas, vetorização textual em nível de caractere, treinamento comparativo de redes neurais e aplicação do melhor classificador sobre os parâmetros extraídos dos logs.

---

## 2. Objetivo da modelagem

A etapa de Machine Learning teve como objetivo desenvolver um classificador capaz de identificar padrões textuais compatíveis com **SQL Injection** em parâmetros HTTP extraídos dos logs.

A abordagem adotada foi baseada em **classificação textual supervisionada**, utilizando redes neurais profundas sobre representações em **nível de caractere**, uma vez que payloads SQLi costumam depender fortemente de:

- operadores lógicos;
- aspas;
- comentários;
- funções SQL;
- caracteres especiais;
- pequenas variações sintáticas e tentativas de obfuscação.

A classificação multirrótulo dos **tipos de SQL Injection** também foi testada em caráter exploratório, mas não apresentou desempenho satisfatório com a base atual. Por isso, a entrega final do projeto foi mantida na tarefa de **detecção binária**.

---

## 3. Modelo final escolhido

O modelo final selecionado foi o **`conv1d_bilstm_binario`**, baseado na arquitetura:

**Embedding + Conv1D + MaxPooling1D + BiLSTM + Dense**

Essa arquitetura foi escolhida porque combina:

- **extração de padrões locais** por meio da camada convolucional (`Conv1D`);
- **modelagem sequencial bidirecional** por meio da camada recorrente (`BiLSTM`).

Essa combinação é particularmente adequada para o problema estudado, pois payloads SQLi contêm tanto padrões locais relevantes quanto dependências sequenciais de caracteres.

---

## 4. Tabela comparativa dos modelos

| Modelo | Acurácia | F1-Score | Precisão | Recall | AUC | Tempo de Processamento (ms) |
|---|---:|---:|---:|---:|---:|---:|
| `conv1d_bilstm_binario` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9243.62 |
| `bilstm_binario` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 16408.21 |
| `cnn_binario` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 6168.52 |
| `baseline_binario` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 5961.81 |

---

## 5. Conclusão técnica

Os modelos binários avaliados apresentaram desempenho máximo no conjunto de teste atualmente disponível, com acurácia, precisão, recall, F1-score e AUC iguais a 1,0. Como as métricas finais ficaram empatadas, a escolha do modelo final considerou também a estrutura arquitetural e sua aderência ao problema.

O modelo **`conv1d_bilstm_binario`** foi mantido como solução principal porque oferece um bom equilíbrio entre representação local e sequencial dos textos, sendo mais coerente com payloads curtos, sintaticamente sensíveis e frequentemente ofuscados, como os encontrados em ataques de SQL Injection.

Apesar dos resultados excelentes, a interpretação deve ser feita com cautela. A base atual ainda apresenta limitações importantes, como:

- concentração dos eventos em poucas rotas;
- baixa diversidade de tráfego benigno real;
- classe negativa parcialmente construída com exemplos controlados.

Assim, o desempenho observado é forte para o contexto da base utilizada, mas novas coletas e maior diversidade de dados são recomendadas para fortalecer a generalização do modelo.

---

## 6. Fluxo do pipeline analítico

O projeto foi organizado em um fluxo contínuo que integra **ETL**, **EDA** e **ML**.

### Fluxo do `run_pipeline.sh`

1. converter `logs/access.log` em `data/raw/access_log_structured.csv`;
2. garantir a disponibilidade de `payloads_dataset.csv` em `data/raw`;
3. sincronizar `data/raw` com `gdrive_logsqli:LogsSQLi/data/raw`.

### Fluxo integrado do projeto

#### ETL (M1)
- leitura dos logs estruturados e da base de payloads;
- padronização dos campos;
- parsing da coluna `request`;
- extração de método HTTP, endpoint, query string e protocolo;
- expansão dos parâmetros da query string;
- decodificação e normalização dos valores observados;
- persistência das tabelas tratadas em `data/processed`.

#### EDA (M2)
- estatística descritiva;
- análise de distribuições;
- identificação de outliers;
- correlações entre variáveis;
- comparação de estratégias de detecção de SQLi.

#### ML (M3)
- construção da base supervisionada;
- geração da base binária com exemplos benignos controlados;
- vetorização textual em nível de caractere;
- particionamento treino/validação/teste;
- treinamento e comparação entre arquiteturas neurais;
- escolha do modelo campeão;
- aplicação do modelo final sobre `df_params`;
- consolidação de alertas por parâmetro, requisição, endpoint e status HTTP.

---

## 7. Estrutura do repositório

```text
LogsSQLi/
├── models/
├── notebooks/
├── scripts/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── nginx.conf
└── payloads_dataset.csv
```

---

## 8. Principais arquivos

### `notebooks/ETL_e_EDA_Case_LogsSQLi.ipynb`

Notebook responsável pelas etapas de:

- carga das bases;
- parsing dos logs;
- expansão de parâmetros;
- normalização textual;
- consolidação da dimensão de payloads;
- construção da base analítica;
- análise exploratória dos dados.

### `notebooks/ML_Case_LogsSQLi.ipynb`

Notebook responsável por:

- preparação supervisionada das bases de treino;
- vetorização textual;
- treinamento e comparação dos modelos binários;
- curva ROC/AUC;
- análise de robustez do modelo campeão;
- aplicação do melhor classificador sobre `df_params`;
- geração de alertas e consolidações finais.

### `models/`

Contém os modelos treinados exportados em formato `.keras`.

### `scripts/run_pipeline.sh`

Script que organiza a execução inicial do pipeline de dados.

### `scripts/convert_access_to_csv.py`

Script que converte o `access.log` em uma base estruturada em CSV.

---

## 9. Instruções de reprodução

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd LogsSQLi
```

### 2. Criar e ativar ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Executar os notebooks

Abra os notebooks na pasta notebooks/:
- ETL_e_EDA_Case_LogsSQLi.ipynb
- ML_Case_LogsSQLi.ipynb

A execução dos notebooks foi planejada para ambiente Google Colab, com persistência dos artefatos no Google Drive.

## 10. Dependências principais

As bibliotecas utilizadas no projeto incluem:
- pandas
- numpy
- matplotlib
- scikit-learn
- tensorflow
- odfpy

## 11. Modelos gerados

Os principais modelos binários produzidos nesta etapa foram:
- models/12-04-2026-conv1d_bilstm_binario.keras
- models/12-04-2026-bilstm_binario.keras
- models/12-04-2026-cnn_binario.keras
- models/12-04-2026-baseline_binario.keras

## 12. Ambiente local do projeto

O ambiente local foi estruturado para gerar tráfego controlado e registrar logs HTTP com apoio do OWASP Juice Shop e de um Nginx configurado como proxy reverso.

Arquitetura simplificada

```
Cliente / Navegador / curl
            |
            v
      Nginx (porta 80)
            |
            v
 OWASP Juice Shop (porta 3000 interna)
```

Componentes principais
- OWASP Juice Shop: aplicação vulnerável usada como alvo de tráfego.
- Nginx: proxy reverso responsável por encaminhar requisições e registrar os logs.
- Pasta logs/: diretório local utilizado para armazenar access.log e error.log.

Subida do ambiente local

```
cd /LogsSQLi

mkdir -p logs
docker-compose up -d
docker-compose ps
```
Acesso à aplicação:

- http://localhost
- http://127.0.0.1

Também é possível gerar tráfego com:

```
curl http://localhost
curl "http://localhost/#/login"
curl "http://localhost/rest/products/search?q=apple"
curl "http://localhost/rest/user/login"
```

## 13. Observações metodológicas

Com base nos experimentos realizados:

- a detecção binária de SQLi apresentou desempenho elevado na base atual;
- a vetorização em nível de caractere mostrou-se adequada ao problema;
- as arquiteturas CNN, BiLSTM e CNN + BiLSTM foram testadas;
- a classificação dos tipos de SQLi foi mantida como etapa exploratória, não como entrega final;
- a estrutura do notebook foi organizada para facilitar futuras reexecuções com bases maiores.

## 14. Próximas evoluções previstas

As próximas evoluções do projeto devem priorizar:

- ampliação da base de payloads SQLi;
- aumento da diversidade de tráfego benigno real;
- inclusão de novas rotas e cenários de navegação;
- expansão dos logs com mais tentativas maliciosas e entradas normais;
- reavaliação da robustez do modelo campeão;
- eventual retomada da classificação por tipo de SQL Injection.

## 15. Equipe
- Victor Flohr Costa Bicudo Larrubia - 082210026
- Vitor Dié dos Santos Pereira - 082210023
- Beatriz de Sá Silva - 081210011
- Bruno Hector Wüsthofen - 082210013