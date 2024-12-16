from pydantic import BaseModel
from typing import Optional, Callable

from principalai_core.invocable.core import Invocable, FunctionInvocable
from principalai_core.data.models.core import Entity
from principalai_core.tools.core import Tool
from principalai_core.utils.errors import (
    AlreadyExistsError, 
    DoesNotExistError
)

class Agent(Invocable):
    """Base class for Agents - Agents are autonomous functions which utilize an LLM to achieve their objective."""
    def __init__(
        self,
        name_:str,
        description_: Optional[str] = None,
        inputParameterSchema_: Optional[BaseModel] = None,
        outputParameterSchema_: Optional[BaseModel] = None,  #The agent has to have some sort of output. It might only be a string
        tools_: Optional[list[Tool]] = None
    ):
        super().__init__(inputParameterSchema_, outputParameterSchema_)
        self.attributes: Entity = Entity(name_, description_)
        self.tools: Optional[dict[str, Tool]] = tools_

    def get_tools(self):
        """Return a list of all tools avaialable to the agent"""
        return self.tools
    
    def add_tool(
        self,
        tool_: Tool
    ):
        """Add a tool to the agent"""
        if tool_.attributes.name in self.tools:
            raise AlreadyExistsError(f'''{tool_.attributes.name} is already a tool in this agent. Please check if this tool was added in 
                                     previously or change the name of the tool.''')
        self.tools[tool_.attributes.name] = tool_

    def remove_tool(
        self, 
        toolName_: str
    ):
        """Remove a tool from the agent"""
        if toolName_ not in self.tools:
            raise DoesNotExistError(f'{toolName_} does not exist as a tool in this agent. Please check the tool name again.')
        del self.tools[toolName_]

class FunctionAgent(Agent, FunctionInvocable):
    """Agents that are implemented as functions"""
    def __init__(
        self,
        name_:str,
        description_: Optional[str] = None,
        inputParameterSchema_: Optional[BaseModel] = None,
        outputParameterSchema_: Optional[BaseModel] = None,  #The agent has to have some sort of output. It might only be a string
        tools_: Optional[list[Tool]] = None,
        func_: Optional[Callable] = None
    ):
        super().__init__(name_, description_, inputParameterSchema_, outputParameterSchema_, tools_)
        self.func = func_