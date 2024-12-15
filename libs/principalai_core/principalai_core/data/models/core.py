from pydantic import BaseModel

class Entity(BaseModel):
    """Data entity. Present in input, output, messages and more"""
    def __init__(
        self, 
        name_: str, 
        description_: str, 
        entitytype_: str
    ):
        '''
        Use the following conventions for name and description
        
        1. If its a normal, long text message response from the LLM:
            name: message_{index}
            description: some description that may be useful for logs/definition
            
        2. If its an entity of interest (for example - places, names, objects, etc.)
            name: entity name
            description: some good description on what the entity is. This will affect accuracy and performance for future 
            responses

        Ultimately, you have the freedom to skip out on the separated entity paradigm. However, using it will give you better 
        accuracy.
        '''
        self.name: str = name_
        self.description: str = description_,
        self.entitytype = entitytype_