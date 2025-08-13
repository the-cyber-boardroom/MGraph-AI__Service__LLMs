from osbot_utils.helpers.safe_str.Safe_Str__Text                        import Safe_Str__Text
from osbot_utils.helpers.llms.builders.LLM_Request__Builder__Open_AI    import LLM_Request__Builder__Open_AI
from osbot_utils.helpers.llms.schemas.Schema__LLM_Request               import Schema__LLM_Request
from osbot_utils.helpers.llms.schemas.Schema__LLM_Response              import Schema__LLM_Response
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.type_safe.decorators.type_safe                         import type_safe
from osbot_utils.utils.Json                                             import str_to_json

from mgraph_ai_service_llms.service.llms.prompts.schemas.Schema__Facts import Schema__Facts

SYSTEM_PROMPT__EXTRACT_FACTS = """You are a fact extraction expert that identifies and extracts key factual information from text.

Your task is to:
1. Extract concrete, verifiable facts from the text
2. Categorize each fact appropriately
3. Assign a confidence level to each fact
4. Provide a brief summary of the main points

For each fact, assign a category:
- "date" - Temporal information (dates, times, periods)
- "person" - Names of people or roles
- "location" - Places, addresses, geographic locations
- "number" - Quantities, amounts, statistics, measurements
- "event" - Actions, occurrences, happenings
- "organization" - Companies, institutions, groups
- "other" - Facts that don't fit the above categories

For confidence levels, use a scale from 0 to 1:
- 0.9-1.0 = Explicitly stated, clear fact
- 0.7-0.8 = Strongly implied or very likely
- 0.5-0.6 = Reasonably inferred
- Below 0.5 = Uncertain or speculative"""

USER_PROMPT__EXTRACT_FACTS = """\
Extract the key facts from the following text:

======================== TEXT CONTENT ========================
{text_content}
==============================================================

Extract:
1. All identifiable facts with their confidence levels and categories
2. A brief summary of the main points
"""


class LLM__Prompt__Extract_Facts(Type_Safe):
    request_builder: LLM_Request__Builder__Open_AI

    def llm_request(self, text_content: str, model_to_use: Safe_Str__Text = None) -> Schema__LLM_Request:
        system_prompt = SYSTEM_PROMPT__EXTRACT_FACTS
        user_prompt   = USER_PROMPT__EXTRACT_FACTS.format(text_content=text_content)

        with self.request_builder as _:
            if model_to_use:
                _.set__model(model_to_use)
            else:
                _.set__model__gpt_4o_mini()  # Default to GPT-4o-mini
            _.add_message__system(system_prompt)
            _.add_message__user(user_prompt)
            _.set__function_call(parameters=Schema__Facts, function_name='extract_facts')

        return self.request_builder.llm_request()

    @type_safe
    def process_llm_response(self, llm_response: Schema__LLM_Response) -> Schema__Facts: # Process the LLM response into structured facts.
        content         = llm_response.obj().response_data.choices[0].message.content
        content_json    = str_to_json(content)
        return Schema__Facts.from_json(content_json)
