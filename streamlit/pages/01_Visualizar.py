import streamlit as st
import psycopg2
import pandas as pd

# ------------------------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------------------------

def get_tables(conn):
    """
    Retorna lista de nomes de tabelas do esquema público.
    """
    query = """
        SELECT tablename 
        FROM pg_catalog.pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    # rows retorna uma lista de tuplas [(nome_tabela,), (nome_tabela2,)...]
    return [row[0] for row in rows]

def get_table_columns(conn, table_name):
    """
    Retorna as colunas de uma tabela, com nome, tipo, etc. via information_schema.
    """
    query = f"""
        SELECT
            column_name,
            data_type,
            is_nullable,
            character_maximum_length
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        columns_info = cur.fetchall()
    return columns_info

def get_primary_keys(conn, table_name):
    """
    Retorna as colunas que compõem a primary key de uma tabela.
    """
    query = f"""
        SELECT
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name 
           AND tc.table_schema = kcu.table_schema
        WHERE tc.table_name = '{table_name}'
          AND tc.constraint_type = 'PRIMARY KEY';
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return [row[0] for row in rows]

def get_foreign_keys(conn, table_name):
    """
    Retorna os relacionamentos de chave estrangeira de uma tabela.
    Formato: [(coluna_origem, tabela_destino, coluna_destino), ...]
    """
    query = f"""
        SELECT
            kcu.column_name AS fk_column,
            ccu.table_name  AS referenced_table,
            ccu.column_name AS referenced_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
           AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
           AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name = '{table_name}';
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    # rows => [("fk_column", "tabela_referenciada", "coluna_referenciada"), ...]
    return rows

def load_table_data(conn, table_name, limit=100):
    """
    Carrega os dados da tabela (limitando a uma quantidade específica).
    """
    query = f'SELECT * FROM "{table_name}" LIMIT {limit};'
    return pd.read_sql(query, conn)

def build_relationship_graph(conn, tables):
    """
    Retorna string no formato Graphviz para desenhar os relacionamentos
    entre as tabelas listadas em `tables`.
    """
    edges = []
    for table in tables:
        fks = get_foreign_keys(conn, table)
        for fk_col, ref_table, ref_col in fks:
            # Exemplo de aresta: table -> ref_table
            # Vamos indicar também que a aresta é "table.fk_col -> ref_table.ref_col"
            edge_str = f'"{table}" -> "{ref_table}" [label="{fk_col} → {ref_col}"]'
            edges.append(edge_str)

    # Monta o digrafo
    graph_definition = 'digraph {\n'
    for edge in edges:
        graph_definition += f'    {edge}\n'
    graph_definition += '}\n'
    return graph_definition


# ------------------------------------------------------------------------------
# Aplicação principal em Streamlit
# ------------------------------------------------------------------------------
def visualizar():
    st.title("Visão Geral do Banco de Dados")

    # ---------------------------------------------------------------
    # Conexão com o banco
    # ---------------------------------------------------------------
    # Ajuste com as credenciais do seu PostgreSQL (host, dbname, user, password)
    conn = psycopg2.connect(
        host="localhost",
        dbname="ufop",
        user="root",
        password="dfssiehfieufgh3478357",
        port=5432  # ou outra porta que seu Postgres use
    )

    st.subheader("Tabelas do banco (schema público)")

    # ---------------------------------------------------------------
    # Listar tabelas
    # ---------------------------------------------------------------
    tables = get_tables(conn)
    if not tables:
        st.warning("Não foram encontradas tabelas no schema público.")
        return

    st.write(f"Total de tabelas encontradas: {len(tables)}")
    table_selected = st.selectbox("Selecione uma tabela", tables)

    # ---------------------------------------------------------------
    # Mostrar metadados da tabela selecionada
    # ---------------------------------------------------------------
    st.write(f"**Estrutura da tabela** `{table_selected}`:")
    columns_info = get_table_columns(conn, table_selected)
    if columns_info:
        df_columns = pd.DataFrame(
            columns_info,
            columns=["Coluna", "Tipo", "Pode ser Nulo?", "Tamanho Máximo"]
        )
        st.dataframe(df_columns)
    else:
        st.warning("Não foram encontradas colunas para esta tabela.")

    # Chave primária
    pks = get_primary_keys(conn, table_selected)
    if pks:
        st.write(f"**Chave Primária**: {', '.join(pks)}")
    else:
        st.write("A tabela não possui Primary Key definida.")

    # Chaves estrangeiras
    fks = get_foreign_keys(conn, table_selected)
    if fks:
        st.write("**Chaves Estrangeiras**:")
        for fk_col, ref_table, ref_col in fks:
            st.write(f"- `{fk_col}` → {ref_table}({ref_col})")
    else:
        st.write("A tabela não possui Foreign Keys.")

    # ---------------------------------------------------------------
    # Visualizar dados da tabela
    # ---------------------------------------------------------------
    st.subheader(f"Dados da Tabela {table_selected}")
    limit = st.number_input("Quantidade de linhas para exibir", min_value=1, max_value=1000, value=100)
    df_data = load_table_data(conn, table_selected, limit=limit)
    st.dataframe(df_data)

    # ---------------------------------------------------------------
    # (Opcional) Visualizar relações entre tabelas via Graphviz
    # ---------------------------------------------------------------
    st.subheader("Diagrama de Relacionamentos (FK) das Tabelas")
    if st.button("Gerar diagrama"):
        graphviz_str = build_relationship_graph(conn, tables)
        st.graphviz_chart(graphviz_str)

    # Fechar conexão
    conn.close()

def main():
    visualizar()

# Chamamos main() para que quando esta página for selecionada,
# ela execute seu conteúdo
main()