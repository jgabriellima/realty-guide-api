-- Conceder permissões de uso no esquema real_estate
GRANT USAGE ON SCHEMA real_estate TO anon;
GRANT USAGE ON SCHEMA real_estate TO service_role;

-- Conceder permissões de SELECT, INSERT, UPDATE, DELETE em todas as tabelas do esquema real_estate
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA real_estate TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA real_estate TO service_role;

-- Conceder permissões de EXECUTE em todas as funções do esquema real_estate
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA real_estate TO anon;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA real_estate TO service_role;

-- Conceder permissões de SELECT e USAGE em todas as sequências do esquema real_estate
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA real_estate TO anon;
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA real_estate TO service_role;
