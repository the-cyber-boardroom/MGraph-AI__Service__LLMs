import json
from typing                                                                                          import List, Dict, Any
from osbot_utils.type_safe.Type_Safe                                                                 import Type_Safe
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                       import Service__Open_Router
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers        import Schema__Open_Router__Providers

DEFAULT_MODEL    = "openai/gpt-oss-120b"
DEFAULT_PROVIDER = Schema__Open_Router__Providers.GROQ
DEFAULT_PROMPT_TEXT = "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December."

# System prompts for each analysis type
SYSTEM_PROMPT_FACTS = """You are a fact extraction expert. Extract concrete, verifiable facts from the text.
Return ONLY a JSON array of strings, where each string is a single fact.
Facts should be specific, clear, and based only on what's stated in the text.
Example: ["The meeting is scheduled for 3pm", "John is the project manager", "The budget is $50,000"]"""

SYSTEM_PROMPT_DATA_POINTS = """You are a data extraction specialist. Extract quantifiable data points, metrics, numbers, and measurements from the text.
Return ONLY a JSON array of strings, where each string describes a specific data point.
Include numbers, percentages, dates, quantities, measurements, and any quantifiable information.
Example: ["Revenue increased by 25%", "3 team members assigned", "Deadline: March 15, 2024", "Temperature: 72°F"]"""

SYSTEM_PROMPT_QUESTIONS = """You are a conversation strategist. Based on the text provided, generate insightful follow-up questions to ask the user.
Return ONLY a JSON array of strings, where each string is a question.
Questions should seek clarification, explore implications, or gather additional relevant information.
Example: ["What is the expected ROI for this project?", "Have you considered the regulatory requirements?", "Who are the key stakeholders?"]"""

SYSTEM_PROMPT_HYPOTHESES = """You are an analytical thinker. Based on the text, generate reasonable hypotheses or educated inferences.
Return ONLY a JSON array of strings, where each string is a hypothesis.
Hypotheses should be logical extensions or interpretations based on the information provided.
Example: ["The delay might be due to resource constraints", "This pattern suggests seasonal demand", "The user may be planning a product launch"]"""


class Service__Text_Analysis(Type_Safe):
    open_router     : Service__Open_Router                  = None
    model           : str                                   = DEFAULT_MODEL
    provider        : Schema__Open_Router__Providers        = DEFAULT_PROVIDER
    temperature     : float                                  = 0.3                # Lower temperature for more consistent extraction
    max_tokens      : int                                    = 1000

    def __init__(self):
        super().__init__()
        self.open_router = Service__Open_Router()

    def _extract_json_list(self, text          : str ,                                                   # Helper to extract JSON list from LLM response
                                 system_prompt : str
                          ) -> List[str]:

        user_prompt = f"Analyze the following text:\n\n{text}"

        response = self.open_router.chat_completion(
            prompt        = user_prompt                ,
            model         = self.model                 ,
            system_prompt = system_prompt              ,
            temperature   = self.temperature           ,
            max_tokens    = self.max_tokens            ,
            provider      = self.provider.value        ,
            max_cost      = 0.5                        )

        response_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Try to parse JSON response
        try:
            # Clean up response text - remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text.strip())

            # Ensure it's a list
            if isinstance(result, list):
                # Ensure all items are strings
                return [str(item) for item in result]
            else:
                return []

        except (json.JSONDecodeError, IndexError):
            # Fallback: try to extract bullet points or numbered items
            lines = response_text.split('\n')
            items = []
            for line in lines:
                line = line.strip()
                # Remove common list markers
                if line.startswith(('- ', '* ', '• ')):
                    items.append(line[2:].strip())
                elif line and line[0].isdigit() and ('. ' in line or ') ' in line):
                    # Handle numbered lists
                    items.append(line.split('. ', 1)[-1].split(') ', 1)[-1].strip())
                elif line and '"' in line:
                    # Try to extract quoted strings
                    import re
                    quotes = re.findall(r'"([^"]+)"', line)
                    items.extend(quotes)

            return items if items else [response_text] if response_text else []

    def extract_facts(self, text: str                                                                    # Extract facts from text
                     ) -> Dict[str, Any]:
        facts = self._extract_json_list(text, SYSTEM_PROMPT_FACTS)

        return { "text"        : text                    ,
                 "facts"       : facts                   ,
                 "facts_count" : len(facts)              ,
                 "model"       : self.model              ,
                 "provider"    : self.provider.value     }

    def extract_data_points(self, text: str                                                              # Extract data points from text
                           ) -> Dict[str, Any]:
        data_points = self._extract_json_list(text, SYSTEM_PROMPT_DATA_POINTS)

        return { "text"              : text                      ,
                 "data_points"       : data_points               ,
                 "data_points_count" : len(data_points)          ,
                 "model"             : self.model                ,
                 "provider"          : self.provider.value       }

    def generate_questions(self, text: str                                                               # Generate follow-up questions
                          ) -> Dict[str, Any]:
        questions = self._extract_json_list(text, SYSTEM_PROMPT_QUESTIONS)

        return { "text"            : text                        ,
                 "questions"       : questions                   ,
                 "questions_count" : len(questions)              ,
                 "model"           : self.model                  ,
                 "provider"        : self.provider.value         }

    def generate_hypotheses(self, text: str                                                              # Generate hypotheses from text
                           ) -> Dict[str, Any]:
        hypotheses = self._extract_json_list(text, SYSTEM_PROMPT_HYPOTHESES)

        return { "text"             : text                       ,
                 "hypotheses"       : hypotheses                 ,
                 "hypotheses_count" : len(hypotheses)            ,
                 "model"            : self.model                 ,
                 "provider"         : self.provider.value        }

    def analyze_all(self, text: str                                                                      # Run all analysis types
                   ) -> Dict[str, Any]:
        facts       = self._extract_json_list(text, SYSTEM_PROMPT_FACTS      )
        data_points = self._extract_json_list(text, SYSTEM_PROMPT_DATA_POINTS)
        questions   = self._extract_json_list(text, SYSTEM_PROMPT_QUESTIONS  )
        hypotheses  = self._extract_json_list(text, SYSTEM_PROMPT_HYPOTHESES )

        return { "text"        : text                    ,
                 "facts"       : facts                   ,
                 "data_points" : data_points             ,
                 "questions"   : questions               ,
                 "hypotheses"  : hypotheses              ,
                 "summary"     : { "facts_count"       : len(facts)       ,
                                  "data_points_count"  : len(data_points) ,
                                  "questions_count"    : len(questions)   ,
                                  "hypotheses_count"   : len(hypotheses)  },
                 "model"       : self.model              ,
                 "provider"    : self.provider.value     }