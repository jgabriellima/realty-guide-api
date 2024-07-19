CREATE OR REPLACE FUNCTION real_estate.get_property_with_metadata(
    p_url TEXT DEFAULT NULL,
    p_slug TEXT DEFAULT NULL,
    p_id INT DEFAULT NULL
)
RETURNS TABLE(
    id INT,
    id_reference TEXT,
    title TEXT,
    description TEXT,
    slug TEXT,
    url TEXT,
    total_price NUMERIC,
    iptu NUMERIC,
    condominium_fee NUMERIC,
    neighborhood TEXT,
    full_address TEXT,
    property_metadata JSONB,
    property_images JSONB
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
    jsonb_agg(DISTINCT jsonb_build_object('parameter_name', pm.parameter_name, 'parameter_value_description', pm.parameter_value_description)) AS property_metadata,
    jsonb_agg(DISTINCT jsonb_build_object('url', pi.url, 'caption', pi.caption)) AS property_images
FROM real_estate.property p
         LEFT JOIN real_estate.property_metadata pm ON p.id = pm.property_id
         LEFT JOIN real_estate.property_images pi ON p.id = pi.property_id
WHERE (p.url = p_url OR p_url IS NULL)
  AND (p.slug = p_slug OR p_slug IS NULL)
  AND (p.id = p_id OR p_id IS NULL)
GROUP BY p.id;
END;
$$ LANGUAGE plpgsql;
