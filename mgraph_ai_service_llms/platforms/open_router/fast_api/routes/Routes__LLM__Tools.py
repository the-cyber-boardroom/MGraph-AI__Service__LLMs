# todo: this needs to recreated with better support (once the JSON_Output is done)

# from typing                                                                                            import Dict, Any, List
# from osbot_fast_api.api.routes.Fast_API__Routes                                                        import Fast_API__Routes
# from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Tag                                             import Safe_Str__Fast_API__Route__Tag
# from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Call                import Schema__LLM__Tool__Call
# from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Response            import Schema__LLM__Tool__Response
# from mgraph_ai_service_llms.platforms.open_router.service.Service__LLM__Tools                          import Service__LLM__Tools
# from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Request             import Schema__LLM__Tool__Request
# from mgraph_ai_service_llms.platforms.open_router.schemas.tools.Schema__LLM__Tool__Definition          import Schema__LLM__Tool__Definition
#
# TAG__ROUTES_LLM_TOOLS   = 'llm-tools'
# ROUTES_PATHS__LLM_TOOLS = [ f'/{TAG__ROUTES_LLM_TOOLS}/complete-with-tool'    ,
#                            f'/{TAG__ROUTES_LLM_TOOLS}/validate-tool-arguments']
#
# class Routes__LLM__Tools(Fast_API__Routes):
#     tag          : Safe_Str__Fast_API__Route__Tag = TAG__ROUTES_LLM_TOOLS
#     service_tools: Service__LLM__Tools           = None
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.service_tools = Service__LLM__Tools()
#
#     def complete_with_tool(self, request: Schema__LLM__Tool__Request                                        # Execute completion with tool/function support
#                            ) -> Schema__LLM__Tool__Response:
#         """
#         Execute LLM completion with tool/function calling support.
#
#         The calling service provides:
#         1. The user prompt
#         2. A tool definition (converted from Type_Safe using Type_Safe__To__LLM_Tools)
#         3. Model and parameters
#
#         Returns tool calls that the LLM wants to make, which the calling service
#         can then execute locally since it knows the actual implementation.
#         """
#         return self.service_tools.execute_with_tool(request)
#
#     def validate_tool_arguments(self, tool_name       : str                        ,                        # Validate tool arguments against schema
#                                       tool_arguments  : Dict[str, Any]             ,
#                                       tool_definition : Schema__LLM__Tool__Definition
#                                 ) -> Dict[str, Any]:
#         """
#         Validate that tool arguments match the expected schema.
#
#         This is useful for the calling service to validate LLM-generated
#         arguments before attempting to execute the tool.
#
#         Returns:
#             Dictionary with 'valid' (bool), 'errors' (list), and 'data' (cleaned arguments)
#         """
#
#         # Create tool call object
#         tool_call = Schema__LLM__Tool__Call(name      = tool_name     ,
#                                             arguments = tool_arguments)
#
#         return self.service_tools.validate_tool_arguments(tool_call, tool_definition)
#
#     def test_echo_tool(self) -> Schema__LLM__Tool__Response:                                                # Test endpoint with a simple echo tool
#         """
#         Test endpoint that demonstrates tool usage with a simple echo function.
#         This helps verify the tool calling pipeline is working correctly.
#         """
#
#         # Define a simple echo tool
#         echo_tool = Schema__LLM__Tool__Definition(
#             name        = "echo_message"                                   ,
#             description = "Echo back a message with optional formatting"   ,
#             parameters  = { "type"       : "object"                                              ,
#                            "properties" : { "message"   : { "type"        : "string"                            ,
#                                                            "description" : "The message to echo"                },
#                                            "uppercase" : { "type"        : "boolean"                           ,
#                                                            "description" : "Whether to return in uppercase"    ,
#                                                            "default"    : False                                 } },
#                            "required"   : ["message"]                                           }
#         )
#
#         # Create request
#         request = Schema__LLM__Tool__Request(
#             user_prompt     = "Please echo the message 'Hello World' in uppercase"  ,
#             system_prompt   = "You are a helpful assistant that uses tools when asked.",
#             tool_definition = echo_tool                                             ,
#             force_tool_use  = True
#         )
#
#         return self.service_tools.execute_with_tool(request)
#
#     def setup_routes(self):
#         self.add_route_post(self.complete_with_tool    )
#         self.add_route_post(self.validate_tool_arguments)
#         self.add_route_get (self.test_echo_tool        )