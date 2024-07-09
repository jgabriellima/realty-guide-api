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
