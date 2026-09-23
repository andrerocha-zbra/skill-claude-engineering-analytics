"""Gera um notebook .ipynb novo (esqueleto Silver/Gold/Bronze), pronto para editar.

Promove a "receita" que hoje so existe em prosa (referencia de mecanismos + template
NB_DEV_DEFAULT.ipynb) a um gerador real: cria um .ipynb valido (nbformat 4, source como
lista de linhas, sem outputs, execution_count null -- ja import-safe por construcao, ver
limpar_notebook_import.py para notebooks EDITADOS depois) com as 11 secoes padrao, celula
de parametros no formato certo por cloud, Spark configs, esqueleto Spark-SQL-first (cadeia
de temp views com marcadores "-- TODO:"), quality gates Tier 1 (raise) e Tier 2 (aviso),
write Delta FULL/MERGE e checklist final.

Client-agnostico: nada de nome de cliente/empresa hardcoded -- tudo vem de argumento.

Uso:
    python novo_notebook.py --camada silver --entidade doador --dominio doadores \\
        --cloud fabric --saida datalake/_tech-sync/silver/doador/NB_SILVER_DOADOR.ipynb

    python novo_notebook.py --camada gold --entidade recorrencia_mensal --dominio doadores \\
        --cloud fabric --saida datalake/_tech-sync/gold/recorrencia_mensal/NB_GOLD_RECORRENCIA_MENSAL.ipynb \\
        --registrar-csv datalake/_tech-sync/metadata_driven/metadata_driven_orchestration.csv
"""
import argparse
import json
import re
import unicodedata
import uuid
from datetime import date
from pathlib import Path

COLUNAS_CSV = [
    "is_active", "execution_order", "layer", "domain", "subdomain", "ddd_type",
    "business_entity", "notebook_name", "owner", "source_system", "business_definition",
    "primary_key", "target_schema", "target_table", "load_method", "watermark_enabled",
    "watermark_column", "watermark_start_value", "watermark_lookback_days", "env",
    "timeout_minutes", "retry_count", "notebook_id",
]

SPARK_CONFIGS = """# Configuracoes legadas de leitura Parquet (datas historicas/INT96 de origens espelhadas).
spark.conf.set("spark.sql.parquet.datetimeRebaseModeInRead", "LEGACY")
spark.conf.set("spark.sql.parquet.int96RebaseModeInRead", "LEGACY")

# Adaptive Query Execution: reduz shuffle, coalesce particoes e trata skew em joins.
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")"""

IMPORTS_PADRAO = """from pyspark.sql import functions as F
from pyspark.sql.window import Window
from delta.tables import DeltaTable"""


# ------------------------------------------------------------------ helpers de identificador

def slug_identificador(nome: str) -> str:
    """Normaliza um nome livre (com espaco/acento) para um identificador Python seguro,
    minusculo, sem acento -- notebooks deste padrao ficam 100% ASCII (import-safe)."""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    limpo = re.sub(r"[^a-zA-Z0-9]+", "_", sem_acento).strip("_").lower()
    return limpo or "entidade"


# ------------------------------------------------------------------ helpers de celula ipynb

def _linhas(texto: str) -> list:
    # Convencao nbformat: toda linha termina em "\n", exceto a ultima. rstrip evita que um
    # texto de template com \n final vire uma linha vazia extra na lista.
    return texto.rstrip("\n").splitlines(keepends=True)


def celula_markdown(texto: str) -> dict:
    return {"cell_type": "markdown", "id": str(uuid.uuid4()), "metadata": {}, "source": _linhas(texto)}


def celula_codigo(texto: str, tags=None) -> dict:
    metadata = {"tags": tags} if tags else {}
    return {
        "cell_type": "code",
        "id": str(uuid.uuid4()),
        "metadata": metadata,
        "execution_count": None,
        "outputs": [],
        "source": _linhas(texto),
    }


# ------------------------------------------------------------------ metadata do notebook por cloud

def metadata_notebook(cloud: str) -> dict:
    if cloud == "fabric":
        return {
            "kernelspec": {"display_name": "Synapse PySpark", "language": "Python", "name": "synapse_pyspark"},
            "language_info": {"name": "python"},
            "microsoft": {"language": "python", "language_group": "synapse_pyspark"},
            "spark_compute": {"compute_id": "/trident/default", "session_options": {"conf": {}}},
            # TODO: preencher known_lakehouses/default_lakehouse* ao abrir este notebook no
            # workspace Fabric de destino (o Fabric reescreve este bloco sozinho ao salvar).
            "dependencies": {
                "lakehouse": {
                    "known_lakehouses": [{"id": "TODO-lakehouse-guid"}],
                    "default_lakehouse": "TODO-lakehouse-guid",
                    "default_lakehouse_name": "TODO_lakehouse",
                    "default_lakehouse_workspace_id": "TODO-workspace-guid",
                },
                "environment": {},
            },
        }
    return {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }


# ------------------------------------------------------------------ blocos de parametros por cloud

def celulas_parametros(cloud: str, camada: str, dominio: str, entidade: str, entidade_slug: str) -> list:
    md = celula_markdown(
        "#### Parametros e ambiente\n\n"
        "Parametros de execucao (injetados por pipeline/orquestracao em runtime) e "
        "configuracao de ambiente/destino. Grupo domain-driven mapeia direto para as "
        "colunas do CSV de orquestracao metadata-driven."
    )
    if cloud == "fabric":
        texto_param = (
            '# Main Conditions\n'
            'ENV = "DEV"\n'
            'IS_ACTIVE = True\n'
            '\n'
            '# Domain-driven\n'
            f'DOMAIN = "{dominio}"\n'
            'OWNER = "TODO"\n'
            'SUBDOMAIN = "TODO"\n'
            f'BUSINESS_ENTITY = "{entidade}"\n'
            'DDD_TYPE = "Entity"  # Entity|Aggregate|ValueObject|Event|Service\n'
            '\n'
            '# Catalog\n'
            'LAKEHOUSE = "TODO_lakehouse"\n'
            'SOURCE_SCHEMA = "TODO_schema_espelhado"\n'
            f'TARGET_SCHEMA = "TODO_{camada}_schema"\n'
            f'TARGET_TABLE = "{entidade_slug}"\n'
            'PRIMARY_KEY = "TODO_pk"          # pipe "|" se chave composta, ex: "id_a|id_b"\n'
            'SOURCE_SYSTEM = "TODO_sistema"   # pipe "|" se multiplas origens\n'
            '\n'
            '# Ingestion\n'
            'LOAD_METHOD = "FULL"             # FULL | MERGE | APPEND -- normalmente vem do CSV metadata-driven\n'
            'TIMEZONE = "America/Sao_Paulo"\n'
            'WATERMARK_ENABLED = False\n'
            'WATERMARK_COLUMN = "TODO"\n'
            'WATERMARK_START_VALUE = "1900-01-01 00:00:00"\n'
            'WATERMARK_LOOKBACK_DAYS = 1'
        )
        celula_param = celula_codigo(texto_param, tags=["parameters"])
        celula_convert = celula_codigo(
            '# Papermill/Fabric injeta a celula acima como texto puro; listas chegam pipe-separated.\n'
            'PRIMARY_KEY = PRIMARY_KEY.split("|")\n'
            'SOURCE_SYSTEM = SOURCE_SYSTEM.split("|")'
        )
        return [md, celula_param, celula_convert]

    texto_param = (
        '# Databricks nao tem celula "tags: parameters" -- o equivalente e dbutils.widgets.\n'
        'dbutils.widgets.text("ENV", "DEV")\n'
        f'dbutils.widgets.text("DOMAIN", "{dominio}")\n'
        f'dbutils.widgets.text("BUSINESS_ENTITY", "{entidade}")\n'
        'dbutils.widgets.text("CATALOG", "TODO_catalog")           # Unity Catalog: catalog.schema.tabela\n'
        f'dbutils.widgets.text("TARGET_SCHEMA", "TODO_{camada}_schema")\n'
        f'dbutils.widgets.text("TARGET_TABLE", "{entidade_slug}")\n'
        'dbutils.widgets.text("PRIMARY_KEY", "TODO_pk")            # pipe "|" se chave composta\n'
        'dbutils.widgets.text("LOAD_METHOD", "FULL")               # FULL | MERGE | APPEND\n'
        '\n'
        'ENV = dbutils.widgets.get("ENV")\n'
        'DOMAIN = dbutils.widgets.get("DOMAIN")\n'
        'BUSINESS_ENTITY = dbutils.widgets.get("BUSINESS_ENTITY")\n'
        'CATALOG = dbutils.widgets.get("CATALOG")\n'
        'TARGET_SCHEMA = dbutils.widgets.get("TARGET_SCHEMA")\n'
        'TARGET_TABLE = dbutils.widgets.get("TARGET_TABLE")\n'
        'PRIMARY_KEY = dbutils.widgets.get("PRIMARY_KEY").split("|")\n'
        'LOAD_METHOD = dbutils.widgets.get("LOAD_METHOD")'
    )
    return [md, celula_codigo(texto_param)]


# ------------------------------------------------------------------ montagem do notebook completo

def montar_celulas(camada: str, entidade: str, dominio: str, cloud: str, sistemas_origem: str) -> list:
    entidade_slug = slug_identificador(entidade)
    hoje = date.today().strftime("%d/%m/%Y")
    camada_upper = camada.upper()
    celulas = []

    # 0. Header
    celulas.append(celula_markdown(
        f"# {camada_upper} - {entidade}\n\n"
        "- TODO: descricao da tabela (o que ela representa, grao, regra de negocio central)\n"
        "- Desenvolvido por: TODO\n"
        f"- Criado em {hoje}\n"
        f"- Dominio: {dominio}\n"
        f"- Sistemas de origem: {sistemas_origem}\n\n"
        "Notebook gerado por novo_notebook.py (plugin analytics-project-architect). Esqueleto "
        "a preencher -- ver checklist na ultima celula antes de publicar."
    ))

    # 0b. Historico de atualizacoes
    celulas.append(celula_markdown(
        "### Historico de atualizacoes\n\n"
        f"- {hoje}: Primeiro deploy (esqueleto gerado por novo_notebook.py)"
    ))

    # 1. Bibliotecas / Spark Configs
    celulas.append(celula_markdown(
        "#### Spark Configs e bibliotecas\n\n"
        "Configuracoes de leitura Parquet legada e Adaptive Query Execution, seguidas dos "
        "imports padrao PySpark/Delta usados no restante do notebook."
    ))
    celulas.append(celula_codigo(SPARK_CONFIGS + "\n\n" + IMPORTS_PADRAO))

    # 2. Parametros e ambiente
    celulas.extend(celulas_parametros(cloud, camada, dominio, entidade, entidade_slug))

    # 3. Preparacao da tabela destino
    nota_bronze = ""
    if camada == "bronze" and cloud == "fabric":
        nota_bronze = (
            "\n\n# NOTA: no padrao Fabric deste projeto, Bronze costuma ser um mirrored "
            "database (sem tabela fisica). Remova esta celula se for o caso aqui."
        )
    celulas.append(celula_markdown(
        "#### Preparacao da tabela destino\n\n"
        "Garante a existencia do schema de destino antes da primeira escrita."
    ))
    celulas.append(celula_codigo(
        '# TODO: ajustar para catalog.schema (Databricks/Unity Catalog) ou schema do\n'
        '# lakehouse (Fabric), conforme o projeto.\n'
        'spark.sql(f"CREATE SCHEMA IF NOT EXISTS {TARGET_SCHEMA}")\n'
        'print(f"[OK] Schema garantido: {TARGET_SCHEMA}")' + nota_bronze
    ))

    # 4. Leitura das origens (inicio da cadeia de temp views Spark-SQL-first)
    celulas.append(celula_markdown(
        "#### Leitura das origens\n\n"
        "-- TODO: a cadeia de temp views (Spark SQL first, sem CTE) comeca aqui. Cada etapa "
        "e UMA celula Markdown (titulo = nome da view, corpo = o que ela contem) seguida de "
        "UMA celula de codigo com uma unica createOrReplaceTempView, dentro de uma funcao "
        f"gera_tabela_{entidade_slug}()/gera_view_<nome>() chamada na mesma celula. "
        "Ver exemplo do padrao na celula seguinte."
    ))
    celulas.append(celula_codigo(
        f'# 1 celula = 1 temp view. Leitura de origem usa gera_tabela_<TABELA>(); as demais\n'
        f'# etapas usam gera_view_<nome>(). SELECT explicito de colunas, nunca SELECT *.\n'
        f'def gera_tabela_{entidade_slug}():\n'
        f'    df = spark.sql(f"""\n'
        f'        -- TODO: SELECT explicito de colunas a partir da origem real\n'
        f'        SELECT\n'
        f'            <CAMPO_ID> AS id_negocio,\n'
        f'            <CAMPO_DESCRICAO> AS descricao\n'
        f'        FROM {{SOURCE_SCHEMA}}.<TABELA_ORIGEM>\n'
        f'    """)\n'
        f'    return df.createOrReplaceTempView("{entidade_slug}_origem")\n\n'
        f'gera_tabela_{entidade_slug}()'
    ))

    # 4b. Exemplo ilustrativo do padrao (celula Markdown apenas)
    celulas.append(celula_markdown(
        "##### Exemplo do padrao: 1 temp view por celula\n\n"
        "Cada etapa da transformacao e uma celula Markdown (titulo = nome da view, o que ela "
        "contem) IMEDIATAMENTE seguida de uma celula de codigo com uma unica "
        "createOrReplaceTempView, dentro de uma funcao gera_view_<nome>() chamada na mesma "
        "celula. Sem CTE (`WITH ... AS`) dentro de um spark.sql: cada etapa e a sua propria "
        "temp view, nomeada e documentada -- para o PO revisar a regra de negocio lendo o "
        "notebook renderizado, sem precisar ler PySpark.\n\n"
        "Exemplo (substituir pelas etapas reais da entidade):\n\n"
        "- Celula Markdown: `#### padronizado - normaliza nomes de campo e tipos`\n"
        "- Celula de codigo:\n"
        "  ```python\n"
        "  def gera_view_padronizado():\n"
        "      df = spark.sql(\"SELECT id_negocio, descricao FROM origem\")\n"
        "      return df.createOrReplaceTempView(\"padronizado\")\n\n"
        "  gera_view_padronizado()\n"
        "  ```"
    ))

    # 5. Padronizacao de campos
    celulas.append(celula_markdown(
        "#### Padronizacao de campos\n\n"
        "Renomeia campos, mantem IDs como texto (STRING) e tipa apenas datas/valores/quantidades "
        "com as funcoes tratar_* (nunca UDF Python -- deixa o Catalyst otimizar)."
    ))
    celulas.append(celula_codigo(
        '# TODO: colunas e tratamentos reais (tratar_timestamp/tratar_inteiro/tratar_booleano).\n'
        'def gera_view_padronizado():\n'
        f'    df = spark.sql("""\n'
        f'        SELECT\n'
        f'            id_negocio,\n'
        f'            descricao\n'
        f'        FROM {entidade_slug}_origem\n'
        f'    """)\n'
        f'    return df.createOrReplaceTempView("padronizado")\n\n'
        f'gera_view_padronizado()'
    ))

    # 6. Regra de duplicidade
    celulas.append(celula_markdown(
        "#### Regra de duplicidade\n\n"
        "Documentar a chave e o criterio de desempate explicito (ROW_NUMBER + ORDER BY "
        "documentado, nunca uma linha arbitraria). Remover esta etapa apenas quando a "
        "entidade nao exigir deduplicacao."
    ))
    celulas.append(celula_codigo(
        '# TODO: PARTITION BY = chave real; ORDER BY = criterio de desempate documentado.\n'
        'def gera_view_deduplicado():\n'
        '    df = spark.sql("""\n'
        '        WITH base AS (\n'
        '            SELECT\n'
        '                id_negocio,\n'
        '                descricao,\n'
        '                ROW_NUMBER() OVER (\n'
        '                    PARTITION BY id_negocio\n'
        '                    ORDER BY id_negocio DESC NULLS LAST\n'
        '                ) AS ordem_duplicidade\n'
        '            FROM padronizado\n'
        '        )\n'
        '        SELECT id_negocio, descricao\n'
        '        FROM base\n'
        '        WHERE ordem_duplicidade = 1\n'
        '    """)\n'
        '    return df.createOrReplaceTempView("deduplicado")\n\n'
        'gera_view_deduplicado()'
    ))

    # 7. Consolidado (excecao: retorna DataFrame em vez de registrar view)
    celulas.append(celula_markdown(
        "#### Consolidado\n\n"
        "Ultima etapa da cadeia: monta a lista final de colunas. Excecao ao padrao -- "
        "`gera_tabela_final()` RETORNA o DataFrame em vez de registrar uma temp view "
        "(as validacoes de qualidade e o write precisam do DataFrame, nao so da view)."
    ))
    celulas.append(celula_codigo(
        '# TODO: lista final de colunas (com rastreabilidade de origem, se aplicavel).\n'
        'def gera_tabela_final():\n'
        '    return spark.sql("""\n'
        '        SELECT\n'
        '            id_negocio,\n'
        '            descricao\n'
        '        FROM deduplicado\n'
        '    """)\n\n'
        'df_final = gera_tabela_final()\n'
        'df_final.createOrReplaceTempView("consolidado")'
    ))

    # 8. Validacoes de qualidade (Tier 1 hard gate + Tier 2 aviso)
    bloco_fanout = ""
    if camada == "gold":
        bloco_fanout = (
            '\n\n# Gold-only: multiplicacao de linhas apos join contra uma dimensao (fan-out).\n'
            '# TODO: trocar pelos nomes reais da fato/dimensao envolvidas no join.\n'
            '# linhas_antes_join = spark.table("<fato_base>").count()\n'
            '# linhas_depois_join = df_apos_join.count()\n'
            '# if linhas_depois_join > linhas_antes_join:\n'
            '#     erros.append(\n'
            '#         f"join multiplicou linhas: {linhas_antes_join} -> {linhas_depois_join}"\n'
            '#     )'
        )
    celulas.append(celula_markdown(
        "#### Validacoes de qualidade\n\n"
        "Gate obrigatorio ANTES do write. Tier 1 (`raise ValueError`) bloqueia a escrita "
        "quando a tabela sairia errada/inutilizavel; Tier 2 (`print(\"[AVISO] ...\")`) so "
        "avisa, para investigacao humana, sem travar a carga. Contadores reunidos em uma "
        "unica query (uma acao Spark, nao um `.filter().count()` por checagem)."
    ))
    celulas.append(celula_codigo(
        '# TODO: trocar <CAMPO_ID> pela(s) coluna(s) reais da PRIMARY_KEY / campo obrigatorio.\n'
        'df_metricas = spark.sql("""\n'
        '    SELECT\n'
        '        (SELECT COUNT(1) FROM consolidado) AS qt_final,\n'
        '        (SELECT COUNT(1) FROM consolidado WHERE <CAMPO_ID> IS NULL) AS qt_chave_nula,\n'
        '        (\n'
        '            SELECT COUNT(1) FROM (\n'
        '                SELECT <CAMPO_ID> FROM consolidado GROUP BY <CAMPO_ID> HAVING COUNT(1) > 1\n'
        '            ) duplicados\n'
        '        ) AS qt_pk_duplicada\n'
        '    FROM (SELECT 1)\n'
        '""")\n'
        'metricas = df_metricas.first().asDict()\n'
        'for nome, valor in metricas.items():\n'
        '    print(f"{nome}: {valor}")\n\n'
        '# --- Tier 1: gate obrigatorio, bloqueia o write ---\n'
        'erros = []\n'
        'if metricas["qt_final"] == 0:\n'
        '    erros.append("DataFrame final vazio")\n'
        'if metricas["qt_chave_nula"] > 0:\n'
        '    erros.append(f"{metricas[\'qt_chave_nula\']} registro(s) com campo obrigatorio nulo")\n'
        'if metricas["qt_pk_duplicada"] > 0:\n'
        '    erros.append(f"{metricas[\'qt_pk_duplicada\']} chave(s) duplicada(s) na PK")'
        + bloco_fanout +
        '\n\nif erros:\n'
        '    raise ValueError("Escrita bloqueada pelas validacoes: " + "; ".join(erros))\n'
        'print("[OK] Validacoes estruturais concluidas. Escrita liberada.")\n\n'
        '# --- Tier 2: aviso de observabilidade, NAO bloqueia (limiar configuravel) ---\n'
        '# TODO: ajustar o limiar e o contador real por entidade (ver quality-gates.md).\n'
        'LIMIAR_AVISO_PCT = 1.0\n'
        'qt_residual = 0  # TODO: ex. valor de-para caindo em "Outro"/"Indefinido"\n'
        'pct_residual = 100 * qt_residual / metricas["qt_final"] if metricas["qt_final"] else 0\n'
        'if pct_residual >= LIMIAR_AVISO_PCT:\n'
        '    print(f"[AVISO] residual em {pct_residual:.2f}% (esperado < {LIMIAR_AVISO_PCT}%). Investigar.")\n'
        'else:\n'
        '    print(f"[OK] residual em {pct_residual:.2f}%.")'
    ))

    # 9. Metadados e escrita
    celulas.append(celula_markdown(
        "#### Metadados e escrita\n\n"
        "Adiciona `data_processamento` e grava a tabela Delta. FULL reconstroi a tabela "
        "inteira (volume pequeno/medio, ou regra que exige reconstrucao completa); MERGE "
        "faz upsert por PK confiavel (a 1a carga, sem tabela existente, cai em FULL sozinha). "
        "`LOAD_METHOD` normalmente vem do CSV metadata-driven, nao e hardcoded aqui."
    ))
    celulas.append(celula_codigo(
        'df_final = df_final.withColumn("data_processamento", F.current_timestamp())\n\n'
        'if LOAD_METHOD == "MERGE":\n'
        '    alvo = f"{TARGET_SCHEMA}.{TARGET_TABLE}"\n'
        '    if not spark.catalog.tableExists(alvo):\n'
        '        df_final.write.format("delta").mode("overwrite") \\\n'
        '            .option("overwriteSchema", "true").saveAsTable(alvo)\n'
        '    else:\n'
        '        condicao = " AND ".join([f"target.{c} = source.{c}" for c in PRIMARY_KEY])\n'
        '        (DeltaTable.forName(spark, alvo).alias("target")\n'
        '            .merge(df_final.alias("source"), condicao)\n'
        '            .whenMatchedUpdateAll()\n'
        '            .whenNotMatchedInsertAll()\n'
        '            .execute())\n'
        'else:\n'
        '    df_final.write.format("delta").mode("overwrite") \\\n'
        '        .option("overwriteSchema", "true").saveAsTable(f"{TARGET_SCHEMA}.{TARGET_TABLE}")\n\n'
        'print("--------")\n'
        'print("Carga finalizada")\n'
        'print(f"Ambiente: {ENV}")\n'
        'print(f"Destino: {TARGET_SCHEMA}.{TARGET_TABLE}")\n'
        'print(f"Metodo de carga: {LOAD_METHOD}")\n'
        'print(f"Linhas final: {metricas[\'qt_final\']}")\n'
        'print("--------")'
    ))

    # 10. Checklist final
    fanout_item = "- [ ] Fan-out de join contra dimensao coberto (Gold)\n" if camada == "gold" else ""
    celulas.append(celula_markdown(
        "## Checklist antes de publicar\n\n"
        "- [ ] SELECT explicito de colunas na leitura da origem (sem `SELECT *`)\n"
        "- [ ] Cadeia de temp views documentada (1 celula Markdown + 1 `createOrReplaceTempView` "
        "por celula, sem CTE)\n"
        "- [ ] Regra de duplicidade com criterio de desempate explicito e documentado\n"
        "- [ ] Validacoes Tier 1 (`raise`) cobrindo: vazio, PK duplicada, campo obrigatorio nulo\n"
        + fanout_item +
        "- [ ] Limiares Tier 2 (`[AVISO]`) ajustados para a entidade\n"
        "- [ ] `LOAD_METHOD` confirmado contra `metadata_driven_orchestration.csv` (nao hardcoded)\n"
        "- [ ] Linha da entidade anexada ao `metadata_driven_orchestration.csv` (Fabric)\n"
        "- [ ] Notebook sem acento (import-safe); rodar `limpar_notebook_import.py` antes do import"
    ))

    return celulas


def montar_notebook(camada: str, entidade: str, dominio: str, cloud: str, sistemas_origem: str) -> dict:
    return {
        "cells": montar_celulas(camada, entidade, dominio, cloud, sistemas_origem),
        "metadata": metadata_notebook(cloud),
        "nbformat": 4,
        "nbformat_minor": 5,
    }


# ------------------------------------------------------------------ CSV metadata-driven (Fabric)

def montar_linha_csv(camada: str, entidade: str, dominio: str, entidade_slug: str, notebook_name: str) -> str:
    valores = {
        "is_active": "TRUE",
        "execution_order": "TODO",
        "layer": camada.upper(),
        "domain": dominio,
        "subdomain": "TODO",
        "ddd_type": "Entity",
        "business_entity": entidade,
        "notebook_name": notebook_name,
        "owner": "TODO",
        "source_system": "TODO",
        "business_definition": "TODO",
        "primary_key": "TODO",
        "target_schema": "TODO",
        "target_table": entidade_slug,
        "load_method": "TODO",
        "watermark_enabled": "FALSE",
        "watermark_column": "TODO",
        "watermark_start_value": "1900-01-01 00:00:00",
        "watermark_lookback_days": "1",
        "env": "DEV",
        "timeout_minutes": "TODO",
        "retry_count": "TODO",
        "notebook_id": "",
    }
    return ";".join(valores[coluna] for coluna in COLUNAS_CSV)


def registrar_csv(caminho_csv: Path, linha: str) -> None:
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    if not caminho_csv.exists():
        caminho_csv.write_text(";".join(COLUNAS_CSV) + "\n", encoding="utf-8", newline="\n")
        print(f"[novo_notebook] CSV nao existia, cabecalho criado: {caminho_csv}")
    with open(caminho_csv, "a", encoding="utf-8", newline="\n") as f:
        f.write(linha + "\n")
    print(f"[novo_notebook] Linha registrada em {caminho_csv}")


# ------------------------------------------------------------------ CLI

def main():
    parser = argparse.ArgumentParser(description="Gera um notebook .ipynb esqueleto (Bronze/Silver/Gold).")
    parser.add_argument("--camada", required=True, choices=["bronze", "silver", "gold"])
    parser.add_argument("--entidade", required=True, help="Nome de negocio da entidade (ex.: doador)")
    parser.add_argument("--dominio", required=True, help="Dominio de negocio (ex.: doadores)")
    parser.add_argument("--cloud", required=True, choices=["fabric", "databricks"])
    parser.add_argument("--saida", required=True, help="Caminho do .ipynb a gerar")
    parser.add_argument(
        "--sistemas-origem", default="TODO",
        help="Sistema(s) de origem para o cabecalho (default: TODO)",
    )
    parser.add_argument(
        "--registrar-csv",
        help="Caminho do metadata_driven_orchestration.csv para anexar uma linha stub (so --cloud fabric)",
    )
    parser.add_argument("--forcar", action="store_true", help="Sobrescreve --saida se ja existir")
    args = parser.parse_args()

    destino = Path(args.saida)
    if destino.exists() and not args.forcar:
        raise SystemExit(f"[novo_notebook] ja existe: {destino} (use --forcar para sobrescrever)")

    nb = montar_notebook(args.camada, args.entidade, args.dominio, args.cloud, args.sistemas_origem)

    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"[novo_notebook] OK: {destino} ({len(nb['cells'])} celulas, camada={args.camada}, cloud={args.cloud})")

    if args.registrar_csv:
        if args.cloud != "fabric":
            print("[novo_notebook] --registrar-csv ignorado: orquestracao por CSV e um conceito Fabric "
                  "(Databricks usa Jobs/DLT ou databricks.yml -- ver scaffold_cliente.py).")
        else:
            entidade_slug = slug_identificador(args.entidade)
            linha = montar_linha_csv(args.camada, args.entidade, args.dominio, entidade_slug, destino.stem)
            registrar_csv(Path(args.registrar_csv), linha)


if __name__ == "__main__":
    main()
