import importlib.util
import inspect
import os

from celery.local import PromiseProxy

from app.core.db.supabase_conn import SupabaseDB
from app.core.setup_logging import setup_logging

logger = setup_logging("Sync Celery Tasks to DB")


def sync():
    """
    Sync the tasks from the tasks module to the database

    :return: None
    """
    tasks = []

    base_dir = os.path.dirname(os.path.abspath(__file__))
    tasks_path = os.path.abspath(os.path.join(base_dir, '..', 'tasks.py'))

    tasks_module_spec = importlib.util.spec_from_file_location("app.tasks", tasks_path)
    tasks_module = importlib.util.module_from_spec(tasks_module_spec)
    tasks_module_spec.loader.exec_module(tasks_module)

    logger.info(f"Tasks from the tasks module: {dir(tasks_module)}")
    logger.info(len(inspect.getmembers(tasks_module)))

    for name, obj in inspect.getmembers(tasks_module):
        if isinstance(obj, PromiseProxy):
            print(f"Name: {name} - Obj: {obj} - Type: {type(obj)} - Is Function: {inspect.isfunction(obj)}")
            print(obj.__name__)
            if hasattr(obj, 'apply_async'):
                task_function = obj
                description = task_function.__doc__ or "No description available"
                tasks.append({
                    "function_name": task_function.__name__,
                    "description": description.strip()
                })

    if tasks:
        tasks_json = tasks
        logger.info(f"Syncing tasks to the database: {tasks}")
        supabase = SupabaseDB().client
        supabase.schema("real_estate").rpc("update_task_catalog", params={"tasks": tasks_json}).execute()
        logger.info(f"Tasks synced to the database: {tasks}")
        return tasks_json
    else:
        logger.info("No tasks found to sync to the database")
        return None


if __name__ == '__main__':
    sync()
