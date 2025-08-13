from enum import Enum

class Schema__Open_Router__Providers(Enum): # Specific OpenRouter providers for routing
    AUTO      = "auto"           # Let OpenRouter decide
    CEREBRAS  = "cerebras"       # Force Cerebras provider
    GROQ      = "groq"           # Force Groq provider
    TOGETHER  = "together"       # Together AI
    DEEPINFRA = "deepinfra"      # DeepInfra


    def header_value(self) -> str:  # Format for X-Provider header
        if self.value == "auto":
            return None
        return self.value