# consultas.py

import streamlit as st
import psycopg2
import pandas as pd


def get_connection():
    conn = psycopg2.connect(
        host="postgres",
        dbname="ufop",
        user="root",
        password="dfssiehfieufgh3478357",
        port=5432
    )
    return conn

def run_query(query, params=None):
    """
    Executa uma query SQL e retorna (rows, columns).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return rows, colunas


# ------------------------------------------------------------------------------
# 1) Consulta: DocenteResponsávelPorLaboratório
#    - Ex: buscar por nome do docente e ver laboratórios sob responsabilidade.
# ------------------------------------------------------------------------------
def consulta_docente_responsavel_laboratorio():
    st.subheader("Docente Responsável por Laboratório")

    nome_docente = st.text_input("Digite parte do nome do Docente para pesquisa:")
    if st.button("Buscar Responsáveis"):
        parametro = f"%{nome_docente}%"

        query = """
        SELECT 
            doc."código"             AS codigo_docente,
            doc."nome"               AS nome_docente,
            lab."id"                 AS laboratorio_id,
            lab."nome"               AS laboratorio_nome,
            lab."sala"               AS sala,
            lab."prédio"             AS predio,
            drl."data"               AS data_responsabilidade
        FROM "Docente" doc
        JOIN "DocenteResponsávelPorLaboratório" drl
             ON doc."código" = drl."docenteCódigo"
        JOIN "Laboratório" lab
             ON lab."id" = drl."laboratórioId"
        WHERE doc."nome" ILIKE %s
        ORDER BY doc."nome";
        """

        rows, colunas = run_query(query, (parametro,))
        df = pd.DataFrame(rows, columns=colunas)
        st.dataframe(df)


# ------------------------------------------------------------------------------
# 2) Consulta: Equipamento -> Laboratório
#    - Ex: buscar equipamentos de um determinado laboratório ou vice-versa.
# ------------------------------------------------------------------------------
def consulta_equipamentos_por_laboratorio():
    st.subheader("Equipamentos por Laboratório")

    # Opção 1: busca pelo nome do laboratório
    nome_lab = st.text_input("Digite parte do nome do laboratório:")
    if st.button("Buscar Equipamentos"):
        parametro = f"%{nome_lab}%"

        query = """
        SELECT
            lab."id"                 AS laboratorio_id,
            lab."nome"               AS laboratorio_nome,
            eqp."nTombamento"        AS tombamento,
            eqp."nome"               AS nome_equipamento,
            eqp."fabricante"         AS fabricante,
            eqp."nModelo"            AS numero_modelo
        FROM "Laboratório" lab
        JOIN "Equipamento" eqp
             ON lab."id" = eqp."laboratórioId"
        WHERE lab."nome" ILIKE %s
        ORDER BY lab."nome", eqp."nTombamento";
        """

        rows, colunas = run_query(query, (parametro,))
        df = pd.DataFrame(rows, columns=colunas)
        st.dataframe(df)


# ------------------------------------------------------------------------------
# 3) Consulta: Bolsa -> MembroDoProjeto -> Projeto
#    - Ver as bolsas de determinado projeto, ou ver todos os projetos, etc.
# ------------------------------------------------------------------------------
def consulta_bolsas_e_membros_do_projeto():
    st.subheader("Bolsas e Membros de Projeto")

    # Exemplo: buscar por nome do projeto
    nome_projeto = st.text_input("Digite parte do nome do projeto:")
    if st.button("Buscar Bolsas/Membros"):
        parametro = f"%{nome_projeto}%"

        query = """
        SELECT 
            p."código"            AS projeto_codigo,
            p."nome"              AS projeto_nome,
            mbp."id"              AS membro_id,
            mbp."função"          AS funcao,
            mbp."cargaHoraria"    AS carga_horaria,
            b."valor"             AS valor_bolsa,
            b."dataInicio"        AS bolsa_inicio,
            b."dataFim"           AS bolsa_fim
        FROM "Projeto" p
        JOIN "MembroDoProjeto" mbp
             ON p."código" = mbp."projetoCódigo"
        LEFT JOIN "Bolsa" b
             ON b."bolsistaId" = mbp."id"
             AND b."projetoCódigo" = p."código"
        WHERE p."nome" ILIKE %s
        ORDER BY p."nome", mbp."id";
        """
        
        rows, colunas = run_query(query, (parametro,))
        df = pd.DataFrame(rows, columns=colunas)
        st.dataframe(df)


# ------------------------------------------------------------------------------
# 4) Consulta: DiscenteFazAvaliação
#    - Mostrar avaliações que um discente fez, com disciplina, nota etc.
# ------------------------------------------------------------------------------
def consulta_avaliacoes_por_discente():
    st.subheader("Avaliações realizadas por Discente")

    nome_discente = st.text_input("Digite parte do nome do Discente:")
    if st.button("Buscar Avaliações"):
        parametro = f"%{nome_discente}%"

        query = """
        SELECT
            di."matrícula"          AS matricula,
            di."nome"               AS nome_discente,
            av."disciplinaNome"     AS disciplina,
            av."data"               AS data_avaliacao,
            av."valor"              AS valor_prova,
            dfa."nota"              AS nota_obtida
        FROM "Discente" di
        JOIN "DiscenteFazAvaliação" dfa
             ON di."matrícula" = dfa."matrícula"
        JOIN "Avaliação" av
             ON av."disciplinaNome" = dfa."disciplinaNome"
            AND av."número"         = dfa."número"
            AND av."anoSemestre"    = dfa."anoSemestre"
            AND av."data"           = dfa."data"
        WHERE di."nome" ILIKE %s
        ORDER BY di."nome", av."data";
        """

        rows, colunas = run_query(query, (parametro,))
        df = pd.DataFrame(rows, columns=colunas)
        st.dataframe(df)


# ------------------------------------------------------------------------------
# 5) Exemplo adicional: Discente -> MembroDoProjeto
#    - Mostra se o discente (caso seja MembroDoProjeto) participa de algum Projeto
# ------------------------------------------------------------------------------
def consulta_discentes_em_projetos():
    st.subheader("Discentes que participam de Projetos (via MembroDoProjeto)")

    nome_discente = st.text_input("Digite parte do nome do Discente:")
    if st.button("Buscar Projetos do Discente"):
        parametro = f"%{nome_discente}%"

        query = """
        SELECT
            di."matrícula",
            di."nome"               AS nome_discente,
            pj."código"            AS projeto_codigo,
            pj."nome"              AS projeto_nome,
            mbp."id"               AS membro_id,
            mbp."função"           AS funcao,
            mbp."cargaHoraria"     AS carga_horaria
        FROM "Discente" di
        JOIN "MembroDoProjeto" mbp
             ON di."membroDoProjetoId" = mbp."id"
        JOIN "Projeto" pj
             ON mbp."projetoCódigo" = pj."código"
        WHERE di."nome" ILIKE %s
        ORDER BY di."nome", pj."nome";
        """

        rows, colunas = run_query(query, (parametro,))
        df = pd.DataFrame(rows, columns=colunas)
        st.dataframe(df)



# ------------------------------------------------------------------------------
# Página principal de consultas
# ------------------------------------------------------------------------------
def consultas():
    st.title("Consultas Específicas")

    # Menu de escolhas
    opcoes = [
        "Docente Responsável por Laboratório",
        "Equipamentos por Laboratório",
        "Bolsas e Membros de Projeto",
        "Avaliações por Discente",
        "Discentes em Projetos"
    ]
    escolha = st.selectbox("Selecione a consulta que deseja realizar:", opcoes)

    st.write("---")

    if escolha == "Docente Responsável por Laboratório":
        consulta_docente_responsavel_laboratorio()

    elif escolha == "Equipamentos por Laboratório":
        consulta_equipamentos_por_laboratorio()

    elif escolha == "Bolsas e Membros de Projeto":
        consulta_bolsas_e_membros_do_projeto()

    elif escolha == "Avaliações por Discente":
        consulta_avaliacoes_por_discente()

    elif escolha == "Discentes em Projetos":
        consulta_discentes_em_projetos()


def main():
    consultas()


if __name__ == "__main__":
    main()
