from typing                                                                                                 import List, Optional, Dict, Any
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.utils.Http                                                                                 import GET_json
from osbot_utils.decorators.methods.cache_on_self                                                           import cache_on_self
from osbot_utils.type_safe.primitives.safe_float.Safe_Float                                                 import Safe_Float

from mgraph_ai_service_llms.platforms.open_router.cache.Open_Router__Models__Cache import Open_Router__Models__Cache
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Model_ID                   import Safe_Str__Open_Router__Model_ID
from mgraph_ai_service_llms.platforms.open_router.schemas.Safe_Str__Open_Router__Modality                   import Safe_Str__Open_Router__Modality
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model                 import Schema__Open_Router__Model
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Models__Response      import Schema__Open_Router__Models__Response
from mgraph_ai_service_llms.platforms.open_router.schemas.consts__Open_Router                               import URL__OPEN_ROUTER__API__V1_MODELS, URL__OPEN_ROUTER__API__V1_PROVIDERS


class Service__Open_Router__Models(Type_Safe):

    @cache_on_self
    def open_router__models_cache(self):
        return Open_Router__Models__Cache().setup()

    def api__url__models(self):
        return URL__OPEN_ROUTER__API__V1_MODELS

    def api__providers__url(self):
        return URL__OPEN_ROUTER__API__V1_PROVIDERS

    def api__providers__download(self):
        return GET_json(self.api__providers__url())  # Fetch data from OpenRouter API

    def download__api__models(self):                                             # todo: add caching
        return GET_json(self.api__url__models())                                             # Fetch data from OpenRouter API

    def download__api__providers(self):                                             # todo: add caching
        return GET_json(self.api__url__models())                                             # Fetch data from OpenRouter API

    # rename to just models()
    def fetch_models(self) -> Schema__Open_Router__Models__Response:                # Fetch current list of available models
        try:
            cached_response = self.open_router__models_cache().get_cached_models()
            if cached_response and cached_response.data:
                return cached_response

            response_data   = self.download__api__models()
            models_response = Schema__Open_Router__Models__Response.from_json(response_data)

            self.open_router__models_cache().cache_models_response(models_response)
            return models_response

        except Exception as e:
            raise ValueError(f"Failed to fetch models from OpenRouter: {str(e)}")

    @cache_on_self
    def api__models(self) -> List[Schema__Open_Router__Model]:                # Get cached list of models
        response = self.fetch_models()
        return response.data

    @cache_on_self
    def api__providers(self):
        return self.api__providers__download()

    def get_model_by_id(self, model_id : Safe_Str__Open_Router__Model_ID        # Get specific model by ID
                        ) -> Optional[Schema__Open_Router__Model]:
        models = self.api__models()
        for model in models:
            if model.id == model_id:
                return model
        return None

    def get_models_by_modality(self, modality : Safe_Str__Open_Router__Modality # Get models supporting specific modality
                               ) -> List[Schema__Open_Router__Model]:
        models = self.api__models()
        return [m for m in models if m.architecture.modality == modality]

    def get_free_models(self                                                    # Get models that are free to use
                        ) -> List[Schema__Open_Router__Model]:
        models      = self.api__models()
        free_models = []
        zero_cost   = Safe_Float(0.0)

        for model in models:
            if float(model.pricing.prompt) == 0 and float(model.pricing.completion) == 0:
                free_models.append(model)
        return free_models

    def get_models_summary(self                                                 # Get summary of available models
                           ) -> Dict[str, Any]:
        models = self.api__models()

        modalities = {}                                                         # Group by modality
        for model in models:
            modality = str(model.architecture.modality)
            if modality not in modalities:
                modalities[modality] = []
            modalities[modality].append(str(model.id))

        free_models = self.get_free_models()                                    # Find free models

        return { "total_models"      : len(models)                             ,
                 "free_models_count"  : len(free_models)                       ,
                 "free_models"        : [str(m.id) for m in free_models]       ,
                 "modalities"         : modalities                             ,
                 "tokenizers"         : list(set(str(m.architecture.tokenizer) for m in models)) }

