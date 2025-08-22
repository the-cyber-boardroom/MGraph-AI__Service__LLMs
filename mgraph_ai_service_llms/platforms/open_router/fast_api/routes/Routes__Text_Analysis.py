from typing                                                                      import Dict, Any
from osbot_fast_api.api.routes.Fast_API__Routes                                  import Fast_API__Routes
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Tag                       import Safe_Str__Fast_API__Route__Tag
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_llms.platforms.open_router.service.Service__Text_Analysis import Service__Text_Analysis, DEFAULT_PROMPT_TEXT

TAG__ROUTES_TEXT_ANALYSIS   = 'text-analysis'
ROUTES_PATHS__TEXT_ANALYSIS = [ f'/{TAG__ROUTES_TEXT_ANALYSIS}/facts'       ,
                                f'/{TAG__ROUTES_TEXT_ANALYSIS}/data-points' ,
                                f'/{TAG__ROUTES_TEXT_ANALYSIS}/questions'   ,
                                f'/{TAG__ROUTES_TEXT_ANALYSIS}/hypotheses'  ,
                                f'/{TAG__ROUTES_TEXT_ANALYSIS}/analyze-all' ]

class Prompt_Text(Type_Safe):
    text: str = DEFAULT_PROMPT_TEXT

class Routes__Text_Analysis(Fast_API__Routes):
    tag             : Safe_Str__Fast_API__Route__Tag = TAG__ROUTES_TEXT_ANALYSIS
    service_analysis: Service__Text_Analysis         = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service_analysis = Service__Text_Analysis()

    def facts(self, prompt_text: Prompt_Text                                                                            # Extract facts from text
               ) -> Dict[str, Any]:
        return self.service_analysis.extract_facts(prompt_text.text)

    def data_points(self, prompt_text: Prompt_Text                                                                      # Extract data points from text
                   ) -> Dict[str, Any]:
        return self.service_analysis.extract_data_points(prompt_text.text)

    def questions(self, prompt_text: Prompt_Text                                                                        # Generate follow-up questions
                 ) -> Dict[str, Any]:
        return self.service_analysis.generate_questions(prompt_text.text)

    def hypotheses(self, prompt_text: Prompt_Text                                                                       # Generate hypotheses from text
                  ) -> Dict[str, Any]:
        return self.service_analysis.generate_hypotheses(prompt_text.text)

    def analyze_all(self, prompt_text: Prompt_Text                                                                      # Run all analysis types
                   ) -> Dict[str, Any]:
        return self.service_analysis.analyze_all(prompt_text.text)

    def setup_routes(self):
        self.add_route_post(self.facts       )
        self.add_route_post(self.data_points )
        self.add_route_post(self.questions   )
        self.add_route_post(self.hypotheses  )
        self.add_route_post(self.analyze_all )