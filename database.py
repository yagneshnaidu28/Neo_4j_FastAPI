import os
from neo4j import GraphDatabase, Session
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def get_db():
    session = driver.session()
    try:
        yield session
    finally:
        session.close()


def close_driver():
    driver.close()


# ---------- Schemas ----------

# Input schema (what client sends when creating/updating)
class TaskCreate(BaseModel):
    name: str
    task: str
    description: str


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    task: Optional[str] = None
    description: Optional[str] = None


# Output schema (what API returns)
class TaskResponse(BaseModel):
    id: str
    name: str
    task: str
    description: str


def generate_id(session: Session) -> str:
    query = "MATCH (t:Task) RETURN max(toInteger(t.id)) AS max_id"
    result = session.run(query)
    record = result.single()
    max_id = record["max_id"] if record and record["max_id"] is not None else 0
    return str(max_id + 1)