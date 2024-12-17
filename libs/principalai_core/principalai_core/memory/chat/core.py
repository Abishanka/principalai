from pydantic import BaseModel

from principalai_core.memory import Memory

class ChatMemory(Memory):
    def __init__(self):
        super().__init__()
