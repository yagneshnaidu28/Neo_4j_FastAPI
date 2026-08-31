import os
import uuid
from neo4j import GraphDatabase
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


def generate_id() -> str:
    return str(uuid.uuid4())