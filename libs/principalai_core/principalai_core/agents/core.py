from pydantic import BaseModel
from typing import Optional, Callable
from warnings import warn

from principalai_core.invocable import Invocable, FunctionInvocable
from principalai_core.data import Entity
from principalai_core.tools import Tool
from principalai_core.language_models import LanguageModel
from principalai_core.utils.errors import (
    AlreadyExistsError, 
    DoesNotExistError,
    IncorrectDefinitonError
)

class Agent(Invocable):
    """Base class for Agents - Agents are autonomous functions which utilize an LLM to achieve their objective."""
    def __init__(
        self,
        name:str,
        description: Optional[str] = None,
        inputParameterSchema: Optional[BaseModel] = None,
        outputParameterSchema: Optional[BaseModel] = None,
        languageModel: LanguageModel = None,
        languageModelRunEngine: Callable = None,
        tools: Optional[list[Tool]] = None
    ):
        super().__init__(inputParameterSchema, outputParameterSchema, languageModel, languageModelRunEngine)
        self.attributes: Entity = Entity(name, description, "agent")
        self.tools: Optional[dict[str, Tool]] = tools

    def get_tools(self):
        """Return a list of all tools avaialable to the agent"""
        return self.tools
    
    def add_tool(
        self,
        tool_: Tool
    ):
        """Add a tool to the agent"""
        if tool_.attributes.name in self.tools:
            raise AlreadyExistsError(
                f'{tool_.attributes.name} is already a tool in this agent. Please check if this tool was added in previously '
                'or change the name of the tool.'
                )
        self.tools[tool_.attributes.name] = tool_

    def remove_tool(
        self, 
        toolname: str
    ):
        """Remove a tool from the agent"""
        if toolname not in self.tools:
            raise DoesNotExistError(f'{toolname} does not exist as a tool in this agent. Please check the tool name again.')
        del self.tools[toolname]

class FunctionAgent(Agent, FunctionInvocable):
    """Agents that are implemented as functions"""
    def __init__(
        self,
        name:str,
        description: Optional[str] = None,
        inputParameterSchema: Optional[BaseModel] = None,
        outputParameterSchema: Optional[BaseModel] = None,
        languageModel: LanguageModel = None,
        languageModelRunEngine: Callable = None,
        tools: Optional[list[Tool]] = None,
        func: Optional[Callable] = None
    ):
        super().__init__(name, description, inputParameterSchema, outputParameterSchema, tools, languageModel, languageModelRunEngine)
        self.func = func
    
    def __call__(
        self,
        func: Callable
    ):
        """Function decorator"""
        self.func = func
        if self.attributes.description is None:
            funcDocstring = func.__doc__
            if funcDocstring is None:
                raise IncorrectDefinitonError('Function is missing Docstring. Please add a docstring to the function or initialize '
                                              'the Invocable without a decorator.')
            self.attributes.description = funcDocstring
        else:
            #Not really required but good to let the user know
            if func.__doc__ is not None:
                warn('Invocable description provided as parameter and in function docstring. The parameter takes precedence over '
                     'the function docstring. In case both are same, you can safely remove the description parameter.')
        return self