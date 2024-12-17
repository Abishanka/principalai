from pydantic import BaseModel
from typing import Type

from principalai_core.data.core import Entity

def entity_parameter_parser(entityParameters:Type[BaseModel]) -> list[Entity]:
    """Parse entities when they are passed in as parameters through a Pydantic schema"""
    parsedParameters = []
    for parameterName, parameterInfo in entityParameters.model_fields.items():
        if parameterInfo.description is None or parameterInfo.description == "":
            raise ValueError(f'''Description is an empty string. Please enter a valid description; Invalid or incorrect 
                             descriptions will impact performance negatively.''')
        parsedParameters.append(
            Entity(name_=parameterName, description_=parameterInfo.description, entitytype_=parameterInfo.annotation)
        )
    return parsedParameters

def defaultApiToolInputParser(
    inputParameterSchemaBaseModel: BaseModel,
    *args,
    **kwargs
):
    """Default parser for HTTP Requests. Since the default type is GET, the data gets places in params"""
    return {
        "params": (inputParameterSchemaBaseModel(*args, **kwargs)).model_dump()
    }