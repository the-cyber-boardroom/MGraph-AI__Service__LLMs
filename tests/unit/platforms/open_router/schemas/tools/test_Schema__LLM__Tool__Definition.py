from unittest                                                                                       import TestCase
from osbot_utils.testing.__                                                                         import __
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.utils.Objects                                                                      import base_classes
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Definition       import Schema__LLM__Tool__Definition

class test_Schema__LLM__Tool__Definition(TestCase):

    @classmethod
    def setUpClass(cls):                                                                            # Setup expensive resources once
        cls.sample_tool_definition = Schema__LLM__Tool__Definition(
            name        = "get_weather"                                                                             ,
            description = "Get current weather for a location"                                                      ,
            parameters  = { "type"       : "object"                                                                 ,
                            "properties" : { "location"    : { "type"        : "string"                             ,
                                                               "description" : "City or address"                    },
                                            "unit"       : { "type"        : "string"                               ,
                                                            "description" : "Temperature unit"                      ,
                                                            "enum"       : ["celsius", "fahrenheit"]                ,
                                                            "default"    : "celsius"                                }},
                            "required"   : ["location"]                                                             })

    def test__init__(self):                                                                         # Test auto-initialization of tool definition
        with Schema__LLM__Tool__Definition() as _:
            assert type(_)         is Schema__LLM__Tool__Definition
            assert base_classes(_) == [Type_Safe, object]

            # Test field types
            assert _.name        == ''                                                              # Safe_Str empty default
            assert _.description == ''                                                              # Safe_Str empty default
            assert _.parameters  == {}                                                              # Empty dict default

            assert _.obj() == __(name        = ''  ,
                                 description = ''  ,
                                 parameters  = __())

    def test__init__with_full_schema(self):                                                         # Test with complete tool schema
        with self.sample_tool_definition as _:
            assert _.name        == "get_weather"
            assert _.description == "Get current weather for a location"
            assert _.parameters["type"] == "object"
            assert _.parameters["properties"]["location"]["type"] == "string"
            assert _.parameters["required"] == ["location"]

            # Verify nested structure
            assert _.parameters["properties"]["unit"]["enum"] == ["celsius", "fahrenheit"]
            assert _.parameters["properties"]["unit"]["default"] == "celsius"
            assert _.obj() == __(name        = 'get_weather',
                                 description = 'Get current weather for a location',
                                 parameters  = __(type       = 'object',
                                                  properties = __(location = __(type        = 'string',
                                                                                description = 'City or address'),
                                                                                unit        = __(type        ='string'                  ,
                                                                                                 description ='Temperature unit'        ,
                                                                                                 enum        = ['celsius', 'fahrenheit'],
                                                                                                 default     = 'celsius')),
                                                   required  = ['location']))

    def test_to_openai_format(self):                                                                # Test conversion to OpenAI function format
        with self.sample_tool_definition as _:
            openai_format = _.to_openai_format()

            assert openai_format == { "name"        : "get_weather"                               ,
                                      "description" : "Get current weather for a location"        ,
                                      "parameters"  : _.parameters                                }

            # Verify it's the right structure for OpenAI
            assert "type"       in openai_format["parameters"]
            assert "properties" in openai_format["parameters"]
            assert "required"   in openai_format["parameters"]

    def test_to_anthropic_format(self):                                                             # Test conversion to Anthropic tool format
        with self.sample_tool_definition as _:
            anthropic_format = _.to_anthropic_format()

            assert anthropic_format == { "name"         : "get_weather"                           ,
                                         "description"  : "Get current weather for a location"    ,
                                         "input_schema" : _.parameters                            }

            # Note the different key name: input_schema vs parameters
            assert "input_schema" in anthropic_format
            assert anthropic_format["input_schema"] == _.parameters

    def test_json_serialization(self):                                                              # Test JSON round-trip with complex schema
        with self.sample_tool_definition as original:
            # Serialize to JSON
            json_data = original.json()

            # Verify JSON structure
            assert json_data["name"] == "get_weather"
            assert "properties" in json_data["parameters"]

            # Deserialize back
            with Schema__LLM__Tool__Definition.from_json(json_data) as restored:
                assert restored.obj() == original.obj()                                            # Perfect round-trip

                # Test nested structures preserved
                assert restored.parameters["properties"]["unit"]["enum"] == ["celsius", "fahrenheit"]
                assert restored.to_openai_format() == original.to_openai_format()

    def test_complex_nested_schema(self):                                                           # Test with deeply nested object schema
        with Schema__LLM__Tool__Definition() as _:
            _.name = "create_order"
            _.description = "Create a new order with items"
            _.parameters = { "type"       : "object"                                                             ,
                             "properties" : { "customer" : { "type"       : "object"                                             ,
                                                             "properties" : { "name"  : { "type": "string" }                     ,
                                                                              "email" : { "type": "string", "format": "email" }   },
                                                             "required"   : ["name", "email"]                                    },
                                             "items"    : { "type"  : "array"                                                    ,
                                                         "items" : { "type"       : "object"                                   ,
                                                                    "properties" : { "product_id" : { "type": "string" }       ,
                                                                                    "quantity"   : { "type": "integer", "minimum": 1 } }}}},
                             "required"   : ["customer", "items"]                                                       }

            # Verify complex nested structure
            assert _.parameters["properties"]["customer"]["type"] == "object"
            assert _.parameters["properties"]["customer"]["properties"]["email"]["format"] == "email"
            assert _.parameters["properties"]["items"]["items"]["properties"]["quantity"]["minimum"] == 1

    def test_minimal_tool_definition(self):                                                         # Test with minimal required fields
        with Schema__LLM__Tool__Definition() as _:
            _.name = "echo"
            _.description = "Echo back input"
            _.parameters = { "type"       : "object"                  ,
                            "properties" : {}                         ,
                            "required"   : []                         }

            # Should work with empty properties
            openai_format = _.to_openai_format()
            assert openai_format["parameters"]["properties"] == {}
            assert openai_format["parameters"]["required"] == []