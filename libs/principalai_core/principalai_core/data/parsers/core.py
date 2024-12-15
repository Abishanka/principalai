from pydantic import BaseModel
from typing import Type

from principalai_core.data.models.core import Entity

def entity_parameter_parser(entityParameters:Type[BaseModel]) -> list[Entity]:
    """Parse entities when they are passed in as parameters through a Pydantic schema"""
    parsedParameters = []
    for parameterName, parameterInfo in entityParameters.model_fields.items():
        if parameterInfo.description is None or parameterInfo.description is "":
            raise ValueError(f'''Description is an empty string. Please enter a valid description; Invalid or incorrect 
                             descriptions will impact performance negatively.''')
        parsedParameters.append(
            Entity(name_=parameterName, description_=parameterInfo.description, entitytype_=parameterInfo.annotation)
        )
    return parsedParameters