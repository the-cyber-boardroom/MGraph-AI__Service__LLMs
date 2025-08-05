from typing                             import Dict, Any
from urllib.error                       import HTTPError
from osbot_utils.type_safe.Type_Safe    import Type_Safe
from osbot_utils.utils.Http             import POST_json
from osbot_utils.utils.Env              import get_env
from osbot_utils.utils.Json             import str_to_json

ENV_NAME_OPEN_ROUTER__API_KEY = "OPEN_ROUTER__API_KEY"

class Provider__OpenRouter(Type_Safe):
    api_url     : str = "https://openrouter.ai/api/v1/chat/completions"
    api_key_name: str = ENV_NAME_OPEN_ROUTER__API_KEY
    http_referer: str = "the-cyber-boardroom/MGraph-AI__Service__LLMs"

    def api_key(self) -> str:
        return get_env(self.api_key_name)

    def execute(self, llm_payload: Dict[str, Any]) -> Dict[str, Any]:   # Execute request against OpenRouter API
        headers = { "Authorization" : f"Bearer {self.api_key()}",
                    "Content-Type"  : "application/json"        ,
                    "HTTP-Referer"  : self.http_referer         ,
                    "X-Title"       : "MGraph-AI LLM Service"   }

        try:
            response = POST_json(self.api_url, headers=headers, data=llm_payload)
            return response
        except HTTPError as error:
            error_message = str_to_json(error.file.read().decode("utf-8"))
            raise ValueError(error_message)