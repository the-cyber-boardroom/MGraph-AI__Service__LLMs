from enum import Enum


class Schema__Open_Router__Supported_Models(Enum):
    Mistral_AI__Mistral_Small__Free: str = "mistralai/mistral-small-3.2-24b-instruct:free"  # Created Jun 20, 2025    96,000 context $0    /M input tokens  $0   /M output tokens   https://openrouter.ai/mistralai/mistral-small-3.2-24b-instruct:free
    Moonshot_AI__Kimi_K2__Free     : str = "moonshotai/kimi-k2:free"                        # Created Jul 11, 2025    65,536 context $0    /M input tokens  $0   /M output tokens
    Qwen__Qwen3__235b__Free        : str = "qwen/qwen3-235b-a22b-07-25:free"                # Created Jul 21, 2025   262,144 context $0    /M input tokens  $0   /M output tokens   https://openrouter.ai/qwen/qwen3-235b-a22b-07-25:free
    TngTech__DeepSeek              : str = "tngtech/deepseek-r1t2-chimera:free"             # Created Apr 27, 2025   163,840 context $0    /M input tokens  $0   /M output tokens   https://openrouter.ai/tngtech/deepseek-r1t-chimera:free
    Google__Gemini_2_0             : str = "google/gemini-2.0-flash-lite-001"               # Created Feb 25, 2025 1,048,576 context $0.075/M input tokens  $0.30/M output tokens
    Mistral_AI__Devstral_Small     : str = "mistralai/devstral-small"                       # Created Jul 10, 2025   128,000 context $0.07 /M input token   $0.28/M output tokens
    Open_AI__GPT_4o_Mini           : str = "openai/gpt-4o-mini"                             # Created Jul 18, 2024   128,000 context $0.15 /M input tokens  $0.60/M output tokens
    Open_AI__GPT_4_1_Mini          : str = "openai/gpt-4.1-mini"                            # Created Apr 14, 2025 1,047,576 context $0.40 /M input tokens  $1.60/M output tokens
    Open_AI__GPT_5__Nano           : str = "openai/gpt-5-nano"                              # Created Aug 7, 2025    400,000 context $0.05 /M input tokens  $0.40/M output tokens
    Open_AI__GPT_5__Mini           : str = "openai/gpt-5-mini"                              # Created Aug 7, 2025    400,000 contex  $0.25 /M input tokens  $2   /M output tokens


    Open_AI__GPT_OSS_120b          : str = "openai/gpt-oss-120b"                            # Created Aug  5, 2025   131,072 context $0.10 /M input tokens  $0.50/M output tokens   https://openrouter.ai/openai/gpt-oss-120b
    Open_AI__GPT_OSS_20b           : str = "openai/gpt-oss-20b"                             # Created Aug  5, 2025   131,072 context $0.05 /M input tokens  $0.20/M output tokens   https://openrouter.ai/openai/gpt-oss-20b