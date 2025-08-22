from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.git.Safe_Str__Version        import Safe_Str__Version
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id          import Safe_Id
from mgraph_ai_service_llms.config                                          import SERVICE_NAME
from mgraph_ai_service_llms.service.info.schemas.Enum__Service_Environment  import Enum__Service_Environment
from mgraph_ai_service_llms.service.info.schemas.Enum__Service_Status       import Enum__Service_Status
from mgraph_ai_service_llms.utils.Version                                   import version__mgraph_ai_service_llms

class Schema__Service__Status(Type_Safe):
    name        : Safe_Id                   = Safe_Id(SERVICE_NAME)
    version     : Safe_Str__Version         = version__mgraph_ai_service_llms
    status      : Enum__Service_Status      = Enum__Service_Status.operational
    environment : Enum__Service_Environment = Enum__Service_Environment.local