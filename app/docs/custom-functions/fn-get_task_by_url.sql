CREATE OR REPLACE FUNCTION real_estate.get_task_by_url(url TEXT, statuses TEXT[])
RETURNS TABLE(
    task_id VARCHAR,
    function_name VARCHAR,
    description TEXT,
    status VARCHAR,
    input_data JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
RETURN QUERY
SELECT
    real_estate.tasks.task_id,
    real_estate.tasks.function_name,
    real_estate.tasks.description,
    real_estate.tasks.status,
    real_estate.tasks.input_data,
    real_estate.tasks.created_at,
    real_estate.tasks.updated_at
FROM real_estate.tasks
WHERE jsonb_exists(real_estate.tasks.input_data, 'url')
  AND (real_estate.tasks.input_data->>'url')::TEXT = url
      AND real_estate.tasks.status = ANY(statuses);
END;
$$ LANGUAGE plpgsql;
