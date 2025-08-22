from osbot_utils.helpers.llms.actions.LLM_Request__Execute                            import LLM_Request__Execute
from osbot_utils.helpers.llms.builders.LLM_Request__Builder__Open_AI                  import LLM_Request__Builder__Open_AI
from osbot_utils.helpers.llms.cache.LLM_Request__Cache__File_System                   import LLM_Request__Cache__File_System
from osbot_utils.helpers.llms.schemas.Safe_Str__LLM__Model_Name                       import Safe_Str__LLM__Model_Name
from osbot_utils.type_safe.Type_Safe                                                  import Type_Safe
from osbot_utils.utils.Env                                                            import load_dotenv
from mgraph_ai_service_llms.service.cache.LLM__Cache                                  import LLM__Cache
from mgraph_ai_service_llms.service.llms.prompts.LLM__Prompt__Extract_Facts           import LLM__Prompt__Extract_Facts
from mgraph_ai_service_llms.service.llms.providers.open_router.API__LLM__Open_Router  import API__LLM__Open_Router
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers import \
    Schema__Open_Router__Providers


class LLM__Execute_Request(Type_Safe):
    virtual_storage: LLM__Cache = None

    def __init__(self):
        load_dotenv()
        super().__init__()      # refact all this into and .setup() method

    def setup(self):
        self.virtual_storage   = LLM__Cache().setup()
        self.llm_cache         = LLM_Request__Cache__File_System(virtual_storage = self.virtual_storage  ).setup()
        self.llm_api           = API__LLM__Open_Router()
        self.request_builder   = LLM_Request__Builder__Open_AI()
        self.llm_execute       = LLM_Request__Execute(llm_cache       = self.llm_cache      ,
                                                      llm_api         = self.llm_api        ,
                                                      request_builder = self.request_builder)
        return self

    def extract_facts(self, text_content,
                            model_to_use: Safe_Str__LLM__Model_Name,
                            provider    : Schema__Open_Router__Providers  = None):
        model_to_use          = Safe_Str__LLM__Model_Name(model_to_use)
        prompt_extract_facts =  LLM__Prompt__Extract_Facts()
        llm_request           = prompt_extract_facts.llm_request(text_content=text_content, model_to_use=model_to_use)
        llm_response          = self.llm_execute.execute(llm_request)
        llm_request__cache_id = self.llm_execute.llm_cache.get__cache_id__from__request(llm_request)
        facts                 = prompt_extract_facts.process_llm_response(llm_response)
        return dict(cache_id  = llm_request__cache_id,
                    model     = model_to_use   ,
                    data      = facts       .json())

    def extract_facts__request_hash(self, text_content,model_to_use: Safe_Str__LLM__Model_Name):
        prompt_extract_facts = LLM__Prompt__Extract_Facts()
        llm_request  = prompt_extract_facts.llm_request(text_content=text_content, model_to_use=model_to_use)
        request_hash = self.llm_cache.compute_request_hash(llm_request)
        return request_hash
