from pathlib import Path
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="LogsSQLi Analytics Dashboard",
    page_icon="🛡️",
    layout="wide",
)


# =========================
# Helpers
# =========================
def default_repo_root() -> str:
    return str(Path(__file__).resolve().parents[2])


def latest_file(directory: Path, suffix: str) -> Path | None:
    files = sorted(directory.glob(f"*{suffix}"))
    return files[-1] if files else None


@st.cache_data(show_spinner=False)
def read_csv_safe(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def parse_time_column(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(
        series,
        format="%d/%b/%Y:%H:%M:%S %z",
        errors="coerce",
    )
    if parsed.isna().all():
        parsed = pd.to_datetime(series, errors="coerce")
    return parsed


def build_file_map(repo_root: Path) -> dict:
    processed = repo_root / "data" / "processed"
    experiments = processed / "ml" / "experiments"

    return {
        "processed_dir": processed,
        "experiments_dir": experiments,
        "df_analitica": processed / "df_analitica.csv",
        "df_params": processed / "df_params.csv",
        "df_payload_dim": processed / "df_payload_dim.csv",
        "recomendacoes_modelagem": processed / "recomendacoes_modelagem.csv",
        "df_aplicacao": latest_file(experiments, "-aplicacao_binaria_df_params.csv"),
        "resumo_exec_csv": latest_file(experiments, "-resumo_executivo_case.csv"),
        "resumo_exec_txt": latest_file(experiments, "-resumo_executivo_case.txt"),
        "resumo_endpoint": latest_file(experiments, "-resumo_por_endpoint.csv"),
        "resumo_status": latest_file(experiments, "-resumo_por_status.csv"),
        "comparativo_modelos": latest_file(experiments, "-comparativo_modelos_binarios.csv"),
        "comparativo_modelos_resumo": latest_file(experiments, "-comparativo_modelos_binarios_resumo.csv"),
        "top20_endpoints": latest_file(experiments, "-top20_endpoints_alerta.csv"),
        "alertas_por_log": latest_file(experiments, "-alertas_por_log.csv"),
    }


def format_int(value) -> str:
    try:
        return f"{int(value):,}".replace(",", ".")
    except Exception:
        return str(value)


def format_pct(value) -> str:
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return str(value)


def prepare_application_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    numeric_cols = [
        "proba_sqli",
        "pred_sqli_binario",
        "request_time",
        "body_bytes_sent",
        "param_value_raw_length",
        "param_value_decoded_length",
        "status",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "status" in df.columns:
        df["status"] = df["status"].fillna(0).astype(int).astype(str)

    if "pred_sqli_binario" in df.columns:
        df["pred_sqli_binario"] = df["pred_sqli_binario"].fillna(0).astype(int)

    if "proba_sqli" in df.columns:
        df["proba_sqli"] = df["proba_sqli"].fillna(0.0)

    if "faixa_risco" in df.columns:
        df["faixa_risco"] = df["faixa_risco"].fillna("Nao_informado").astype(str)

    if "classe_prevista" in df.columns:
        df["classe_prevista"] = df["classe_prevista"].fillna("Nao_informado").astype(str)

    if "http_method" in df.columns:
        df["http_method"] = df["http_method"].fillna("NA").astype(str)

    if "url_path" in df.columns:
        df["url_path"] = df["url_path"].fillna("NA").astype(str)

    if "param_name_raw" in df.columns:
        df["param_name_raw"] = df["param_name_raw"].fillna("NA").astype(str)

    if "request_success" in df.columns:
        df["request_success"] = df["request_success"].fillna("NA").astype(str)

    if "time_local" in df.columns:
        df["time_local_dt"] = parse_time_column(df["time_local"])
        df["data"] = df["time_local_dt"].dt.date.astype("string")
        df["hora"] = df["time_local_dt"].dt.hour.astype("Int64")

    df["endpoint"] = df["http_method"].astype(str) + " " + df["url_path"].astype(str)

    return df


def apply_filters(df: pd.DataFrame, methods, statuses, endpoints, faixas) -> pd.DataFrame:
    out = df.copy()

    if methods:
        out = out[out["http_method"].isin(methods)]

    if statuses:
        out = out[out["status"].isin(statuses)]

    if endpoints:
        out = out[out["endpoint"].isin(endpoints)]

    if faixas and "faixa_risco" in out.columns:
        out = out[out["faixa_risco"].isin(faixas)]

    return out


def make_endpoint_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    by_log = (
        df.groupby(["endpoint", "log_id"], dropna=False)
        .agg(
            max_pred=("pred_sqli_binario", "max"),
            max_proba=("proba_sqli", "max"),
        )
        .reset_index()
    )

    summary = (
        by_log.groupby("endpoint", dropna=False)
        .agg(
            total_logs=("log_id", "nunique"),
            logs_com_alerta=("max_pred", "sum"),
            maior_proba_sqli=("max_proba", "max"),
            media_proba_sqli=("max_proba", "mean"),
        )
        .sort_values(["logs_com_alerta", "maior_proba_sqli"], ascending=[False, False])
        .reset_index()
    )

    return summary


def make_status_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    by_log = (
        df.groupby(["status", "log_id"], dropna=False)
        .agg(
            max_pred=("pred_sqli_binario", "max"),
            max_proba=("proba_sqli", "max"),
        )
        .reset_index()
    )

    summary = (
        by_log.groupby("status", dropna=False)
        .agg(
            total_logs=("log_id", "nunique"),
            logs_com_alerta=("max_pred", "sum"),
            maior_proba_sqli=("max_proba", "max"),
            media_proba_sqli=("max_proba", "mean"),
        )
        .sort_values(["logs_com_alerta", "status"], ascending=[False, True])
        .reset_index()
    )

    return summary


def make_timeline_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "time_local_dt" not in df.columns:
        return pd.DataFrame()

    work = df.dropna(subset=["time_local_dt"]).copy()
    if work.empty:
        return pd.DataFrame()

    work["data_ref"] = work["time_local_dt"].dt.floor("D")

    by_log = (
        work.groupby(["data_ref", "log_id"], dropna=False)
        .agg(max_pred=("pred_sqli_binario", "max"))
        .reset_index()
    )

    summary = (
        by_log.groupby("data_ref", dropna=False)
        .agg(
            total_logs=("log_id", "nunique"),
            logs_com_alerta=("max_pred", "sum"),
        )
        .reset_index()
        .sort_values("data_ref")
    )

    summary["data_ref"] = summary["data_ref"].astype(str)
    return summary


def build_pivot(df: pd.DataFrame, row_dim: str, col_dim: str, metric: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    if metric == "Contagem de logs":
        if col_dim == "(sem coluna)":
            out = (
                df.drop_duplicates(subset=[row_dim, "log_id"])
                .groupby(row_dim)
                .size()
                .to_frame("contagem_logs")
                .sort_values("contagem_logs", ascending=False)
            )
            return out

        out = (
            df.drop_duplicates(subset=[row_dim, col_dim, "log_id"])
            .groupby([row_dim, col_dim])
            .size()
            .unstack(fill_value=0)
        )
        return out

    if metric == "Contagem de parâmetros":
        if col_dim == "(sem coluna)":
            out = (
                df.groupby(row_dim)
                .size()
                .to_frame("contagem_parametros")
                .sort_values("contagem_parametros", ascending=False)
            )
            return out

        out = df.groupby([row_dim, col_dim]).size().unstack(fill_value=0)
        return out

    metric_map = {
        "Média de probabilidade SQLi": "proba_sqli",
        "Máxima de probabilidade SQLi": "proba_sqli",
        "Média de tempo de requisição": "request_time",
    }

    value_col = metric_map.get(metric)
    if value_col is None or value_col not in df.columns:
        return pd.DataFrame()

    aggfunc = "mean" if "Média" in metric else "max"

    if col_dim == "(sem coluna)":
        out = (
            df.groupby(row_dim)[value_col]
            .agg(aggfunc)
            .to_frame(metric.lower().replace(" ", "_"))
            .sort_values(by=lambda x: x.columns[0], ascending=False)
        )
        return out

    out = df.pivot_table(
        index=row_dim,
        columns=col_dim,
        values=value_col,
        aggfunc=aggfunc,
        fill_value=0,
    )
    return out


def safe_metric_from_summary(df_summary: pd.DataFrame, key: str):
    if df_summary.empty or "indicador" not in df_summary.columns or "valor" not in df_summary.columns:
        return None

    match = df_summary[df_summary["indicador"].astype(str).str.lower() == key.lower()]
    if match.empty:
        return None
    return match.iloc[0]["valor"]


# =========================
# Sidebar
# =========================
st.title("🛡️ LogsSQLi Analytics Dashboard")
st.caption(
    "Dashboard em Streamlit para análise de logs HTTP, simulação OLAP e apoio à decisão com foco em SQL Injection."
)

st.sidebar.header("⚙️ Configurações")

repo_root_str = st.sidebar.text_input(
    "Raiz do projeto LogsSQLi",
    value=default_repo_root(),
)

repo_root = Path(repo_root_str).expanduser()
files = build_file_map(repo_root)

st.sidebar.subheader("Arquivos detectados")
st.sidebar.write("**Processed:**")
st.sidebar.code(str(files["processed_dir"]))
st.sidebar.write("**Experiments:**")
st.sidebar.code(str(files["experiments_dir"]))

with st.sidebar.expander("Ver caminhos esperados"):
    for key, path in files.items():
        if key.endswith("_dir"):
            continue
        st.write(f"**{key}**")
        st.code(str(path) if path else "Nao encontrado")

# =========================
# Leitura dos dados
# =========================
required = {
    "df_aplicacao": files["df_aplicacao"],
    "comparativo_modelos": files["comparativo_modelos"],
    "resumo_exec_csv": files["resumo_exec_csv"],
}

missing_required = [k for k, v in required.items() if v is None or not Path(v).exists()]

if missing_required:
    st.error(
        "Ainda não encontrei todos os artefatos principais do dashboard. "
        f"Pendentes: {', '.join(missing_required)}"
    )
    st.stop()

df_aplicacao = prepare_application_df(read_csv_safe(files["df_aplicacao"]))
df_comparativo = read_csv_safe(files["comparativo_modelos"])
df_resumo_exec = read_csv_safe(files["resumo_exec_csv"])

df_recomendacoes = (
    read_csv_safe(files["recomendacoes_modelagem"])
    if files["recomendacoes_modelagem"] and Path(files["recomendacoes_modelagem"]).exists()
    else pd.DataFrame()
)

resumo_txt = ""
if files["resumo_exec_txt"] and Path(files["resumo_exec_txt"]).exists():
    resumo_txt = Path(files["resumo_exec_txt"]).read_text(encoding="utf-8", errors="ignore")

# =========================
# Filtros globais
# =========================
st.sidebar.subheader("Filtros globais")

method_options = sorted(df_aplicacao["http_method"].dropna().astype(str).unique().tolist())
status_options = sorted(df_aplicacao["status"].dropna().astype(str).unique().tolist())
endpoint_options = sorted(df_aplicacao["endpoint"].dropna().astype(str).unique().tolist())
faixa_options = sorted(df_aplicacao["faixa_risco"].dropna().astype(str).unique().tolist())

selected_methods = st.sidebar.multiselect(
    "Método HTTP",
    options=method_options,
    default=method_options,
)

selected_status = st.sidebar.multiselect(
    "Status HTTP",
    options=status_options,
    default=status_options,
)

selected_endpoints = st.sidebar.multiselect(
    "Endpoint",
    options=endpoint_options,
    default=endpoint_options,
)

selected_faixas = st.sidebar.multiselect(
    "Faixa de risco",
    options=faixa_options,
    default=faixa_options,
)

df_filtered = apply_filters(
    df_aplicacao,
    selected_methods,
    selected_status,
    selected_endpoints,
    selected_faixas,
)

if df_filtered.empty:
    st.warning("Os filtros atuais não retornaram registros. Ajuste os filtros laterais.")
    st.stop()

# =========================
# Métricas derivadas
# =========================
logs_avaliados = df_filtered["log_id"].nunique()
logs_com_alerta = df_filtered.loc[df_filtered["pred_sqli_binario"] == 1, "log_id"].nunique()
params_avaliados = len(df_filtered)
params_classificados = int(df_filtered["pred_sqli_binario"].sum())
pct_logs_alerta = (logs_com_alerta / logs_avaliados * 100) if logs_avaliados else 0.0

endpoint_summary = make_endpoint_summary(df_filtered)
status_summary = make_status_summary(df_filtered)
timeline_summary = make_timeline_summary(df_filtered)

# =========================
# Tabs
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Visão executiva",
        "Simulação OLAP",
        "Modelagem",
        "Exploração detalhada",
        "GenAI",
    ]
)

# =========================
# TAB 1 - Visão executiva
# =========================
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Logs avaliados", format_int(logs_avaliados))
    c2.metric("Logs com alerta SQLi", format_int(logs_com_alerta), delta=f"{pct_logs_alerta:.2f}%")
    c3.metric("Parâmetros avaliados", format_int(params_avaliados))
    c4.metric("Parâmetros classificados como SQLi", format_int(params_classificados))

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top endpoints com mais alertas SQLi")
        if not endpoint_summary.empty:
            chart_ep = endpoint_summary.head(10).set_index("endpoint")[["logs_com_alerta"]]
            st.bar_chart(chart_ep, use_container_width=True)
            st.dataframe(endpoint_summary.head(10), use_container_width=True)
        else:
            st.info("Sem dados suficientes para resumo por endpoint.")

    with col_b:
        st.subheader("Distribuição por status HTTP")
        if not status_summary.empty:
            chart_status = status_summary.set_index("status")[["logs_com_alerta"]]
            st.bar_chart(chart_status, use_container_width=True)
            st.dataframe(status_summary, use_container_width=True)
        else:
            st.info("Sem dados suficientes para resumo por status.")

    st.divider()

    st.subheader("Evolução temporal de logs e alertas")
    if not timeline_summary.empty:
        chart_time = timeline_summary.set_index("data_ref")[["total_logs", "logs_com_alerta"]]
        st.line_chart(chart_time, use_container_width=True)
        st.dataframe(timeline_summary, use_container_width=True)
    else:
        st.info("Não foi possível construir a série temporal com os dados atuais.")

    st.divider()
    st.subheader("Resumo executivo do caso")
    st.dataframe(df_resumo_exec, use_container_width=True)

# =========================
# TAB 2 - Simulação OLAP
# =========================
with tab2:
    st.subheader("Slicing, dicing e drill-down")

    available_dims = [
        col
        for col in [
            "http_method",
            "url_path",
            "status",
            "faixa_risco",
            "classe_prevista",
            "param_name_raw",
            "request_success",
        ]
        if col in df_filtered.columns
    ]

    olap_col1, olap_col2, olap_col3 = st.columns(3)

    with olap_col1:
        row_dim = st.selectbox("Dimensão de linha", options=available_dims, index=0)

    with olap_col2:
        col_dim = st.selectbox(
            "Dimensão de coluna",
            options=["(sem coluna)"] + available_dims,
            index=1 if len(available_dims) > 1 else 0,
        )

    with olap_col3:
        metric = st.selectbox(
            "Métrica",
            options=[
                "Contagem de logs",
                "Contagem de parâmetros",
                "Média de probabilidade SQLi",
                "Máxima de probabilidade SQLi",
                "Média de tempo de requisição",
            ],
            index=0,
        )

    pivot = build_pivot(df_filtered, row_dim, col_dim, metric)

    st.write("### Tabela OLAP")
    if not pivot.empty:
        st.dataframe(pivot, use_container_width=True)
        if col_dim == "(sem coluna)" and pivot.shape[1] == 1:
            st.write("### Visualização rápida")
            st.bar_chart(pivot, use_container_width=True)
    else:
        st.warning("Não foi possível montar a tabela OLAP com a combinação atual.")

    st.divider()

    st.write("### Drill-down por endpoint e log")
    endpoint_choice = st.selectbox(
        "Selecione um endpoint para detalhar",
        options=sorted(df_filtered["endpoint"].unique().tolist()),
    )

    endpoint_df = df_filtered[df_filtered["endpoint"] == endpoint_choice].copy()

    ranked_logs = (
        endpoint_df.groupby("log_id")
        .agg(
            max_proba_sqli=("proba_sqli", "max"),
            qtd_parametros=("log_id", "size"),
        )
        .sort_values(["max_proba_sqli", "qtd_parametros"], ascending=[False, False])
        .reset_index()
    )

    selected_log = st.selectbox(
        "Selecione um log_id",
        options=ranked_logs["log_id"].tolist(),
    )

    st.dataframe(ranked_logs.head(20), use_container_width=True)

    drill_cols = [
        c
        for c in [
            "log_id",
            "time_local",
            "http_method",
            "url_path",
            "status",
            "param_position",
            "param_name_raw",
            "param_value_raw",
            "param_value_decoded",
            "proba_sqli",
            "pred_sqli_binario",
            "classe_prevista",
            "faixa_risco",
        ]
        if c in endpoint_df.columns
    ]

    st.write("### Detalhamento do log selecionado")
    st.dataframe(
        endpoint_df[endpoint_df["log_id"] == selected_log][drill_cols],
        use_container_width=True,
    )

# =========================
# TAB 3 - Modelagem
# =========================
with tab3:
    st.subheader("Comparação de modelos binários")

    metric_cols = [
        "accuracy",
        "precision",
        "recall",
        "auc",
        "f1",
        "tempo_segundos",
        "epochs_trained",
    ]
    for col in metric_cols:
        if col in df_comparativo.columns:
            df_comparativo[col] = pd.to_numeric(df_comparativo[col], errors="coerce")

    champion_row = (
        df_comparativo.sort_values(["f1", "auc", "accuracy"], ascending=[False, False, False]).iloc[0]
        if not df_comparativo.empty
        else None
    )

    if champion_row is not None:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Modelo campeão", str(champion_row.get("model_name", "N/A")))
        m2.metric("F1", f"{float(champion_row.get('f1', 0)):.4f}")
        m3.metric("AUC", f"{float(champion_row.get('auc', 0)):.4f}")
        m4.metric("Accuracy", f"{float(champion_row.get('accuracy', 0)):.4f}")

    st.dataframe(df_comparativo, use_container_width=True)

    selected_model_metric = st.selectbox(
        "Escolha a métrica para comparação",
        options=["accuracy", "precision", "recall", "auc", "f1", "tempo_segundos"],
        index=4,
    )

    if selected_model_metric in df_comparativo.columns:
        model_chart = (
            df_comparativo[["model_name", selected_model_metric]]
            .dropna()
            .set_index("model_name")
            .sort_values(selected_model_metric, ascending=False)
        )
        st.bar_chart(model_chart, use_container_width=True)

    if champion_row is not None:
        st.write("### Detalhamento do modelo campeão")
        champion_df = pd.DataFrame(champion_row).reset_index()
        champion_df.columns = ["atributo", "valor"]
        st.dataframe(champion_df, use_container_width=True)

    if not df_recomendacoes.empty:
        st.write("### Recomendações de modelagem")
        st.dataframe(df_recomendacoes, use_container_width=True)

# =========================
# TAB 4 - Exploração detalhada
# =========================
with tab4:
    st.subheader("Exploração detalhada dos parâmetros")

    risky_only = st.checkbox("Mostrar apenas parâmetros classificados como SQLi", value=False)

    detail_df = df_filtered.copy()
    if risky_only:
        detail_df = detail_df[detail_df["pred_sqli_binario"] == 1]

    top_params = (
        detail_df.groupby(["endpoint", "param_name_raw"], dropna=False)
        .agg(
            total_parametros=("log_id", "size"),
            alertas=("pred_sqli_binario", "sum"),
            media_proba_sqli=("proba_sqli", "mean"),
            max_proba_sqli=("proba_sqli", "max"),
        )
        .sort_values(["alertas", "max_proba_sqli", "total_parametros"], ascending=[False, False, False])
        .reset_index()
    )

    st.write("### Top combinações endpoint + parâmetro")
    st.dataframe(top_params.head(20), use_container_width=True)

    if not top_params.empty:
        top_param_chart = top_params.head(15).copy()
        top_param_chart["endpoint_param"] = (
            top_param_chart["endpoint"].astype(str) + " | " + top_param_chart["param_name_raw"].astype(str)
        )
        st.bar_chart(
            top_param_chart.set_index("endpoint_param")[["alertas"]],
            use_container_width=True,
        )

    st.write("### Base detalhada filtrada")
    ordered_cols = [
        c
        for c in [
            "log_id",
            "time_local",
            "http_method",
            "url_path",
            "status",
            "param_position",
            "param_name_raw",
            "param_value_raw",
            "param_value_decoded",
            "request_time",
            "proba_sqli",
            "pred_sqli_binario",
            "classe_prevista",
            "faixa_risco",
        ]
        if c in detail_df.columns
    ]

    st.dataframe(detail_df[ordered_cols], use_container_width=True)

    csv_export = detail_df[ordered_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Baixar recorte atual em CSV",
        data=csv_export,
        file_name="recorte_dashboard_logssqli.csv",
        mime="text/csv",
    )

# =========================
# TAB 5 - GenAI
# =========================
with tab5:
    st.subheader("Agente de Insight - conteúdo para Google AI Studio")

    resumo_gerado = resumo_txt.strip()
    if not resumo_gerado:
        resumo_gerado = (
            f"Logs avaliados: {logs_avaliados}\n"
            f"Logs com alerta SQLi: {logs_com_alerta}\n"
            f"Percentual de logs com alerta: {pct_logs_alerta:.2f}%\n"
            f"Parâmetros avaliados: {params_avaliados}\n"
            f"Parâmetros classificados como SQLi: {params_classificados}\n"
        )

    st.write("### Resumo executivo disponível")
    st.text_area(
        "Resumo do caso",
        value=resumo_gerado,
        height=220,
    )

    prompt = f"""Você é um consultor especializado em analytics de segurança, observabilidade e risco operacional, com foco em detecção de SQL Injection a partir de logs HTTP.

Contexto do projeto:
- Projeto: LogsSQLi
- Objetivo: transformar logs HTTP em apoio à decisão para identificar padrões suspeitos, priorizar endpoints críticos e apoiar ações preventivas.

Recorte atual do dashboard:
- Logs avaliados: {logs_avaliados}
- Logs com alerta SQLi: {logs_com_alerta}
- Percentual de logs com alerta: {pct_logs_alerta:.2f}%
- Parâmetros avaliados: {params_avaliados}
- Parâmetros classificados como SQLi: {params_classificados}
- Métodos filtrados: {", ".join(selected_methods) if selected_methods else "Todos"}
- Status filtrados: {", ".join(selected_status) if selected_status else "Todos"}
- Endpoints filtrados: {", ".join(selected_endpoints[:10]) if selected_endpoints else "Todos"}

Resumo executivo:
{resumo_gerado}

Sua tarefa:
1. Interpretar os principais sinais do recorte analisado.
2. Identificar riscos prioritários para o negócio e para a operação.
3. Indicar quais endpoints ou padrões merecem investigação imediata.
4. Sugerir ações práticas de mitigação, monitoramento e resposta.
5. Explicar o impacto operacional e estratégico dos achados em linguagem executiva.
6. Responder em português do Brasil, com objetividade, clareza e foco em decisão.

Formato da resposta:
- Diagnóstico do cenário
- Principais riscos
- Prioridades de investigação
- Recomendações de ação
- Impacto para o negócio
"""

    st.write("### Prompt pronto para colar no Google AI Studio")
    st.code(prompt, language="markdown")