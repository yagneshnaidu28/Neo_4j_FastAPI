from fastapi import FastAPI, Depends, HTTPException
from neo4j import Session

from database import get_db, close_driver, generate_id, TaskCreate, TaskUpdate, TaskResponse

app = FastAPI()


@app.on_event("shutdown")
def shutdown_event():
    close_driver()


# CREATE
@app.post("/tasks", response_model=TaskResponse)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task_id = generate_id()
    query = """
    CREATE (t:Task {id: $id, name: $name, task: $task, description: $description})
    RETURN t
    """
    result = db.run(query, id=task_id, name=payload.name,
                     task=payload.task, description=payload.description)
    record = result.single()
    return dict(record["t"])


# READ ALL
@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    query = "MATCH (t:Task) RETURN t"
    result = db.run(query)
    return [dict(record["t"]) for record in result]


# READ ONE
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    query = "MATCH (t:Task {id: $id}) RETURN t"
    result = db.run(query, id=task_id)
    record = result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(record["t"])


# UPDATE
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join([f"t.{key} = ${key}" for key in updates])
    query = f"""
    MATCH (t:Task {{id: $id}})
    SET {set_clause}
    RETURN t
    """
    result = db.run(query, id=task_id, **updates)
    record = result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(record["t"])


# DELETE
@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    query = """
    MATCH (t:Task {id: $id})
    DELETE t
    RETURN COUNT(t) AS deleted_count
    """
    result = db.run(query, id=task_id)
    record = result.single()
    if record["deleted_count"] == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": f"Task {task_id} deleted"}