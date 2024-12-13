from pydantic import BaseModel
from typing import Optional

from principalai_core.data.entity import Entity

class Tool(BaseModel):
    def __init__(self):
        self.description: str
        self.inputParameters: Optional[list[Entity]]
        self.outputParameters: Optional[list[Entity]]