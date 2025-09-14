# import json
# from typing                                                                                               import Dict, Any, Optional, List
# from osbot_utils.type_safe.Type_Safe                                                                      import Type_Safe
# from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Call                   import Schema__LLM__Tool__Call
# from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Response               import Schema__LLM__Tool__Response
# from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                            import Service__Open_Router
# from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Definition             import Schema__LLM__Tool__Definition
# from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Request                import Schema__LLM__Tool__Request
# from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Chat_Request       import Schema__Open_Router__Chat_Request
# from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Message            import Schema__Open_Router__Message
# from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Tool               import Schema__Open_Router__Tool
# from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Tool__Function     import Schema__Open_Router__Tool__Function
# from mgraph_ai_service_llms.platforms.open_router.schemas.request.Safe_Str__Message_Content               import Safe_Str__Message_Content
# from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_ID                 import Safe_Str__Open_Router__Model_ID
#
# class Service__LLM__Tools(Type_Safe):                                                                         # Service for handling LLM tool/function calling
#     open_router : Service__Open_Router = None
#
#     def __init__(self):
#         super().__init__()
#         self.open_router = Service__Open_Router()
#
#     def execute_with_tool(self, request: Schema__LLM__Tool__Request) -> Schema__LLM__Tool__Response: # Execute LLM completion with tool support
#
#         openrouter_tool = self._convert_to_openrouter_tool(request.tool_definition)                  # Convert tool definition to OpenRouter format
#
#         messages = []                                                                                # Build messages
#         if request.system_prompt:
#             messages.append(Schema__Open_Router__Message(role    = "system"                                    ,
#                                                          content = Safe_Str__Message_Content(request.system_prompt)))
#         messages.append(Schema__Open_Router__Message    (role    = "user"                                          ,
#                                                          content = Safe_Str__Message_Content(request.user_prompt)))
#
#         # Create OpenRouter request with tool
#         chat_request = Schema__Open_Router__Chat_Request(model       = Safe_Str__Open_Router__Model_ID(request.model.value),
#                                                          messages    = messages                                             ,
#                                                          temperature = request.temperature                                  ,
#                                                          max_tokens  = request.max_tokens                                   ,
#                                                          tools       = [openrouter_tool]                                    )
#
#         # Force tool use if requested
#         if request.force_tool_use:
#             chat_request.tool_choice = {"type": "function", "function": {"name": str(request.tool_definition.name)}}
#
#         # Add provider if specified
#         if request.provider:
#             from mgraph_ai_service_llms.platforms.open_router.schemas.request.Schema__Open_Router__Provider_Preferences import Schema__Open_Router__Provider_Preferences
#             chat_request.provider = Schema__Open_Router__Provider_Preferences(
#                 order           = [request.provider.value],
#                 allow_fallbacks = True
#             )
#
#         # Execute request
#         response = self.open_router.chat_completion(
#             prompt        = request.user_prompt                               ,
#             model         = request.model.value                               ,
#             system_prompt = request.system_prompt                             ,
#             temperature   = request.temperature                               ,
#             max_tokens    = request.max_tokens                                ,
#             provider      = request.provider.value if request.provider else None
#         )
#
#         # Parse response for tool calls
#         tool_calls_data = []
#         response_content = None
#         requires_action = False
#
#         if "choices" in response and len(response["choices"]) > 0:
#             message = response["choices"][0].get("message", {})
#
#             # Check for tool calls
#             if "tool_calls" in message:
#                 requires_action = True
#                 for tool_call in message["tool_calls"]:
#                     function_data = tool_call.get("function", {})
#                     tool_call_obj = Schema__LLM__Tool__Call(
#                         name      = function_data.get("name", "")                    ,
#                         arguments = json.loads(function_data.get("arguments", "{}")) ,
#                         id        = tool_call.get("id")
#                     )
#                     tool_calls_data.append(tool_call_obj)
#
#             # Get any text content
#             if "content" in message:
#                 response_content = message["content"]
#
#         # Build response
#         return Schema__LLM__Tool__Response(
#             tool_calls       = tool_calls_data                               ,
#             response_content = response_content                              ,
#             requires_action  = requires_action                               ,
#             cache_id         = response.get("cache_id")                      ,
#             model_used       = request.model.value                           ,
#             provider_used    = response.get("provider")
#         )
#
#     def _convert_to_openrouter_tool(self, tool_definition: Schema__LLM__Tool__Definition                      # Convert our schema to OpenRouter format
#                                     ) -> Schema__Open_Router__Tool:
#
#         # Build OpenRouter tool function
#         function = Schema__Open_Router__Tool__Function(
#             name        = tool_definition.name                               ,
#             description = tool_definition.description                        ,
#             parameters  = tool_definition.parameters                          # Already in JSON Schema format
#         )
#
#         # Return as OpenRouter tool
#         return Schema__Open_Router__Tool(
#             type     = "function",
#             function = function
#         )
#
#     def validate_tool_arguments(self, tool_call     : Schema__LLM__Tool__Call        ,                        # Validate tool arguments against schema
#                                       tool_definition : Schema__LLM__Tool__Definition
#                                 ) -> Dict[str, Any]:
#
#         # Extract required fields from parameters
#         required_fields = tool_definition.parameters.get("required", [])
#         properties = tool_definition.parameters.get("properties", {})
#
#         validation_result = { "valid"  : True ,
#                              "errors" : []    ,
#                              "data"   : {}    }
#
#         # Check required fields
#         for field in required_fields:
#             if field not in tool_call.arguments:
#                 validation_result["valid"] = False
#                 validation_result["errors"].append(f"Missing required field: {field}")
#
#         # Validate types (basic validation)
#         for field_name, field_value in tool_call.arguments.items():
#             if field_name in properties:
#                 expected_type = properties[field_name].get("type")
#
#                 # Basic type checking
#                 if expected_type == "string" and not isinstance(field_value, str):
#                     validation_result["valid"] = False
#                     validation_result["errors"].append(f"Field {field_name} should be string")
#                 elif expected_type == "number" and not isinstance(field_value, (int, float)):
#                     validation_result["valid"] = False
#                     validation_result["errors"].append(f"Field {field_name} should be number")
#                 elif expected_type == "boolean" and not isinstance(field_value, bool):
#                     validation_result["valid"] = False
#                     validation_result["errors"].append(f"Field {field_name} should be boolean")
#                 elif expected_type == "array" and not isinstance(field_value, list):
#                     validation_result["valid"] = False
#                     validation_result["errors"].append(f"Field {field_name} should be array")
#                 elif expected_type == "object" and not isinstance(field_value, dict):
#                     validation_result["valid"] = False
#                     validation_result["errors"].append(f"Field {field_name} should be object")
#
#         validation_result["data"] = tool_call.arguments
#         return validation_result