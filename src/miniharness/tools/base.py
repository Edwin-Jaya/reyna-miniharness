from abc import ABC, abstractmethod


class Tool(ABC):
    name: str
    description: str
    parameters: dict[str, any]
    
    @abstractmethod
    def run(self, **kwargs) -> str:
        pass
    
    def schema(self) -> dict:
        return {
            "name":self.name,
            "description":self.description,
            "input_schema":self.parameters,
        }