from typing import Dict
from unittest                                                                                           import TestCase
from osbot_fast_api.api.transformers.Type_Safe__To__Json                                                import Type_Safe__To__Json
from osbot_utils.testing.__                                                                             import __
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.utils.Objects                                                                          import base_classes
from mgraph_ai_service_llms.platforms.open_router.schemas.json_output.Schema__Json_Extract__Request     import Schema__Json_Extract__Request
from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Message_Content             import Safe_Str__Message_Content
from mgraph_ai_service_llms.service.llms.prompts.schemas.Schema__Facts                                  import Schema__Facts
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers           import Schema__Open_Router__Providers

class test_Schema__Json_Extract_Request(TestCase):                                                           # Test request schema

    def test__init__(self):                                                                                  # Test request initialization
        transformer = Type_Safe__To__Json()
        schema = transformer.convert_class(Schema__Facts)

        with Schema__Json_Extract__Request() as _:
            _.text_content  = Safe_Str__Message_Content("Extract from this")
            _.output_schema = schema

            assert type(_)                  is Schema__Json_Extract__Request
            assert base_classes(_)          == [Type_Safe, object]
            assert type(_.text_content)     is Safe_Str__Message_Content
            assert type(_.output_schema)    is dict
            assert _.model                  is None
            assert _.provider               is None
            assert _.temperature            == 0.0                                                           # Default
            assert _.max_tokens             == 5000                                                          # Default

    def test_with_custom_values(self):                                                                       # Test with custom values
        request = Schema__Json_Extract__Request(
            text_content  = Safe_Str__Message_Content("Custom text"),
            output_schema = {"type": "object"}                      ,
            model         = "openai/gpt-4o"                         ,
            provider      = Schema__Open_Router__Providers.OPENAI   ,
            temperature   = 0.7                                     ,
            max_tokens    = 2000                                    )

        assert request.obj() == __(text_content  = "Custom text"     ,
                                   output_schema = __(type='object') ,
                                   model         = "openai/gpt-4o"   ,
                                   provider      = 'openai'          ,
                                   temperature   = 0.7               ,
                                   max_tokens    = 2000              )
