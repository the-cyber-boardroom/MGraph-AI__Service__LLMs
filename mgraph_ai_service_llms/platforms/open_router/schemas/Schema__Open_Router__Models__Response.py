from typing                                                                          import List
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_llms.platforms.open_router.schemas.Schema__Open_Router__Model import Schema__Open_Router__Model


class Schema__Open_Router__Models__Response(Type_Safe):
    data : List[Schema__Open_Router__Model]                                     # List of available models

    def json(self):
        data__json = []
        for model in self.data:
            data__json.append(model.json())

        return dict(data=data__json)