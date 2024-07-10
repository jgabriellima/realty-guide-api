CREATE OR REPLACE FUNCTION real_estate.get_client_with_metadata(p_whatsapp TEXT)
RETURNS TABLE(
    id INT,
    name TEXT,
    whatsapp TEXT,
    created_at TIMESTAMP,
    client_metadata JSONB
) AS $$
BEGIN
RETURN QUERY
SELECT
    c.id,
    c.name,
    c.whatsapp,
    c.created_at,
    jsonb_agg(jsonb_build_object('parameter_name', cm.parameter_name, 'parameter_value_description', cm.parameter_value_description)) AS client_metadata
FROM real_estate.client c
         LEFT JOIN real_estate.client_metadata cm ON c.id = cm.client_id
WHERE c.whatsapp = p_whatsapp
GROUP BY c.id;
END;
$$ LANGUAGE plpgsql;
