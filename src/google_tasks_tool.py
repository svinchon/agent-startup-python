
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_auth import authenticate_google

def list_task_lists():
    """Lists the user's task lists."""
    creds = authenticate_google()
    if not creds:
        return "Authentication failed. Please ensure credentials.json is set up correctly."

    try:
        service = build("tasks", "v1", credentials=creds)

        results = service.tasklists().list(maxResults=10).execute()
        items = results.get("items", [])

        if not items:
            return "No task lists found."

        task_lists = "Task lists:\n"
        for item in items:
            task_lists += f"- {item['title']} ({item['id']})\n"
        return task_lists

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def list_tasks(task_list_id: str):
    """Lists the tasks in a specific task list."""
    creds = authenticate_google()
    if not creds:
        return "Authentication failed. Please ensure credentials.json is set up correctly."

    try:
        service = build("tasks", "v1", credentials=creds)

        results = service.tasks().list(tasklist=task_list_id).execute()
        items = results.get("items", [])

        if not items:
            return f"No tasks found in task list {task_list_id}."

        tasks = f"Tasks in list {task_list_id}:\n"
        for item in items:
            tasks += f"- {item['title']} ({item['id']})\n"
        return tasks

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def create_task(task_list_id: str, title: str, notes: str = None):
    """Creates a new task."""
    creds = authenticate_google()
    if not creds:
        return "Authentication failed. Please ensure credentials.json is set up correctly."

    try:
        service = build("tasks", "v1", credentials=creds)

        task = {
            'title': title,
            'notes': notes
        }

        result = service.tasks().insert(tasklist=task_list_id, body=task).execute()
        return f"Task created: {result.get('title')}"

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def update_task(task_list_id: str, task_id: str, title: str, notes: str = None):
    """Updates a task."""
    creds = authenticate_google()
    if not creds:
        return "Authentication failed. Please ensure credentials.json is set up correctly."

    try:
        service = build("tasks", "v1", credentials=creds)

        task = service.tasks().get(tasklist=task_list_id, task=task_id).execute()
        task['title'] = title
        task['notes'] = notes

        result = service.tasks().update(tasklist=task_list_id, task=task_id, body=task).execute()
        return f"Task updated: {result.get('title')}"

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def delete_task(task_list_id: str, task_id: str):
    """Deletes a task."""
    creds = authenticate_google()
    if not creds:
        return "Authentication failed. Please ensure credentials.json is set up correctly."

    try:
        service = build("tasks", "v1", credentials=creds)

        service.tasks().delete(tasklist=task_list_id, task=task_id).execute()
        return "Task deleted."

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
