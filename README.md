# LogsSQLi

> Este documento descreve o estado atual do projeto e será refinado conforme novas etapas forem concluídas.

## 1. Visão geral

O **LogsSQLi** é um projeto acadêmico da disciplina **Análise de Dados**, da **Faculdade Engenheiro Salvador Arena**, voltado à **coleta, estruturação, análise e modelagem preditiva de logs HTTP** com foco na identificação de padrões associados a **SQL Injection (SQLi)**.

O ambiente foi montado para gerar tráfego controlado em uma aplicação vulnerável (**OWASP Juice Shop**) e registrar esse tráfego por meio de um **Nginx reverso**, que atua como proxy e grava os arquivos de log localmente. A partir desses logs, o projeto evolui para um pipeline analítico com três frentes principais:

- **M1 — Engenharia de Dados (ETL)**  
  Estruturação dos logs brutos, parsing da requisição HTTP, expansão de parâmetros e persistência das tabelas tratadas.
- **M2 — Análise Exploratória de Dados (EDA)**  
  Estatística descritiva, análise de distribuições, correlações, outliers e comparação de estratégias de detecção de SQLi.
- **M3 — Modelagem Preditiva (ML)**  
  Preparação supervisionada das amostras, vetorização textual em nível de caractere, treinamento de modelos neurais e aplicação do melhor classificador sobre os parâmetros extraídos dos logs.

---

## 2. Objetivo do projeto

O objetivo central é construir um pipeline capaz de transformar **logs HTTP brutos** em **bases analíticas úteis** para detectar requisições suspeitas e apoiar o estudo de padrões relacionados a ataques de **SQL Injection**.

De forma prática, o projeto busca:

- subir uma aplicação vulnerável para gerar tráfego web;
- registrar os acessos HTTP em arquivos de log locais;
- converter os logs em estruturas tabulares reutilizáveis;
- enriquecer os dados com atributos derivados da requisição;
- comparar estratégias de detecção de SQLi;
- construir uma base preparada para classificação supervisionada;
- treinar e comparar modelos de Machine Learning / Deep Learning.

---

## 3. Arquitetura do ambiente local

O ambiente local funciona da seguinte forma:

```text
Cliente / Navegador / curl
            |
            v
      Nginx (porta 80)
            |
            v
 OWASP Juice Shop (porta 3000 interna)
```

### Componentes

- **OWASP Juice Shop**  
  Aplicação alvo utilizada para gerar tráfego HTTP e simular requisições realistas em um ambiente controlado.
- **Nginx**  
  Proxy reverso responsável por encaminhar as requisições ao Juice Shop e registrar os logs de acesso.
- **Pasta local `logs/`**  
  Diretório persistido no host para armazenar os arquivos `access.log` e `error.log`.

### Configuração utilizada

- O serviço `juice-shop` usa a imagem `bkimminich/juice-shop`.
- O serviço `nginx-proxy` usa a imagem `nginx:latest`.
- A porta `80` do host é publicada no contêiner do Nginx.
- O arquivo `nginx.conf` é montado como configuração do Nginx.
- A pasta `./logs` é montada em `/var/log/nginx` para persistência dos logs.
- O Nginx faz `proxy_pass` para `http://juice-shop:3000`.
- O formato do `access.log` inclui, entre outros campos, IP, usuário, timestamp, request completa, status, bytes enviados, referer, user-agent e tempo da requisição.

---

## 4. Estrutura atual do projeto

A estrutura abaixo representa a organização esperada do projeto com base no ambiente local, nos notebooks e nos scripts já utilizados:

```text
LogsSQLi/
├── .venv/
├── data/
│   ├── raw/
│   │   ├── access_log_structured.csv
│   │   └── payloads_dataset.csv
│   └── processed/
│       ├── df_analitica.csv
│       ├── df_params.csv
│       ├── df_payload_dim.csv
│       ├── df_match_exato.csv
│       ├── df_match_contains.csv
│       ├── df_params_signature.csv
│       ├── df_estatisticas_numericas.csv
│       ├── df_outliers_iqr.csv
│       ├── comparacao_grupos.csv
│       ├── diferencas_grupos.csv
│       ├── recomendacoes_modelagem.csv
│       └── ml/
│           ├── splits/
│           └── experiments/
├── logs/
│   ├── access.log
│   └── error.log
├── recursos/
├── scripts/
│   ├── convert_access_to_csv.py
│   └── run_pipeline.sh
├── docker-compose.yml
├── nginx.conf
├── ETL_e_EDA_Case_LogsSQLi.ipynb
├── ML_Case_LogsSQLi.ipynb
├── payloads_dataset.csv
└── README.md
```

> **Observação:** alguns diretórios e artefatos são gerados ao longo da execução do pipeline e dos notebooks.

---

## 5. Fontes de dados do projeto

Atualmente, o projeto trabalha com duas fontes principais:

### 5.1 Logs HTTP de acesso

Os logs são gerados localmente a partir do tráfego encaminhado pelo Nginx para o OWASP Juice Shop. O arquivo mais importante nesta etapa é:

- `logs/access.log`

Esse arquivo serve como entrada bruta para o processo de parsing e estruturação.

### 5.2 Base de payloads SQLi

O projeto também utiliza uma base de payloads de referência, consolidada em:

- `payloads_dataset.csv`

Essa base é utilizada para apoiar estratégias de correspondência exata, contenção e consolidação de padrões textuais relacionados a SQL Injection.

---

## 6. Arquivos principais

### `docker-compose.yml`

Responsável por subir os dois serviços do ambiente local:

- `juice-shop`
- `nginx-proxy`

Resumo do comportamento:

- não expõe diretamente a porta do Juice Shop;
- força a passagem do tráfego pelo Nginx;
- publica a porta `80`;
- persiste os logs localmente no diretório `logs/`.

### `nginx.conf`

Define:

- o formato customizado do log;
- o arquivo de saída do `access.log`;
- a escuta na porta `80`;
- o encaminhamento das requisições para `juice-shop:3000`.

### `scripts/convert_access_to_csv.py`

Script responsável por converter o `access.log` em uma base estruturada em CSV, preservando os campos relevantes do log HTTP para as etapas analíticas seguintes.

### `scripts/run_pipeline.sh`

Script que organiza a execução inicial do pipeline, incluindo a conversão dos logs e a movimentação/sincronização dos arquivos para a camada `data/raw`.

### `ETL_e_EDA_Case_LogsSQLi.ipynb`

Notebook que consolida as etapas de:

- carga e validação das bases;
- padronização inicial e criação de variáveis analíticas;
- parsing da linha `request`;
- extração dos parâmetros HTTP;
- normalização e decodificação dos parâmetros;
- consolidação da dimensão de payloads;
- comparação entre estratégias de detecção;
- construção da base analítica final;
- estatística descritiva, outliers, correlações e gráficos;
- persistência das tabelas finais em `data/processed`.

### `ML_Case_LogsSQLi.ipynb`

Notebook que consolida a etapa de modelagem preditiva, incluindo:

- preparação supervisionada da base de treino;
- reconstrução da base binária com negativos controlados;
- vetorização textual em nível de caractere;
- treinamento comparativo de arquiteturas neurais;
- seleção do melhor modelo;
- aplicação do modelo sobre os parâmetros extraídos dos logs;
- consolidação dos alertas por requisição, endpoint e status;
- salvamento dos artefatos de experimento em `data/processed/ml`.

---

## 7. Pré-requisitos

Antes de executar o ambiente local, é necessário ter instalado:

- **Docker**
- **Docker Compose**
- navegador web ou `curl` para gerar tráfego
- ambiente Python para scripts auxiliares e notebooks
- Google Colab / Google Drive, caso a execução dos notebooks siga o mesmo fluxo usado no desenvolvimento atual

### Verificação local

```bash
docker --version
docker-compose --version
python3 --version
```

> Neste ambiente, o comando disponível é **`docker-compose`** e não `docker compose`.

---

## 8. Como subir o ambiente local

### 8.1 Acessar o diretório do projeto

```bash
cd /LogsSQLi
```

### 8.2 Garantir a existência da pasta de logs

```bash
mkdir -p logs
```

### 8.3 Subir os contêineres

```bash
docker-compose up -d
```

### 8.4 Verificar se os serviços estão em execução

```bash
docker-compose ps
```

ou:

```bash
docker ps
```

---

## 9. Como acessar a aplicação

Com o ambiente em execução, acesse no navegador:

```text
http://localhost
```

ou:

```text
http://127.0.0.1
```

Também é possível gerar tráfego com `curl`:

```bash
curl http://localhost
curl "http://localhost/#/login"
curl "http://localhost/rest/products/search?q=apple"
curl "http://localhost/rest/user/login"
```

> Qualquer navegação já contribui para popular o `access.log`.

---

## 10. Logs gerados

Os logs ficam armazenados localmente em:

```text
/LogsSQLi/logs
```

Arquivos esperados:

- `access.log`
- `error.log`

### Acompanhar o log de acesso em tempo real

```bash
tail -f /LogsSQLi/logs/access.log
```

### Acompanhar o log de erro em tempo real

```bash
tail -f /LogsSQLi/logs/error.log
```

### Listar os arquivos do diretório de logs

```bash
ls -lh /LogsSQLi/logs
```

---

## 11. Fluxo do pipeline atual

Com base no fluxo já documentado nos notebooks, o pipeline está organizado da seguinte forma.

### 11.1 Etapa operacional inicial

1. gerar tráfego web no Juice Shop;
2. registrar o tráfego no `logs/access.log`;
3. converter o log para `data/raw/access_log_structured.csv`;
4. garantir a disponibilidade de `payloads_dataset.csv` em `data/raw`.

### 11.2 ETL (M1)

A etapa de engenharia de dados realiza, entre outras atividades:

- leitura do log estruturado;
- leitura da base de payloads;
- padronização de tipos de dados;
- parsing da coluna `request`;
- extração de método HTTP, URL, path, query string e protocolo;
- criação de métricas derivadas de tamanho e estrutura da requisição;
- expansão da query string em parâmetros individuais;
- criação de identificadores técnicos para rastreabilidade;
- decodificação e normalização dos valores observados;
- geração de chaves padronizadas para comparação textual;
- persistência das tabelas intermediárias e finais em `data/processed`.

### 11.3 EDA (M2)

A etapa de análise exploratória contempla:

- estatística descritiva das variáveis numéricas;
- identificação de outliers pela regra do IQR;
- histogramas, boxplots e scatter plots;
- matriz de correlação;
- análise de grupos positivos e negativos;
- comparação entre estratégias de detecção de SQLi.

As estratégias comparadas no projeto incluem:

- **correspondência exata**
- **correspondência por contenção**
- **heurísticas por assinaturas textuais**

### 11.4 ML (M3)

A etapa de modelagem preditiva contempla:

- construção das bases supervisionadas;
- geração de classe negativa controlada;
- vetorização textual em nível de caractere;
- particionamento treino/validação/teste;
- treinamento de modelos binários;
- comparação de arquiteturas neurais;
- análise de estabilidade;
- curva ROC;
- aplicação do melhor modelo sobre os parâmetros extraídos dos logs;
- consolidação de alertas em nível de parâmetro, requisição e endpoint.

---

## 12. Principais tabelas analíticas geradas

Entre os artefatos já previstos ou gerados ao longo do pipeline, destacam-se:

### Camada `data/raw`

- `access_log_structured.csv`
- `payloads_dataset.csv`

### Camada `data/processed`

- `df_params.csv`
- `df_payload_dim.csv`
- `df_match_exato.csv`
- `df_match_contains.csv`
- `df_params_signature.csv`
- `df_analitica.csv`
- `df_estatisticas_numericas.csv`
- `df_outliers_iqr.csv`
- `comparacao_grupos.csv`
- `diferencas_grupos.csv`
- `recomendacoes_modelagem.csv`

### Camada `data/processed/ml`

#### Splits

- `bin_train.csv`
- `bin_val.csv`
- `bin_test.csv`
- `tipo_train.csv`
- `tipo_val.csv`
- `tipo_test.csv`

#### Experimentos

São gerados arquivos como:

- métricas de teste;
- históricos de treinamento;
- relatórios de classificação;
- matrizes de confusão;
- modelos `.keras`;
- inventário de artefatos;
- resumos executivos do case;
- alertas aplicados sobre a base de parâmetros.

---

## 13. Comandos úteis

### Ver logs dos contêineres

```bash
docker-compose logs
```

### Ver logs apenas do Nginx

```bash
docker-compose logs nginx-proxy
```

### Ver logs apenas do Juice Shop

```bash
docker-compose logs juice-shop
```

### Reiniciar os serviços

```bash
docker-compose restart
```

### Parar sem remover

```bash
docker-compose stop
```

### Parar e remover os contêineres

```bash
docker-compose down
```

---

## 14. Execução resumida

A sequência mínima para repetir a etapa de coleta local é:

```bash
cd /LogsSQLi
mkdir -p logs
docker-compose up -d
docker-compose ps
curl http://localhost
tail -f logs/access.log
```

Quando terminar:

```bash
docker-compose down
```

---

## 15. Troubleshooting

### `docker compose` não funciona

Neste ambiente, o comando correto é:

```bash
docker-compose
```

### Porta `80` já está em uso

Verifique com:

```bash
sudo ss -tulpn | grep :80
```

### O log não aparece

Verifique:

- se a pasta `logs/` existe;
- se os contêineres estão em execução;
- se houve tráfego em `http://localhost`;
- se o Nginx subiu corretamente.

Comandos úteis:

```bash
docker-compose ps
docker-compose logs nginx-proxy
ls -lh logs
```

### O navegador não abre a aplicação

Teste:

```bash
docker-compose ps
curl http://localhost
```

---

## 16. Observações metodológicas atuais

Com base no desenvolvimento já realizado até aqui:

- a base analítica final já permite identificar padrões relevantes de requisições suspeitas;
- a estratégia heurística baseada em assinaturas mostrou utilidade importante na base atual;
- variáveis como comprimento do payload decodificado, volume retornado e quantidade de assinaturas acionadas mostraram potencial analítico;
- a etapa de ML foi estruturada como **detecção binária de SQLi**;
- os resultados atuais são promissores, mas ainda exigem cautela quanto à generalização, pois a base precisa de maior diversidade de tráfego benigno e malicioso.

---

## 17. Próximas evoluções previstas

As próximas etapas devem priorizar:

- ampliação da base de logs;
- enriquecimento do catálogo de payloads;
- aumento da variedade de tráfego benigno;
- inclusão de novas variações de SQLi com obfuscação e codificação;
- refinamento da rotulagem;
- fortalecimento da generalização dos modelos;
- eventual retomada da classificação por tipo de SQLi, além da detecção binária.

---

## 18. Status do documento

Este README é **provisório** e foi construído para registrar o estado atual do projeto, servindo como base para evolução da documentação.

Nas próximas versões, este arquivo poderá incorporar:

- instruções completas de instalação;
- dependências Python detalhadas;
- diagrama visual da arquitetura;
- explicação linha a linha dos scripts;
- descrição formal do dicionário de dados;
- resultados consolidados de ETL, EDA e ML;
- orientações de reprodução integral do case.

---

## 19. Equipe
- Victor Flohr Costa Bicudo Larrubia - 082210026
- Vitor Dié dos Santos Pereira - 082210023
- Beatriz de Sá Silva - 081210011
- Bruno Hector Wüsthofen - 082210013