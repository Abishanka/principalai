from pydantic import BaseModel

class Memory(BaseModel):
    def __init__(self):
        self.localMemory = True
        
    @property
    def __str__():
        return None
    
    