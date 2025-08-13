import pytest
from unittest                                                                       import TestCase
from osbot_utils.helpers.llms.schemas.Schema__LLM_Request__Message__Role            import Schema__LLM_Request__Message__Role
from osbot_utils.utils.Env                                                          import get_env
from osbot_utils.utils.Misc                                                         import list_set
from mgraph_ai_service_llms.config                                                  import TEST_DATA__SIMPLE_TEXT
from mgraph_ai_service_llms.service.llms.LLM__Execute_Request                       import LLM__Execute_Request
from mgraph_ai_service_llms.service.llms.prompts.LLM__Prompt__Extract_Facts         import LLM__Prompt__Extract_Facts, SYSTEM_PROMPT__EXTRACT_FACTS
from mgraph_ai_service_llms.service.llms.prompts.schemas.Schema__Facts              import Schema__Facts
from mgraph_ai_service_llms.service.llms.providers.open_router.Provider__OpenRouter import ENV_NAME_OPEN_ROUTER__API_KEY
from tests.unit.Service__Fast_API__Test_Objs                                        import setup__service_fast_api_test_objs


class test_Execute_Request(TestCase):

    @classmethod
    def setUpClass(cls):
        setup__service_fast_api_test_objs()

        if get_env(ENV_NAME_OPEN_ROUTER__API_KEY) is None:
            pytest.skip('This test requires OpenAI API Key to run')
        cls.prompt_extract_facts  = LLM__Prompt__Extract_Facts()
        cls.llm_execute_request   = LLM__Execute_Request().setup()


    def test_llm_request(self):
        with self.prompt_extract_facts as _:
            text_content = TEST_DATA__SIMPLE_TEXT
            llm_request = self.prompt_extract_facts.llm_request(text_content=text_content, model_to_use='')
            assert llm_request.request_data.function_call.parameters == Schema__Facts
            with llm_request.request_data.messages[0] as _:
                assert _.role    == Schema__LLM_Request__Message__Role.SYSTEM
                assert _.content == SYSTEM_PROMPT__EXTRACT_FACTS
            with llm_request.request_data.messages[1] as _:
                assert _.role == Schema__LLM_Request__Message__Role.USER
                assert text_content in _.content



    def test_extract_facts(self):
        #self.llm_execute_with_local_cache.llm_execute.refresh_cache = True
        text_content = TEST_DATA__SIMPLE_TEXT
        with self.llm_execute_request as _:
            #llm_request = self.prompt_extract_facts.llm_request(text_content=text_content, model_to_use='')
            result = _.extract_facts(text_content=text_content)
            assert list_set(result) == ['cache_id', 'data', 'model']