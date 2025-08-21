import pytest
from unittest                                                                                         import TestCase
from osbot_utils.type_safe.Type_Safe                                                                  import Type_Safe
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects                                                                        import base_classes
from osbot_utils.utils.Env                                                                            import get_env, load_dotenv
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                        import Service__Open_Router, ENV_NAME_OPEN_ROUTER__API_KEY
from mgraph_ai_service_llms.platforms.open_router.service.Service__Text_Analysis                      import Service__Text_Analysis, DEFAULT_MODEL, DEFAULT_PROVIDER
from mgraph_ai_service_llms.service.llms.providers.open_router.Schema__Open_Router__Providers         import Schema__Open_Router__Providers
from tests.unit.Service__Fast_API__Test_Objs                                                          import setup__service_fast_api_test_objs


class test_Service__Text_Analysis(TestCase):

    @classmethod
    def setUpClass(cls):                                                                                  # Setup for all tests
        load_dotenv()
        setup__service_fast_api_test_objs()

        if not get_env(ENV_NAME_OPEN_ROUTER__API_KEY):
            pytest.skip(f"Skipping test: OpenRouter API key not found in environment variable: {ENV_NAME_OPEN_ROUTER__API_KEY}")

        cls.service = Service__Text_Analysis()

        # Test texts with different characteristics
        cls.test_text_simple = "The meeting is scheduled for 3pm on Friday. John will present the Q4 results showing a 25% increase in revenue."

        cls.test_text_complex = """
        Our new product launch achieved remarkable success in Q3 2024. 
        Sales exceeded projections by 45%, reaching $2.3 million in the first month.
        Customer satisfaction scores averaged 4.8 out of 5 based on 1,500 reviews.
        The marketing campaign had a click-through rate of 3.2% and conversion rate of 12%.
        We plan to expand to 5 new markets by March 2025.
        """

        cls.test_text_technical = """
        The system processes 10,000 requests per second with 99.9% uptime.
        Average response time is 150ms with a p95 latency of 300ms.
        The database contains 5TB of data across 3 geographic regions.
        """

    def test__init__(self):                                                                               # Test initialization
        service = Service__Text_Analysis()

        assert type(service)             is Service__Text_Analysis
        assert base_classes(service)     == [Type_Safe, object]
        assert type(service.open_router) is Service__Open_Router
        assert service.model             == DEFAULT_MODEL
        assert service.provider          == DEFAULT_PROVIDER
        assert service.temperature       == 0.3
        assert service.max_tokens        == 1000

    def test_extract_facts_simple(self):                                                                  # Test fact extraction with simple text
        result = self.service.extract_facts(self.test_text_simple)

        assert "text"        in result
        assert "facts"       in result
        assert "facts_count" in result
        assert "model"       in result
        assert "provider"    in result

        assert result["text"]     == self.test_text_simple
        assert result["model"]    == DEFAULT_MODEL
        assert result["provider"] == DEFAULT_PROVIDER.value

        assert isinstance(result["facts"], list)
        assert len(result["facts"]) > 0
        assert result["facts_count"] == len(result["facts"])

        # Check that facts are relevant to the text
        facts_str = ' '.join(result["facts"]).lower()
        assert any(word in facts_str for word in ["meeting", "3pm", "friday", "john", "q4", "25%", "revenue"])

    def test_extract_facts_complex(self):                                                                 # Test fact extraction with complex text
        result = self.service.extract_facts(self.test_text_complex)

        assert isinstance(result["facts"], list)
        assert len(result["facts"]) > 3                                                                   # Should extract multiple facts

        facts_str = ' '.join(result["facts"]).lower()
        # Verify key facts are captured
        assert any(term in facts_str for term in ["q3", "2024", "45%", "$2.3 million", "4.8"])

    def test_extract_data_points_simple(self):                                                            # Test data point extraction
        result = self.service.extract_data_points(self.test_text_simple)

        assert "data_points"       in result
        assert "data_points_count" in result

        assert isinstance(result["data_points"], list)
        assert len(result["data_points"]) > 0

        # Should extract numerical data
        data_str = ' '.join(result["data_points"]).lower()
        assert any(term in data_str for term in ["3pm", "25%", "q4"])

    def test_extract_data_points_technical(self):                                                         # Test data points with technical text
        result = self.service.extract_data_points(self.test_text_technical)

        assert len(result["data_points"]) >= 3                                                            # Multiple data points

        data_str = ' '.join(result["data_points"]).lower()
        # Should capture technical metrics
        assert any(term in data_str for term in ["10,000", "10000", "99.9%", "150ms", "300ms", "5tb"])

    def test_generate_questions_simple(self):                                                             # Test question generation
        result = self.service.generate_questions(self.test_text_simple)

        assert "questions"       in result
        assert "questions_count" in result

        assert isinstance(result["questions"], list)
        assert len(result["questions"]) > 0

        # Questions should be actual questions
        for question in result["questions"]:
            assert isinstance(question, str)
            # Most should end with ? or contain question words
            is_question = (question.strip().endswith('?') or
                          any(q in question.lower() for q in ['what', 'why', 'how', 'when', 'who', 'which']))
            assert is_question, f"Not a question format: {question}"

    def test_generate_questions_complex(self):                                                            # Test questions with complex text
        result = self.service.generate_questions(self.test_text_complex)

        assert len(result["questions"]) >= 3                                                              # Should generate multiple questions

        questions_str = ' '.join(result["questions"]).lower()
        # Questions should be relevant to the content
        assert any(term in questions_str for term in ["product", "sales", "market", "customer", "expansion"])

    def test_generate_hypotheses_simple(self):                                                            # Test hypothesis generation
        result = self.service.generate_hypotheses(self.test_text_simple)

        assert "hypotheses"       in result
        assert "hypotheses_count" in result

        assert isinstance(result["hypotheses"], list)
        assert len(result["hypotheses"]) > 0

        # Hypotheses should be statements/inferences
        for hypothesis in result["hypotheses"]:
            assert isinstance(hypothesis, str)
            assert len(hypothesis) > 10                                                                   # Not just short phrases

    def test_generate_hypotheses_complex(self):                                                           # Test hypotheses with complex text
        result = self.service.generate_hypotheses(self.test_text_complex)

        assert len(result["hypotheses"]) >= 2                                                             # Should generate multiple hypotheses

        hypotheses_str = ' '.join(result["hypotheses"]).lower()
        # Should relate to the success metrics mentioned
        assert any(term in hypotheses_str for term in ["success", "growth", "market", "customer", "expansion", "performance"])

    def test_analyze_all(self):                                                                           # Test comprehensive analysis
        result = self.service.analyze_all(self.test_text_complex)

        assert "text"        in result
        assert "facts"       in result
        assert "data_points" in result
        assert "questions"   in result
        assert "hypotheses"  in result
        assert "summary"     in result

        # Check all components are lists
        assert isinstance(result["facts"], list)
        assert isinstance(result["data_points"], list)
        assert isinstance(result["questions"], list)
        assert isinstance(result["hypotheses"], list)

        # Check summary counts
        summary = result["summary"]
        assert summary["facts_count"]       == len(result["facts"])
        assert summary["data_points_count"] == len(result["data_points"])
        assert summary["questions_count"]   == len(result["questions"])
        assert summary["hypotheses_count"]  == len(result["hypotheses"])

        # All should have content
        assert summary["facts_count"]       > 0
        assert summary["data_points_count"] > 0
        assert summary["questions_count"]   > 0
        assert summary["hypotheses_count"]  > 0

    def test_empty_text_handling(self):                                                                   # Test with empty text
        empty_text = ""

        result = self.service.extract_facts(empty_text)
        assert isinstance(result["facts"], list)
        # Might return empty list or a message about no content

    def test_json_extraction_fallback(self):                                                              # Test fallback when JSON parsing fails
        # This tests the internal _extract_json_list method indirectly
        text_with_numbers = "Item 1: Revenue $100k. Item 2: Costs $50k. Item 3: Profit $50k."

        result = self.service.extract_data_points(text_with_numbers)

        assert len(result["data_points"]) > 0                                                             # Should extract something even if JSON fails

    def test_provider_configuration(self):                                                                # Test different provider configuration
        service = Service__Text_Analysis()
        service.provider = Schema__Open_Router__Providers.CEREBRAS
        service.temperature = 0.5

        result = service.extract_facts("Test text with different provider.")
        assert result["provider"] == "cerebras"

    def test_long_text_handling(self):                                                                    # Test with longer text
        long_text = " ".join([self.test_text_complex] * 5)                                               # Repeat text 5 times

        result = self.service.extract_facts(long_text)
        assert isinstance(result["facts"], list)
        assert len(result["facts"]) > 0

    def test_special_characters_handling(self):                                                           # Test with special characters
        text_with_special = "Revenue: $1,234.56 | Growth: 25% → 35% | Status: ✓ Complete"

        result = self.service.extract_data_points(text_with_special)
        assert len(result["data_points"]) > 0

        # Should handle currency and percentages
        data_str = ' '.join(result["data_points"]).lower()
        assert any(char in data_str for char in ["$", "%", "1234", "25", "35"])