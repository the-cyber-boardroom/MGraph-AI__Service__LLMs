from enum import Enum

class Schema__Open_Router__Providers(Enum): # Specific OpenRouter providers for routing
    AUTO      = None
    CEREBRAS  = "cerebras"       # Force Cerebras provider
    GROQ      = "groq"           # Force Groq provider
    TOGETHER  = "together"       # Together AI
    DEEPINFRA = "deepinfra"      # DeepInfra
    OPENAI    = "openai"