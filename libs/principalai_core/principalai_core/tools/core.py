from pydantic import BaseModel, ValidationError
from typing import Optional, Callable
from warnings import warn
import requests

from principalai_core.invocable import Invocable, FunctionInvocable
from principalai_core.data import Entity
from principalai_core.utils.errors import (
    IncorrectDefinitonError,
    HttpRequestError
)
from principalai_core.utils.parsers import defaultApiToolInputParser
from principalai_core.utils.http import HttpRequestType

class Tool(Invocable):
    """Base class for Tool - Tools allow LLMs to perform actions outside of generation."""
    def __init__(
        self,
        name: str, 
        description: Optional[str] = None, 
        inputParameterSchema: Optional[BaseModel] = None, 
        outputParameterSchema: Optional[BaseModel] = None
    ):
        super().__init__(inputParameterSchema, outputParameterSchema)
        self.attributes: Entity = Entity(name, description)

class FunctionTool(Tool, FunctionInvocable):
    """
    Tools that are implemented as functions.

    FunctionTool can be implemented using @Decorators

    @FunctionTool("Hello World Tool")
    def function_tool_function():
        "Tool that returns Hellow World"
        return "Hello World"
    """
    def __init__(
        self,
        name: str, 
        description: Optional[str] = None, 
        inputParameterSchema: Optional[BaseModel] = None,
        outputParameterSchema: Optional[BaseModel] = None, 
        func: Optional[Callable] = None
    ):
        super().__init__(name, description, inputParameterSchema, outputParameterSchema)
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
                raise IncorrectDefinitonError('''Function is missing Docstring. Please add a docstring to the function or 
                                              initialize the Invocable without a decorator.''')
            self.attributes.description = funcDocstring
        else:
            #Not really required but good to let the user know
            if func.__doc__ is not None:
                warn('''Invocable description provided as parameter and in function docstring. The parameter takes 
                     precedence over the function docstring. In case both are same, you can safely remove the description 
                     parameter.''')
        return self

class ApiTool(FunctionTool):
    """
    Tools that are implemented as API Endpoints. When these tools are invoked, the API endpoint is called.

    ***
    Requires Input and Output Parameter Schema. This is required to construct API call and Validate API response.
    ***

    ApiTool specific variables can be passed through the function body using @Decorators.

    @ApiTool("somendpoint_API")
    def api_tool_function():
        "Tool to call someendpoint to get back some data"
        return {
            "apiEndpoint": "https://host.com:port/someendpoint"
        }
    """
    def __init__(
        self,
        name: str,
        inputParameterSchema: BaseModel,
        outputParameterSchema: BaseModel,
        description: Optional[str] = None,
        apiEndpoint: Optional[str] = None,
        httpRequestType: Optional[HttpRequestType] = HttpRequestType.GET.name.lower(),
        httpParameters: dict = {}, #Dictionary to provide HTTP request parameters except for inputs
        inputParameterParser: Optional[Callable] = None, #Custom parser. Can be used to put data into Url Paramter, Body, etc.
    ):
        super().__init__(name, description, inputParameterSchema, outputParameterSchema)
        self.func = None
        self.apiEndpoint = apiEndpoint
        self.httpRequestType = httpRequestType
        self.httpParameters = httpParameters
        if inputParameterParser is None:
            self.inputParameterParser = defaultApiToolInputParser
        else:
            self.inputParameterParser = inputParameterParser

    def run(
        self,
        *args,
        **kwargs
    ):
        #Run the function to get required variables
        functionVariables = self.func()   
        if self.apiEndpoint is None:
            if "apiEndpoint" in functionVariables:
                self.apiEndpoint = functionVariables["apiEndpoint"]
            else:
                raise IncorrectDefinitonError(f'''apiEndpoint is not provided in either the function or passed in during 
                                              instantiation. Please check the variable name and if it is passed in
                                              correctly.''')
        else:
            #Already populated warning
            pass
        if "httpRequestType" in functionVariables:
            if self.httpRequestType is not None:
                ##lready populated warning
                pass
            self.httpRequestType = functionVariables["httpRequestType"]
        if "httpParameters" in functionVariables:
            if self.httpRequestType is not None:
                #Already populated warning
                pass
            self.httpParameters = functionVariables["httpParameters"]

        try:
            requestMethod = getattr(requests, self.httpRequestType)
            if not callable(requestMethod):
                raise HttpRequestError(f'Invalid HTTP request method: {self.httpRequestType}')
            inputParametersParsed = self.inputParameterParser(self.inputParameterSchema[0], *args, **kwargs)
            response = requestMethod(self.apiEndpoint, **inputParametersParsed, **self.httpParameters)
            if self.outputParameterSchema is None:
                return response.json()
            else:
                try:
                    validatedOutput = self.outputParameterSchema[0](response.json())
                except ValidationError as e:
                    raise ValidationError(f'''Tool {self.name} could not validate the API response. Please check the output
                                          parameter schema passed in and the API response.: {e}''')
                return validatedOutput
        except requests.RequestException as e:
            raise HttpRequestError(f'Http request failed: {e}')