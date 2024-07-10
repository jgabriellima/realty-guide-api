-- Criar o esquema se não existir
CREATE SCHEMA IF NOT EXISTS real_estate;

-- Tabela property
CREATE TABLE real_estate.property
(
    id              SERIAL PRIMARY KEY,
    id_reference    VARCHAR(255)        NOT NULL,
    slug            VARCHAR(255) UNIQUE NOT NULL,
    url             VARCHAR(255)        NOT NULL,
    total_price     NUMERIC             NOT NULL,
    iptu            NUMERIC             NOT NULL,
    condominium_fee NUMERIC             NOT NULL,
    neighborhood    VARCHAR(255),
    full_address    VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_property_id_reference ON real_estate.property (id_reference);
CREATE INDEX idx_property_slug ON real_estate.property (slug);
CREATE INDEX idx_property_neighborhood ON real_estate.property (neighborhood);

-- Tabela property_metadata
CREATE TABLE real_estate.property_metadata
(
    id                          SERIAL PRIMARY KEY,
    property_id                 INT REFERENCES real_estate.property (id) ON DELETE CASCADE,
    parameter_name              VARCHAR(255) NOT NULL,
    parameter_value_description TEXT         NOT NULL,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_property_metadata_property_id ON real_estate.property_metadata (property_id);

-- Tabela property_images
CREATE TABLE real_estate.property_images
(
    id          SERIAL PRIMARY KEY,
    property_id INT REFERENCES real_estate.property (id) ON DELETE CASCADE,
    url         VARCHAR(255) NOT NULL,
    caption     TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_property_images_property_id ON real_estate.property_images (property_id);

-- Tabela client
CREATE TABLE real_estate.client
(
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255)       NOT NULL,
    whatsapp   VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_client_whatsapp ON real_estate.client (whatsapp);

-- Tabela client_metadata
CREATE TABLE real_estate.client_metadata
(
    id                          SERIAL PRIMARY KEY,
    client_id                   INT REFERENCES real_estate.client (id) ON DELETE CASCADE,
    parameter_name              VARCHAR(255) NOT NULL,
    parameter_value_description TEXT         NOT NULL,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_client_metadata_client_id ON real_estate.client_metadata (client_id);

-- Tabela real_estate_agent
CREATE TABLE real_estate.real_estate_agent
(
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255)       NOT NULL,
    whatsapp   VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_real_estate_agent_whatsapp ON real_estate.real_estate_agent (whatsapp);

-- Tabela real_estate_agent_metadata
CREATE TABLE real_estate.real_estate_agent_metadata
(
    id                          SERIAL PRIMARY KEY,
    agent_id                    INT REFERENCES real_estate.real_estate_agent (id) ON DELETE CASCADE,
    parameter_name              VARCHAR(255) NOT NULL,
    parameter_value_description TEXT         NOT NULL,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_real_estate_agent_metadata_agent_id ON real_estate.real_estate_agent_metadata (agent_id);


-- Tabela task_catalog para definir e gerenciar as funções que podem ser executadas
CREATE TABLE real_estate.task_catalog
(
    id            SERIAL PRIMARY KEY,
    function_name VARCHAR(255) UNIQUE          NOT NULL,
    description   TEXT                         NOT NULL,
    status        VARCHAR(50) DEFAULT 'active' NOT NULL,
    created_at    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_task_catalog_function_name ON real_estate.task_catalog (function_name);

-- Tabela tasks para gerenciar tarefas em background
CREATE TABLE real_estate.tasks
(
    id            SERIAL PRIMARY KEY,
    task_id       VARCHAR(255) UNIQUE NOT NULL,
    function_name VARCHAR(255) REFERENCES real_estate.task_catalog (function_name),
    agent_id      INT REFERENCES real_estate.real_estate_agent (id),
    description   TEXT                NOT NULL,
    status        VARCHAR(50)         NOT NULL,
    error         TEXT,
    input_data    JSONB,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices adicionais para melhorar a performance das consultas
CREATE INDEX idx_tasks_task_id ON real_estate.tasks (task_id);
CREATE INDEX idx_tasks_function_name ON real_estate.tasks (function_name);
CREATE INDEX idx_tasks_status ON real_estate.tasks (status);
CREATE INDEX idx_tasks_agent_id ON real_estate.tasks (agent_id);


-- Conceder permissões de uso no esquema real_estate
GRANT
USAGE
ON
SCHEMA
real_estate TO anon;
GRANT USAGE ON SCHEMA
real_estate TO service_role;

-- Conceder permissões de SELECT, INSERT, UPDATE, DELETE em todas as tabelas do esquema real_estate
GRANT
SELECT,
INSERT
,
UPDATE,
DELETE
ON ALL TABLES IN SCHEMA real_estate TO anon;
GRANT
SELECT,
INSERT
,
UPDATE,
DELETE
ON ALL TABLES IN SCHEMA real_estate TO service_role;

-- Conceder permissões de EXECUTE em todas as funções do esquema real_estate
GRANT
EXECUTE
ON
ALL
FUNCTIONS IN SCHEMA real_estate TO anon;
GRANT EXECUTE ON ALL
FUNCTIONS IN SCHEMA real_estate TO service_role;

-- Conceder permissões de SELECT e USAGE em todas as sequências do esquema real_estate
GRANT
SELECT, USAGE
ON ALL SEQUENCES IN SCHEMA real_estate TO anon;
GRANT
SELECT, USAGE
ON ALL SEQUENCES IN SCHEMA real_estate TO service_role;
