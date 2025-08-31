import os
from notion_client import Client
from dotenv import load_dotenv
from pathlib import Path

# === Load .env file ===
dotenv_path = Path("notion.env")
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    raise FileNotFoundError("Missing `notion.env` file in current directory.")

# === Load Notion API credentials ===
notion_token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")

if not notion_token or not db_id:
    raise ValueError("NOTION_TOKEN or NOTION_DATABASE_ID is missing or invalid.")

notion = Client(auth=notion_token)

# === Fetch tasks ===
def fetch_notion_tasks(limit=10, category=None, status=None, sort_by="xp"):
    try:
        filters = []

        # Status filter
        if status and status != "All":
            filters.append({"property": "status", "select": {"equals": status}})
        else:
            filters.append({"property": "status", "select": {"does_not_equal": "Done"}})

        # Category filter
        if category and category != "All":
            filters.append({"property": "category", "select": {"equals": category}})

        query = {
            "database_id": db_id,
            "page_size": limit
        }

        if filters:
            query["filter"] = {"and": filters}

        result = notion.databases.query(**query)

        tasks = []
        for row in result["results"]:
            props = row.get("properties", {})

            task_name = props.get("task", {}).get("title", [])
            name = task_name[0]["text"]["content"] if task_name else "Untitled"

            status_name = props.get("status", {}).get("select", {}).get("name", "Unknown")
            category_name = props.get("category", {}).get("select", {}).get("name", "Uncategorized")
            xp_score = props.get("xp_score", {}).get("number", 0)
            roi_score = props.get("roi_score", {}).get("number", 0)

            reason_text = props.get("reason", {}).get("rich_text", [])
            reason = reason_text[0]["text"]["content"] if reason_text else "No reason provided"

            tasks.append({
                "name": name,
                "status": status_name,
                "category": category_name,
                "xp": xp_score,
                "roi": roi_score,
                "reason": reason
            })

        # Sort tasks
        sort_by = sort_by.lower()
        if sort_by in ("xp", "roi", "name"):
            tasks.sort(key=lambda x: x.get(sort_by, 0), reverse=(sort_by != "name"))

        return tasks

    except Exception as e:
        return [{"name": f"Error: {str(e)}", "status": "Error"}]


# === Mark a task as complete ===
def mark_task_complete(task_name):
    try:
        results = notion.databases.query(
            database_id=db_id,
            filter={"property": "task", "title": {"equals": task_name}},
        )
        if results["results"]:
            task_id = results["results"][0]["id"]
            notion.pages.update(
                page_id=task_id,
                properties={"status": {"select": {"name": "Done"}}}
            )
            return True
        return False
    except Exception as e:
        print(f"Error marking task complete: {e}")
        return False
