from pydantic import BaseModel

class Entity(BaseModel):
    """Data entity. Present in input, output, messages and more"""
    def __init__(self, name_: str, description_: str):
        self.name: str = name_
        self.description: str = description_