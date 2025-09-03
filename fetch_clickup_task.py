import os
import json
import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("CLICKUP_API_KEY")

if not API_KEY:
    raise ValueError("Missing CLICKUP_API_KEY in .env file")

# Hardcoded ClickUp task URL (example)
task_url = "https://app.clickup.com/t/20419954/PERSON-20340"

# Step 1: Extract ClickUp task ID from the URL
def extract_task_id(url):
    try:
        parts = url.strip("/").split("/")
        return parts[-1]  # e.g. "PERSON-20467"
    except Exception as e:
        raise ValueError(f"Unable to parse ClickUp task ID from URL: {e}")

task_short_id = extract_task_id(task_url)

# Step 2: Find the real task ID via the API
headers = {
    "Authorization": API_KEY
}

search_endpoint = "https://api.clickup.com/api/v2/task"

params = {
    "custom_task_ids": "true",
    "team_id": "20419954",
    "include_markdown_description": "true"  # ✅ ensures markdown comes back
}

# Construct full URL using short task key
task_detail_url = f"{search_endpoint}/{task_short_id}"

response = requests.get(task_detail_url, headers=headers, params=params)

if response.status_code != 200:
    raise RuntimeError(f"Failed to fetch task. Status: {response.status_code}, Response: {response.text}")

task_data = response.json()

# Step 3: Save the task JSON locally
with open("task_data.json", "w", encoding="utf-8") as f:
    json.dump(task_data, f, indent=2)

print("✅ Task data saved to task_data.json")
