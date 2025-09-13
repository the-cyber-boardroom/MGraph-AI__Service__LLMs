from unittest                                                                                       import TestCase
from osbot_utils.testing.__                                                                         import __
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.utils.Objects                                                                      import base_classes
from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Parameter        import Schema__LLM__Tool__Parameter

class test_Schema__LLM__Tool__Parameter(TestCase):

    def test__init__(self):                                                                         # Test auto-initialization of parameter schema
        with Schema__LLM__Tool__Parameter() as _:
            assert type(_)         is Schema__LLM__Tool__Parameter
            assert base_classes(_) == [Type_Safe, object]

            # Test all fields are initialized with correct types
            assert _.name        == ''                                                              # Safe_Str empty default
            assert _.type        == ''                                                              # Safe_Str empty default
            assert _.description is None                                                            # Optional field
            assert _.required    is True                                                            # Explicit default
            assert _.enum        is None                                                            # Optional field
            assert _.default     is None                                                            # Optional field
            assert _.properties  is None                                                            # For nested objects
            assert _.items       is None                                                            # For arrays

            # Comprehensive state verification
            assert _.obj() == __(name        = ''    ,
                                 type        = ''    ,
                                 description = None  ,
                                 required    = True  ,
                                 enum        = None  ,
                                 default     = None  ,
                                 properties  = None  ,
                                 items       = None  )

    def test__init__with_values(self):                                                              # Test initialization with explicit values
        with Schema__LLM__Tool__Parameter() as _:
            _.name        = "location"
            _.type        = "string"
            _.description = "City or address for weather lookup"
            _.required    = True
            _.enum        = ["celsius", "fahrenheit"]

            assert _.obj() == __(name        = "location"                          ,
                                 type        = "string"                            ,
                                 description = "City or address for weather lookup",
                                 required    = True                                ,
                                 enum        = ["celsius", "fahrenheit"]           ,
                                 default     = None                                ,
                                 properties  = None                                ,
                                 items       = None                                )

    def test_json_serialization(self):                                                              # Test JSON round-trip preserves all data
        with Schema__LLM__Tool__Parameter() as original:
            original.name        = "temperature_unit"
            original.type        = "string"
            original.description = "Temperature unit preference"
            original.required    = False
            original.default     = "celsius"
            original.enum        = ["celsius", "fahrenheit", "kelvin"]

            # Serialize to JSON
            json_data = original.json()

            # Deserialize back
            with Schema__LLM__Tool__Parameter.from_json(json_data) as restored:
                assert restored.obj() == original.obj()                                            # Perfect round-trip

                # Verify types preserved
                assert type(restored.name)        is type(original.name)
                assert type(restored.type)        is type(original.type)
                assert restored.enum              == ["celsius", "fahrenheit", "kelvin"]

    def test_nested_object_parameter(self):                                                         # Test parameter for nested object types
        with Schema__LLM__Tool__Parameter() as _:
            _.name = "address"
            _.type = "object"
            _.properties = { "street" : { "type": "string" },
                            "city"   : { "type": "string" },
                            "zip"    : { "type": "string" } }

            assert _.properties["street"]["type"] == "string"
            assert len(_.properties) == 3

    def test_array_parameter(self):                                                                 # Test parameter for array types
        with Schema__LLM__Tool__Parameter() as _:
            _.name = "tags"
            _.type = "array"
            _.items = {"type": "string"}

            assert _.items["type"] == "string"