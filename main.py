from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import os
import openai
import subprocess
import json

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

app = FastAPI()

class TaskRequest(BaseModel):
    task: str

@app.post("/run")
def run_task(request: TaskRequest):
    """Executes a plain-English task."""
    task_description = request.task
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an automation agent that converts user tasks into JSON-based operations."},
            {"role": "user", "content": task_description}
        ],
        api_key=AIPROXY_TOKEN
    )
    
    try:
        task_json = json.loads(response["choices"][0]["message"]["content"])
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse LLM response")
    
    try:
        output = execute_task(task_json)
        return {"status": "success", "output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
def read_file(path: str = Query(..., description="Path to the file")):
    """Returns the content of the specified file."""
    if not path.startswith("/data/"):
        raise HTTPException(status_code=403, detail="Access to this file is not allowed")
    
    try:
        with open(path, "r") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")


def execute_task(task_json):
    operation = task_json.get("operation")
    parameters = task_json.get("parameters", {})
    
    if operation == "count_weekdays":
        return count_weekdays(parameters)
    elif operation == "sort_contacts":
        return sort_contacts(parameters)
    else:
        raise ValueError("Unsupported operation")

#task
def count_weekdays(params):
    file_path = params.get("file_path")
    weekday_name = params.get("weekday_name")
    output_path = params.get("output_path")
    
    if not file_path.startswith("/data/") or not output_path.startswith("/data/"):
        raise PermissionError("Invalid file path")
    
    with open(file_path, "r") as f:
        dates = f.readlines()
    
    count = sum(1 for date in dates if weekday_name in date)
    
    with open(output_path, "w") as f:
        f.write(str(count))
    
    return f"Counted {count} {weekday_name}s"

def sort_contacts(params):
    input_path = params.get("input_path")
    output_path = params.get("output_path")
    
    if not input_path.startswith("/data/") or not output_path.startswith("/data/"):
        raise PermissionError("Invalid file path")
    
    with open(input_path, "r") as f:
        contacts = json.load(f)
    
    sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))
    
    with open(output_path, "w") as f:
        json.dump(sorted_contacts, f, indent=4)
    
    return "Sorted contacts successfully"
