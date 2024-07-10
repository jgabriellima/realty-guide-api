CREATE OR REPLACE FUNCTION real_estate.get_property_with_metadata(url TEXT)
RETURNS TABLE(
    id INT,
    id_reference TEXT,
    title TEXT,
    description TEXT,
    slug TEXT,
    url TEXT,
    total_price FLOAT,
    iptu FLOAT,
    condominium_fee FLOAT,
    neighborhood TEXT,
    full_address TEXT,
    property_metadata JSONB
) AS $$

BEGIN
RETURN QUERY
SELECT
    p.id,
    p.id_reference,
    p.title,
    p.description,
    p.slug,
    p.url,
    p.total_price,
    p.iptu,
    p.condominium_fee,
    p.neighborhood,
    p.full_address,
    jsonb_agg(jsonb_build_object('parameter_name', pm.parameter_name, 'parameter_value_description', pm.parameter_value_description)) AS property_metadata
FROM real_estate.property p
         LEFT JOIN real_estate.property_metadata pm ON p.id = pm.property_id
WHERE (p.url = p_url OR p.slug = p_slug)
GROUP BY p.id;
END;
$$ LANGUAGE plpgsql;
