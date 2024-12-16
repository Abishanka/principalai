from pydantic import BaseModel

from principalai_core.agents.core import Agent
from principalai_core.utils.errors import AlreadyExistsError

class AgentRegistry(BaseModel):
    """Registry for managing agents"""
    def __init__(self):
        self.__agents: dict[str, Agent]

    def register_agent(
        self, 
        agent: Agent
    ):
        """Add an agent to the registry"""
        if agent.attributes.name in self.__agents:
            raise AlreadyExistsError(f'''{agent.name} already exists in this registry instance. Please change the agent name or remove 
                                     the agent with the same name.''')
        self.__agents[agent.attributes.name] = agent

    def get_registered_agents(self):
        """Get a list of agents registered"""
        return self.__agents.keys()