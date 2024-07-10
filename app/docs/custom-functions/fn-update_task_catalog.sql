-- Função para atualizar o catálogo de tarefas
CREATE OR REPLACE FUNCTION real_estate.update_task_catalog(tasks JSONB)
RETURNS VOID AS $$
DECLARE
task RECORD;
BEGIN
    -- Marcar todas as tarefas existentes como inativas
UPDATE real_estate.task_catalog
SET status = 'inactive';

-- Inserir ou atualizar as tarefas da lista
FOR task IN SELECT * FROM jsonb_array_elements(tasks) LOOP
    INSERT INTO real_estate.task_catalog (function_name, description, status, updated_at)
            VALUES (task->>'function_name', task->>'description', 'active', CURRENT_TIMESTAMP)
            ON CONFLICT (function_name) DO UPDATE
                                               SET description = EXCLUDED.description,
                                               status = 'active',
                                               updated_at = EXCLUDED.updated_at;
END LOOP;

    -- Remover tarefas que não estão mais na lista (opcional)
DELETE FROM real_estate.task_catalog
WHERE status = 'inactive';
END;
$$ LANGUAGE plpgsql;
