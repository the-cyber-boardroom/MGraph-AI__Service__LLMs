import requests
from unittest                                                                                   import TestCase
from osbot_utils.testing.__                                                                     import __
from osbot_utils.type_safe.primitives.core.Safe_UInt                                            import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text__Dangerous         import Safe_Str__Text__Dangerous
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Display_Name       import Safe_Str__Display_Name
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Topic              import Safe_Str__Topic
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Money            import Safe_Float__Money
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Percentage_Exact import Safe_Float__Percentage_Exact
from osbot_utils.utils.Env                                                                      import get_env, load_dotenv
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_fast_api.api.transformers.Type_Safe__To__Json                                        import Type_Safe__To__Json
from osbot_fast_api.schemas.consts__Fast_API                                                    import ENV_VAR__FAST_API__AUTH__API_KEY__NAME
from osbot_fast_api.schemas.consts__Fast_API                                                    import ENV_VAR__FAST_API__AUTH__API_KEY__VALUE

class test_qa__from_doc__LLM_Service__JSON_Extraction_API_Guide(TestCase):
    def test__http__llm_json__extract(self):


        load_dotenv()

        headers = { get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME): get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE) }

        # 1. Define your data structure as a Type_Safe class
        class Schema__Company_Info(Type_Safe):
            company_name      : Safe_Str__Display_Name
            revenue           : Safe_Float__Money
            revenue_str       : Safe_Str__Text__Dangerous       # we should be using a type like Safe_Str__Money or Safe_Str__Dollars
            growth_percentage : Safe_Float__Percentage_Exact
            fiscal_period     : Safe_Str__Topic
            year              : Safe_UInt
            quarter           : Safe_UInt

        # 2. Convert Type_Safe to JSON Schema (transparent operation)
        transformer  = Type_Safe__To__Json()
        output_schema = transformer.convert_class(Schema__Company_Info)
        text_content  = "TechCorp reported Q3 2024 revenue of $5.2 million, a 30% increase year-over-year."

        # 3. Make the extraction request
        response = requests.post(url   = "https://llms.dev.mgraph.ai/platform/open-router/llm-json/extract",
                                json   = { "text_content" : text_content        ,
                                           "output_schema": output_schema       ,
                                           "model"        : "openai/gpt-oss-20b",
                                           "provider"     : "groq"              },
                                headers = headers        )
        assert response.status_code == 200

        # 4. Convert response back to Type_Safe instance (type-safe operation)
        result       = response.json()
        company_info = Schema__Company_Info.from_json(result["json_data"])

        # Now you have a fully typed object :)
        assert company_info.json() == { 'company_name'     : 'TechCorp'       ,
                                        'fiscal_period'    : 'Q3 2024'        ,
                                        'growth_percentage': 30.0             ,
                                        'quarter'          : 3                ,
                                        'revenue'          : 5200000.0        ,
                                        'revenue_str'      : '$5.2 million'   ,
                                        'year'             : 2024             }
        assert company_info.obj() == __(company_name      = 'TechCorp'      ,
                                        revenue           = 5200000.0       ,
                                        revenue_str       = '$5.2 million'  ,
                                        growth_percentage = 30.0            ,
                                        fiscal_period     = 'Q3 2024'       ,
                                        year              = 2024            ,
                                        quarter          = 3                )