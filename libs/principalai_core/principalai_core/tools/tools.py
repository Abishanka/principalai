from pydantic import BaseModel
from data.entity import Entity

class Tool(BaseModel):
    description: str
    parameters: Entity