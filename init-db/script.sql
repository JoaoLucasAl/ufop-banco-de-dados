CREATE TYPE "Sexo" AS ENUM ('F', 'M');

CREATE TABLE "Equipamento" (
    "nTombamento" SERIAL NOT NULL,
    "nModelo" INTEGER NOT NULL,
    "nome" VARCHAR(100) NOT NULL,
    "fabricante" VARCHAR(100) NOT NULL,
    "laboratórioId" INTEGER NOT NULL,

    CONSTRAINT "Equipamento_pkey" PRIMARY KEY ("nTombamento")
);

CREATE TABLE "Laboratório" (
    "id" SERIAL NOT NULL,
    "nome" VARCHAR(100) NOT NULL,
    "sala" SMALLINT NOT NULL,
    "prédio" VARCHAR(100) NOT NULL,

    CONSTRAINT "Laboratório_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "Docente" (
    "código" TEXT NOT NULL,
    "nome" VARCHAR(100) NOT NULL,
    "cpf" VARCHAR(11) NOT NULL,
    "salário" INTEGER NOT NULL,
    "sexo" "Sexo" NOT NULL,
    "efetividade" BOOLEAN NOT NULL,
    "dataNascimento" TIMESTAMP(3) NOT NULL,
    "dataAdmissão" TIMESTAMP(3) NOT NULL,
    "departamentoNome" VARCHAR(100) NOT NULL,

    CONSTRAINT "Docente_pkey" PRIMARY KEY ("código")
);

CREATE TABLE "DocenteResponsávelPorLaboratório" (
    "docenteCódigo" TEXT NOT NULL,
    "laboratórioId" INTEGER NOT NULL,
    "data" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "DocenteResponsávelPorLaboratório_pkey" PRIMARY KEY ("docenteCódigo","laboratórioId")
);

CREATE TABLE "Departamento" (
    "nome" VARCHAR(100) NOT NULL,
    "localização" TEXT NOT NULL,
    "cursoCódigo" VARCHAR(10) NOT NULL,

    CONSTRAINT "Departamento_pkey" PRIMARY KEY ("nome")
);

CREATE TABLE "Curso" (
    "código" VARCHAR(10) NOT NULL,
    "nome" VARCHAR(100) NOT NULL,
    "vagas" SMALLINT NOT NULL,
    "departamentoNome" TEXT NOT NULL,

    CONSTRAINT "Curso_pkey" PRIMARY KEY ("código")
);

CREATE TABLE "Discente" (
    "matrícula" VARCHAR(50) NOT NULL,
    "nome" VARCHAR(100) NOT NULL,
    "sexo" "Sexo" NOT NULL,
    "dataNascimento" TIMESTAMP(3) NOT NULL,
    "cursoCódigo" VARCHAR(10) NOT NULL,

    CONSTRAINT "Discente_pkey" PRIMARY KEY ("matrícula")
);

CREATE TABLE "Projeto" (
    "código" SERIAL NOT NULL,
    "nome" VARCHAR(100) NOT NULL,
    "departamentoNome" VARCHAR(100) NOT NULL,

    CONSTRAINT "Projeto_pkey" PRIMARY KEY ("código")
);

CREATE TABLE "Extensão" (
    "id" INTEGER NOT NULL,
    "áreaDePesquisa" VARCHAR(100) NOT NULL,

    CONSTRAINT "Extensão_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "Pesquisa" (
    "id" INTEGER NOT NULL,
    "objetivo" VARCHAR(100) NOT NULL,

    CONSTRAINT "Pesquisa_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "MembroDoProjeto" (
    "id"      SERIAL       NOT NULL,
    "docenteId"     TEXT         NULL,
    "discenteId"    VARCHAR(50)  NULL,
    "cargaHoraria"  SMALLINT     NOT NULL,
    "função"        VARCHAR(50)  NOT NULL,
    "projetoCódigo" INTEGER      NOT NULL,
    
    CONSTRAINT "MembroDoProjeto_pkey" PRIMARY KEY ("id"),

    -- Garante que somente um dos campos (docente ou discente) seja preenchido
    CONSTRAINT "chk_docente_ou_discente"
      CHECK (
        ("docenteId"  IS NOT NULL AND "discenteId"  IS NULL)
        OR
        ("docenteId"  IS NULL     AND "discenteId"  IS NOT NULL)
      )
);

CREATE TABLE "Bolsa" (
    "valor" SMALLINT NOT NULL,
    "dataInicio" TIMESTAMP(3) NOT NULL,
    "dataFim" TIMESTAMP(3) NOT NULL,
    "bolsistaId" SERIAL NOT NULL,
    "projetoCódigo" INTEGER NOT NULL,

    CONSTRAINT "Bolsa_pkey" PRIMARY KEY ("bolsistaId","projetoCódigo","dataInicio")
);

CREATE TABLE "Disciplina" (
    "nome" VARCHAR(30) NOT NULL,
    "créditos" SMALLINT NOT NULL,
    "departamentoNome" VARCHAR(100) NOT NULL,

    CONSTRAINT "Disciplina_pkey" PRIMARY KEY ("nome")
);

CREATE TABLE "Turma" (
    "disciplinaNome" VARCHAR(30) NOT NULL,
    "número" SMALLINT NOT NULL,
    "anoSemestre" VARCHAR(10) NOT NULL,
    "ementa" TEXT NOT NULL,
    "horárioInicio" TIMESTAMP(3) NOT NULL,
    "horárioFim" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Turma_pkey" PRIMARY KEY ("disciplinaNome","número","anoSemestre")
);

CREATE TABLE "TurmaAcessaLaboratório" (
    "disciplinaNome" VARCHAR(30) NOT NULL,
    "número" SMALLINT NOT NULL,
    "anoSemestre" VARCHAR(10) NOT NULL,
    "laboratórioId" INTEGER NOT NULL,
    "data" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "TurmaAcessaLaboratório_pkey" PRIMARY KEY ("disciplinaNome","número","anoSemestre","laboratórioId")
);

CREATE TABLE "Avaliação" (
    "disciplinaNome" VARCHAR(30) NOT NULL,
    "número" SMALLINT NOT NULL,
    "anoSemestre" VARCHAR(10) NOT NULL,
    "data" TIMESTAMP(3) NOT NULL,
    "peso" SMALLINT NOT NULL,
    "valor" SMALLINT NOT NULL,

    CONSTRAINT "Avaliação_pkey" PRIMARY KEY ("disciplinaNome","número","anoSemestre","data")
);

CREATE TABLE "DiscenteFazAvaliação" (
    "disciplinaNome" VARCHAR(30) NOT NULL,
    "número" SMALLINT NOT NULL,
    "anoSemestre" VARCHAR(10) NOT NULL,
    "data" TIMESTAMP(3) NOT NULL,
    "matrícula" VARCHAR(50) NOT NULL,
    "nota" SMALLINT NOT NULL,

    CONSTRAINT "DiscenteFazAvaliação_pkey" PRIMARY KEY ("disciplinaNome","número","anoSemestre","data","matrícula")
);

CREATE TABLE "DiscenteMatriculadoEmTurma" (
    "disciplinaNome" VARCHAR(30) NOT NULL,
    "número" SMALLINT NOT NULL,
    "anoSemestre" VARCHAR(10) NOT NULL,
    "matrícula" VARCHAR(50) NOT NULL,
    "nota" SMALLINT NOT NULL,
    "frequência" SMALLINT NOT NULL,

    CONSTRAINT "DiscenteMatriculadoEmTurma_pkey" PRIMARY KEY ("disciplinaNome","número","anoSemestre","matrícula")
);

CREATE TABLE "DocenteMinistraEmTurma" (
    "disciplinaNome" VARCHAR(30) NOT NULL,
    "número" SMALLINT NOT NULL,
    "anoSemestre" VARCHAR(10) NOT NULL,
    "código" TEXT NOT NULL,

    CONSTRAINT "DocenteMinistraEmTurma_pkey" PRIMARY KEY ("disciplinaNome","número","anoSemestre","código")
);

CREATE UNIQUE INDEX "Curso_nome_key" ON "Curso"("nome");

CREATE UNIQUE INDEX "Curso_departamentoNome_key" ON "Curso"("departamentoNome");

CREATE UNIQUE INDEX "Bolsa_bolsistaId_key" ON "Bolsa"("bolsistaId");

ALTER TABLE "Equipamento" ADD CONSTRAINT "Equipamento_laboratórioId_fkey" FOREIGN KEY ("laboratórioId") REFERENCES "Laboratório"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Docente" ADD CONSTRAINT "Docente_departamentoNome_fkey" FOREIGN KEY ("departamentoNome") REFERENCES "Departamento"("nome") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "DocenteResponsávelPorLaboratório" ADD CONSTRAINT "DocenteResponsávelPorLaboratório_docenteCódigo_fkey" FOREIGN KEY ("docenteCódigo") REFERENCES "Docente"("código") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "DocenteResponsávelPorLaboratório" ADD CONSTRAINT "DocenteResponsávelPorLaboratório_laboratórioId_fkey" FOREIGN KEY ("laboratórioId") REFERENCES "Laboratório"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Curso" ADD CONSTRAINT "Curso_departamentoNome_fkey" FOREIGN KEY ("departamentoNome") REFERENCES "Departamento"("nome") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Discente" ADD CONSTRAINT "Discente_cursoCódigo_fkey" FOREIGN KEY ("cursoCódigo") REFERENCES "Curso"("código") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Projeto" ADD CONSTRAINT "Projeto_departamentoNome_fkey" FOREIGN KEY ("departamentoNome") REFERENCES "Departamento"("nome") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Extensão" ADD CONSTRAINT "Extensão_id_fkey" FOREIGN KEY ("id") REFERENCES "Projeto"("código") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Pesquisa" ADD CONSTRAINT "Pesquisa_id_fkey" FOREIGN KEY ("id") REFERENCES "Projeto"("código") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "MembroDoProjeto" ADD CONSTRAINT "MembroDoProjeto_docente_fkey" FOREIGN KEY ("docenteId") REFERENCES "Docente"("código") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "MembroDoProjeto" ADD CONSTRAINT "MembroDoProjeto_discente_fkey" FOREIGN KEY ("discenteId") REFERENCES "Discente"("matrícula") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "MembroDoProjeto" ADD CONSTRAINT "MembroDoProjeto_projetoCódigo_fkey" FOREIGN KEY ("projetoCódigo") REFERENCES "Projeto"("código") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Bolsa" ADD CONSTRAINT "Bolsa_bolsistaId_fkey" FOREIGN KEY ("bolsistaId") REFERENCES "MembroDoProjeto"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Bolsa" ADD CONSTRAINT "Bolsa_projetoCódigo_fkey" FOREIGN KEY ("projetoCódigo") REFERENCES "Projeto"("código") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Disciplina" ADD CONSTRAINT "Disciplina_departamentoNome_fkey" FOREIGN KEY ("departamentoNome") REFERENCES "Departamento"("nome") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Turma" ADD CONSTRAINT "Turma_disciplinaNome_fkey" FOREIGN KEY ("disciplinaNome") REFERENCES "Disciplina"("nome") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "TurmaAcessaLaboratório" ADD CONSTRAINT "TurmaAcessaLaboratório_disciplinaNome_número_anoSemestre_fkey" FOREIGN KEY ("disciplinaNome", "número", "anoSemestre") REFERENCES "Turma"("disciplinaNome", "número", "anoSemestre") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "TurmaAcessaLaboratório" ADD CONSTRAINT "TurmaAcessaLaboratório_laboratórioId_fkey" FOREIGN KEY ("laboratórioId") REFERENCES "Laboratório"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Avaliação" ADD CONSTRAINT "Avaliação_disciplinaNome_número_anoSemestre_fkey" FOREIGN KEY ("disciplinaNome", "número", "anoSemestre") REFERENCES "Turma"("disciplinaNome", "número", "anoSemestre") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "DiscenteFazAvaliação" ADD CONSTRAINT "DiscenteFazAvaliação_disciplinaNome_número_anoSemestre__fkey" FOREIGN KEY ("disciplinaNome", "número", "anoSemestre", "data") REFERENCES "Avaliação"("disciplinaNome", "número", "anoSemestre", "data") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "DiscenteFazAvaliação" ADD CONSTRAINT "DiscenteFazAvaliação_matrícula_fkey" FOREIGN KEY ("matrícula") REFERENCES "Discente"("matrícula") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "DiscenteMatriculadoEmTurma" ADD CONSTRAINT "DiscenteMatriculadoEmTurma_disciplinaNome_número_anoSemes_fkey" FOREIGN KEY ("disciplinaNome", "número", "anoSemestre") REFERENCES "Turma"("disciplinaNome", "número", "anoSemestre") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "DiscenteMatriculadoEmTurma" ADD CONSTRAINT "DiscenteMatriculadoEmTurma_matrícula_fkey" FOREIGN KEY ("matrícula") REFERENCES "Discente"("matrícula") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "DocenteMinistraEmTurma" ADD CONSTRAINT "DocenteMinistraEmTurma_disciplinaNome_número_anoSemestre_fkey" FOREIGN KEY ("disciplinaNome", "número", "anoSemestre") REFERENCES "Turma"("disciplinaNome", "número", "anoSemestre") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "DocenteMinistraEmTurma" ADD CONSTRAINT "DocenteMinistraEmTurma_código_fkey" FOREIGN KEY ("código") REFERENCES "Docente"("código") ON DELETE RESTRICT ON UPDATE CASCADE;

INSERT INTO "Departamento" ("nome", "localização", "cursoCódigo")
VALUES
('Computação', 'Bloco A', 'C01'),
('Matemática', 'Bloco B', 'C02'),
('Física',     'Bloco C', 'C03');

INSERT INTO "Curso" ("código", "nome", "vagas", "departamentoNome")
VALUES
('COMP1', 'Bacharelado em Ciência da Computação', 50, 'Computação'),
('MAT1',  'Licenciatura em Matemática',           40, 'Matemática'),
('FIS1',  'Bacharelado em Física',                35, 'Física');

INSERT INTO "Laboratório" ("id", "nome", "sala", "prédio")
VALUES
(1, 'LabComp1', 101, 'Prédio de Computação'),
(2, 'LabMat1',  201, 'Prédio de Matemática'),
(3, 'LabFis1',  301, 'Prédio de Física');

INSERT INTO "Equipamento" ("nModelo", "nome", "fabricante", "laboratórioId")
VALUES
(100, 'Computador Dell',  'Dell',                1),
(200, 'Impressora HP',    'HP',                  1),
(300, 'Calculadora TI',   'Texas Instruments',   2);

INSERT INTO "Docente" 
("código", "nome", "cpf", "salário", "sexo", "efetividade", 
 "dataNascimento", "dataAdmissão", "departamentoNome")
VALUES
('D001', 'Alice', '11111111111', 5000, 'F', TRUE, 
 '1985-01-01 00:00:00', '2010-02-15 00:00:00', 'Computação'),
('D002', 'Maria',   '22222222222', 5500, 'M', FALSE,
 '1975-05-10 00:00:00', '2012-09-10 00:00:00', 'Matemática'),
('D003', 'Carol', '33333333333', 6000, 'F', TRUE, 
 '1990-07-07 00:00:00', '2015-01-20 00:00:00', 'Física'),
('D004', 'Heitor',  '44444444444', 4500, 'F', FALSE, 
 '1990-10-10 00:00:00', '2020-08-08 00:00:00', 'Computação'),
('D005', 'Hugo',  '55555555555', 4800, 'M', TRUE,  
 '1988-03-03 00:00:00', '2019-05-05 00:00:00', 'Matemática'),
('D006', 'Irene', '66666666666', 5200, 'F', TRUE,  
 '1979-11-11 00:00:00', '2018-12-12 00:00:00', 'Física');

INSERT INTO "DocenteResponsávelPorLaboratório" ("docenteCódigo", "laboratórioId", "data")
VALUES
('D001', 1, '2020-01-01 00:00:00'),
('D002', 2, '2021-01-01 00:00:00'),
('D003', 3, '2022-01-01 00:00:00');

INSERT INTO "Disciplina" ("nome", "créditos", "departamentoNome")
VALUES
('Estrutura de Dados', 6, 'Computação'),
('Cálculo I',          4, 'Matemática'),
('Mecânica',           5, 'Física');

INSERT INTO "Turma" 
("disciplinaNome", "número", "anoSemestre", "ementa", "horárioInicio", "horárioFim")
VALUES
('Estrutura de Dados', 1, '2025.1', 'Ementa ED',      '2025-02-20 08:00:00', '2025-02-20 10:00:00'),
('Cálculo I',          1, '2025.1', 'Ementa Calc I',  '2025-02-20 10:00:00', '2025-02-20 12:00:00'),
('Mecânica',           1, '2025.1', 'Ementa Mecânica','2025-02-20 14:00:00', '2025-02-20 16:00:00');

INSERT INTO "TurmaAcessaLaboratório" 
("disciplinaNome", "número", "anoSemestre", "laboratórioId", "data")
VALUES
('Estrutura de Dados', 1, '2025.1', 1, '2025-03-01 09:00:00'),
('Cálculo I',          1, '2025.1', 2, '2025-03-02 11:00:00'),
('Mecânica',           1, '2025.1', 3, '2025-03-03 15:00:00');

INSERT INTO "Avaliação" 
("disciplinaNome", "número", "anoSemestre", "data", "peso", "valor")
VALUES
('Estrutura de Dados', 1, '2025.1', '2025-04-01 08:00:00', 2, 10),
('Cálculo I',          1, '2025.1', '2025-04-02 10:00:00', 2, 10),
('Mecânica',           1, '2025.1', '2025-04-03 14:00:00', 2, 10);

INSERT INTO "Discente" 
("matrícula", "nome", "sexo", "dataNascimento", "cursoCódigo")
VALUES
('S001', 'Daniel', 'M', '2002-01-01 00:00:00', 'COMP1'),
('S002', 'João',    'F', '2001-05-05 00:00:00', 'MAT1'),
('S003', 'Maria',  'M', '2000-03-03 00:00:00', 'FIS1'),
('S004', 'Beatriz',  'F', '2002-02-02 00:00:00', 'COMP1'),
('S005', 'José',  'M', '2001-06-06 00:00:00', 'MAT1'),
('S006', 'Josué', 'F', '2000-09-09 00:00:00', 'FIS1');

INSERT INTO "DiscenteFazAvaliação"
("disciplinaNome", "número", "anoSemestre", "data", "matrícula", "nota")
VALUES
('Estrutura de Dados', 1, '2025.1', '2025-04-01 08:00:00', 'S001', 9),
('Cálculo I',          1, '2025.1', '2025-04-02 10:00:00', 'S002', 8),
('Mecânica',           1, '2025.1', '2025-04-03 14:00:00', 'S003', 7);

INSERT INTO "DiscenteMatriculadoEmTurma"
("disciplinaNome", "número", "anoSemestre", "matrícula", "nota", "frequência")
VALUES
('Estrutura de Dados', 1, '2025.1', 'S001', 9,  95),
('Cálculo I',          1, '2025.1', 'S002', 8,  90),
('Mecânica',           1, '2025.1', 'S003', 7,  80);

INSERT INTO "DocenteMinistraEmTurma"
("disciplinaNome", "número", "anoSemestre", "código")
VALUES
('Estrutura de Dados', 1, '2025.1', 'D001'),
('Cálculo I',          1, '2025.1', 'D002'),
('Mecânica',           1, '2025.1', 'D003');

INSERT INTO "Projeto"
("código", "nome", "departamentoNome")
VALUES
(1, 'Projeto Computação', 'Computação'),
(2, 'Projeto Matemática', 'Matemática'),
(3, 'Projeto Física',     'Física');

INSERT INTO "Extensão"
("id", "áreaDePesquisa")
VALUES
(1, 'Inteligência Artificial'),
(2, 'Educação Matemática'),
(3, 'Astrofísica');

INSERT INTO "Pesquisa"
("id", "objetivo")
VALUES
(1, 'Pesquisas em IA'),
(2, 'Pesquisas em métodos de ensino'),
(3, 'Pesquisas em mecânica quântica');

INSERT INTO "MembroDoProjeto"
("discenteId", "cargaHoraria", "função", "projetoCódigo")
VALUES
('S001', 10, 'Pesquisador', 1),
('S002', 10, 'Pesquisador', 2),
('S003', 10, 'Pesquisador', 3);

INSERT INTO "MembroDoProjeto"
("docenteId", "cargaHoraria", "função", "projetoCódigo")
VALUES
('D001', 12, 'Orientador', 1),
('D002', 12, 'Orientador', 2),
('D003', 12, 'Orientador', 3);

INSERT INTO "Bolsa"
("valor", "dataInicio", "dataFim", "bolsistaId", "projetoCódigo")
VALUES
(1000, '2025-02-01 00:00:00', '2025-07-01 00:00:00', 1, 1),
( 800, '2025-03-01 00:00:00', '2025-07-01 00:00:00', 2, 2),
(1200, '2025-01-15 00:00:00', '2025-06-15 00:00:00', 3, 3);
