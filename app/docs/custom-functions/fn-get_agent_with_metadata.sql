CREATE OR REPLACE FUNCTION real_estate.get_agent_with_metadata(p_id INT, p_whatsapp TEXT)
RETURNS TABLE(
    id INT,
    name TEXT,
    whatsapp TEXT,
    created_at TIMESTAMP,
    agent_metadata JSONB
) AS $$
BEGIN
RETURN QUERY
SELECT
    a.id,
    a.name,
    a.whatsapp,
    a.created_at,
    jsonb_agg(jsonb_build_object('parameter_name', am.parameter_name, 'parameter_value_description', am.parameter_value_description)) AS agent_metadata
FROM real_estate.real_estate_agent a
         LEFT JOIN real_estate.real_estate_agent_metadata am ON a.id = am.agent_id
WHERE (a.id = p_id OR a.whatsapp = p_whatsapp)
GROUP BY a.id;
END;
$$ LANGUAGE plpgsql;
