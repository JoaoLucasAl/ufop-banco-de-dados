import streamlit as st
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor


def get_tables(conn):
    """
    Retorna lista de tabelas do schema público.
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
    return [r[0] for r in rows]


def get_table_columns(conn, table_name):
    """
    Retorna metadados das colunas da tabela:
      - column_name
      - data_type (ex: character varying, integer, boolean, user-defined, etc.)
      - is_nullable
      - udt_name (se for enum ou user-defined, ex: "Sexo")
    """
    query = f"""
    SELECT
        column_name,
        data_type,
        is_nullable,
        udt_name
    FROM information_schema.columns
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        cols = cur.fetchall()
    # Retorna [(coluna, data_type, is_nullable, udt_name), ...]
    return cols


def get_primary_keys(conn, table_name):
    """
    Retorna nome das colunas que compõem a primary key de 'table_name'.
    """
    query = f"""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
               ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
        WHERE tc.table_name = '{table_name}'
          AND tc.constraint_type = 'PRIMARY KEY';
    """
    with conn.cursor() as cur:
        cur.execute(query)
        pk_cols = cur.fetchall()
    return [r[0] for r in pk_cols]


def load_table_data(conn, table_name, pk_cols):
    """
    Carrega dados da tabela (select *), em formato de dicionário (RealDictCursor)
    para facilitar a manipulação. Retorna uma lista de dicts.
    """
    from psycopg2.extras import RealDictCursor
    
    # Monta o ORDER BY com aspas nas colunas:
    # ex.: ORDER BY "nTombamento", "nome" ...
    order_by_cols = ", ".join(f'"{col}"' for col in pk_cols)

    query = f"""
        SELECT * 
        FROM "{table_name}" 
        ORDER BY {order_by_cols} 
        LIMIT 200;
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return rows



def build_insert_statement(table_name, columns):
    """
    Monta o comando INSERT de forma genérica, do tipo:
      INSERT INTO "Table" (col1, col2, ...) VALUES (%s, %s, ...)
    Retorna a string do SQL e a lista de colunas que serão preenchidas.
    """
    col_names = [f'"{c}"' for c in columns]  # Aspas duplas para lidar com nomes que tenham maiúscula, acentos, etc.
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f'INSERT INTO "{table_name}" ({", ".join(col_names)}) VALUES ({placeholders})'
    return sql


def build_update_statement(table_name, columns, pk_cols):
    """
    Monta um comando UPDATE de forma genérica:
      UPDATE "Table" SET colA=%s, colB=%s ...
      WHERE pk1=%s AND pk2=%s ...
    Retorna a string SQL e a lista de colunas (na ordem de binding).
    """
    # Colunas que não são PK
    non_pk_cols = [c for c in columns if c not in pk_cols]
    set_clause = ", ".join([f'"{c}"=%s' for c in non_pk_cols])
    where_clause = " AND ".join([f'"{pk}"=%s' for pk in pk_cols])
    sql = f'UPDATE "{table_name}" SET {set_clause} WHERE {where_clause}'
    return sql, non_pk_cols


def parse_input_value(value_str, data_type):
    """
    Converte a string digitada pelo usuário em um valor Python coerente com data_type.
    Exemplo:
      - se data_type = 'boolean', converter 'True'/'False' ou '1'/'0' etc.
      - se data_type = 'integer', converter para int
      - se data_type = 'timestamp', converter para datetime, etc.
    Aqui faremos algo bem simplificado e genérico.
    """
    if value_str == "" or value_str is None:
        return None

    data_type_lower = data_type.lower()
    # Exemplos básicos - ajuste conforme necessidade
    if "integer" in data_type_lower or "smallint" in data_type_lower:
        return int(value_str)
    elif "numeric" in data_type_lower or "decimal" in data_type_lower:
        return float(value_str)
    elif "boolean" in data_type_lower:
        # Aceitar 'true', 'false', '1', '0'
        val = value_str.strip().lower()
        return val in ["true", "1", "t", "yes"]
    elif "timestamp" in data_type_lower or "date" in data_type_lower:
        # Tentar converter usando pd.to_datetime
        return pd.to_datetime(value_str)
    # Se for user-defined enum (ex: Sexo), assumiremos string literal
    return value_str


# ------------------------------------------------------------------------------
# Aplicação principal
# ------------------------------------------------------------------------------
def editar_inserir():
    st.title("Inserir/Editar Dados")

    # Conexão com o DB - ajuste suas credenciais
    conn = psycopg2.connect(
        host="postgres",
        dbname="ufop",
        user="root",
        password="dfssiehfieufgh3478357",
        port=5432  # ou outra porta que seu Postgres use
    )
    # 1. Listar tabelas
    tables = get_tables(conn)
    if not tables:
        st.error("Não há tabelas no schema público.")
        conn.close()
        return

    # 2. Escolher tabela
    selected_table = st.selectbox("Selecione a Tabela", tables)

    # 3. Carregar metadados: colunas e chave primária
    columns_info = get_table_columns(conn, selected_table)
    pk_cols = get_primary_keys(conn, selected_table)

    if len(columns_info) == 0:
        st.warning("Tabela sem colunas ou não foi possível obter metadados.")
        conn.close()
        return

    # 4. Escolher operação: Inserir ou Editar
    operation = st.radio("Operação", ["Inserir", "Editar"])

    # 5. Exibir dados existentes (opcional, para referência)
    if st.checkbox("Mostrar dados atuais da tabela (até 200 linhas)"):
        rows = load_table_data(conn, selected_table, pk_cols)
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)
        else:
            st.info("Nenhum registro encontrado na tabela.")

    if operation == "Inserir":
        st.subheader(f"Inserir novo registro em '{selected_table}'")

        # Montar formulário dinâmico para cada coluna
        # (Podemos ignorar colunas do tipo SERIAL ou geradas automaticamente, se desejar.)
        input_data = {}
        for col_name, data_type, is_nullable, udt_name in columns_info:
            # A rigor, você pode pular colunas se elas forem PK serial
            # Aqui, apenas pediremos ao usuário para inserir valor (ou deixar em branco).
            user_val = st.text_input(f"{col_name} ({data_type})", value="")
            input_data[col_name] = user_val

        if st.button("Inserir Registro"):
            # Montar lista de colunas e valores (apenas as que o usuário preencheu ou que vamos inserir).
            col_names = []
            col_values = []
            for col_name, data_type, is_nullable, udt_name in columns_info:
                val_str = input_data[col_name]
                if val_str.strip() == "":
                    # Se o campo está vazio, ou vira NULL ou confiamos em default. Depende do schema.
                    # Se não for nullable e não tiver default, isso vai dar erro.
                    # Faremos val=None, que insere NULL.
                    val = None
                else:
                    # Tentar converter
                    val = parse_input_value(val_str, data_type)
                col_names.append(col_name)
                col_values.append(val)

            sql_insert = build_insert_statement(selected_table, col_names)
            try:
                with conn.cursor() as cur:
                    cur.execute(sql_insert, tuple(col_values))
                conn.commit()
                st.success("Registro inserido com sucesso!")
            except Exception as e:
                conn.rollback()
                st.error(f"Erro ao inserir: {e}")

    else:  # operation == "Editar"
        st.subheader(f"Editar (Update) registro existente em '{selected_table}'")
        if not pk_cols:
            st.error("Esta tabela não tem chave primária definida. Atualização genérica fica arriscada.")
            conn.close()
            return

        # Precisamos que o usuário escolha qual registro editar, com base na PK
        # Para isso, carregamos todos os registros e deixamos a pessoa escolher via selectbox
        rows = load_table_data(conn, selected_table, pk_cols)
        if not rows:
            st.info("Nenhum registro encontrado para editar.")
            conn.close()
            return

        # Cria uma forma textual de identificar cada row pela PK
        def pk_string(row, pk_cols):
            vals = [str(row[pk]) for pk in pk_cols]
            return " / ".join(vals)

        # Mapeia pk_string -> row
        row_map = {pk_string(r, pk_cols): r for r in rows}

        selected_row_key = st.selectbox("Selecione o registro (chave):", list(row_map.keys()))
        row_to_edit = row_map[selected_row_key]

        # Exibir formulário pré-preenchido
        # Precisamos de duas coisas:
        # 1) PK (fixa)
        # 2) Colunas não-PK (podem ser alteradas)
        input_data_update = {}
        for col_name, data_type, is_nullable, udt_name in columns_info:
            current_val = row_to_edit[col_name]
            if current_val is None:
                current_val_str = ""
            else:
                current_val_str = str(current_val)

            new_val_str = st.text_input(f"{col_name} ({data_type})", value=current_val_str)
            input_data_update[col_name] = new_val_str

        if st.button("Atualizar Registro"):
            # Montar lista de colunas (sem as PK, pois as PK não serão alteradas) e valores
            all_col_names = [c[0] for c in columns_info]
            sql_update, non_pk_cols = build_update_statement(selected_table, all_col_names, pk_cols)

            # Construir a lista de valores na ordem: [val_col_nonpk..., val_pk...]
            non_pk_values = []
            for c in non_pk_cols:
                data_type = next((x[1] for x in columns_info if x[0] == c), "text")
                val_converted = parse_input_value(input_data_update[c], data_type)
                non_pk_values.append(val_converted)

            # Pegar os valores das PK a partir do row original (caso a gente não queira permitir mudança de PK)
            pk_values = []
            for pk in pk_cols:
                data_type = next((x[1] for x in columns_info if x[0] == pk), "text")
                # Se quiséssemos deixar o user editar PK, teríamos que usar input_data_update[pk].
                # Mas normalmente não se muda PK. Então usamos row_to_edit.
                original_val = row_to_edit[pk]
                pk_val_converted = parse_input_value(str(original_val), data_type)
                pk_values.append(pk_val_converted)

            try:
                with conn.cursor() as cur:
                    cur.execute(sql_update, tuple(non_pk_values + pk_values))
                conn.commit()
                st.success("Registro atualizado com sucesso!")
            except Exception as e:
                conn.rollback()
                st.error(f"Erro ao atualizar: {e}")

    conn.close()


def main():
    editar_inserir()

if __name__ == "__main__":
    main()