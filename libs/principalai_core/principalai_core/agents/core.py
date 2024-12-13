from pydantic import BaseModel
from typing import Optional

from principalai_core.tools.core import Tool
from principalai_core.data.entity import Entity
from principalai_core.utils.errors import AlreadyExistsError, DoesNotExistError

class Agent(BaseModel):
    """Base class for agents"""
    __customClasses = {}

    @classmethod
    def register_custom_class(cls, customClassName: str, customClass):
        """Register a custom class"""
        if customClassName in cls.__customClasses:
            return AlreadyExistsError(f"{customClassName} is already a registered custom {cls.__name__}. Please pick a different name or un-register the existing custom class.")
        if not issubclass(cls, customClass):
            raise TypeError(f"Custom class must inherit from {cls.__name__}")

    @classmethod
    def list_custom_classes(cls):
        """Return a list of all custom class names"""
        return cls.__customClasses.keys()

    def __init__(self, name_:str, description_: str, inputParameters_: list[Entity], outputParameters_: list[Entity], tools_:list[Tool]=None):
        """Initialize instance of agent"""
        self.name: str = name_
        self.description: str = description_
        self.inputParameters: list[Entity] = inputParameters_
        self.outputParameters: list[Entity] = outputParameters_
        self.tools: Optional[dict[str, Tool]] = tools_
    
    def get_tools(self):
        """Return a list of all tools avaialable to the agent"""
        return self.tools
    
    def add_tool(self, tool_: Tool):
        """Add a tool to the agent"""
        if tool_.name in self.tools:
            raise AlreadyExistsError(f"{tool_.name} is already a tool in this agent. Please check if this tool was added in previously or change the name of the tool.")
        self.tools[tool_.name] = tool_

    def remove_tool(self, toolName_: str):
        """Remove a tool from the agent"""
        if toolName_ not in self.tools:
            raise DoesNotExistError(f"{toolName_} does not exist as a tool in this agent. Please check the tool name again.")