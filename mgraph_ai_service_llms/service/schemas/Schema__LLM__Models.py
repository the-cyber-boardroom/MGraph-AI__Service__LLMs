from enum import Enum


class Schema__LLM__Models(Enum):
    """Supported LLM models with their identifiers and metadata"""

    # Free models
    MISTRAL_SMALL_FREE = "mistralai/mistral-small-3.2-24b-instruct:free"
    MOONSHOT_KIMI_FREE = "moonshotai/kimi-k2:free"
    QWEN_235B_FREE     = "qwen/qwen3-235b-a22b-07-25:free"
    DEEPSEEK_FREE      = "tngtech/deepseek-r1t2-chimera:free"

    # Paid models
    GEMINI_2_FLASH     = "google/gemini-2.0-flash-lite-001"
    GPT_4O_MINI        = "openai/gpt-4o-mini"
    GPT_4_1_MINI       = "openai/gpt-4.1-mini"
    GPT_OSS_120B       = "openai/gpt-oss-120b"
    GPT_OSS_20B        = "openai/gpt-oss-20b"

    @property
    def is_free(self) -> bool:
        return "free" in self.value

    @property
    def provider(self) -> str:
        return self.value.split("/")[0]