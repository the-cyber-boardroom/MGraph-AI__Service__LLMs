import pytest
from unittest                                                                                         import TestCase
from fastapi.testclient                                                                              import TestClient
from osbot_fast_api.schemas.consts__Fast_API import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Env                                                                           import get_env, load_dotenv
from mgraph_ai_service_llms.fast_api.Service__Fast_API                                               import Service__Fast_API
from mgraph_ai_service_llms.platforms.open_router.fast_api.routes.Routes__Text_Analysis import TAG__ROUTES_TEXT_ANALYSIS, ROUTES_PATHS__TEXT_ANALYSIS
from mgraph_ai_service_llms.platforms.open_router.service.Service__Open_Router                       import ENV_NAME_OPEN_ROUTER__API_KEY
from mgraph_ai_service_llms.platforms.open_router.service.Service__Text_Analysis import DEFAULT_PROMPT_TEXT
from tests.unit.Service__Fast_API__Test_Objs                                                         import setup__service_fast_api_test_objs


class test_Routes__Text_Analysis(TestCase):

    @classmethod
    def setUpClass(cls):                                                                                  # Setup FastAPI test client using main app
        load_dotenv()
        cls.test_objs = setup__service_fast_api_test_objs()

        if not get_env(ENV_NAME_OPEN_ROUTER__API_KEY):
            pytest.skip(f"Skipping test: OpenRouter API key not found in environment variable: {ENV_NAME_OPEN_ROUTER__API_KEY}")

        # Use the main Service__Fast_API which already has routes configured
        #cls.service_fast_api = Service__Fast_API()
        #cls.service_fast_api.setup()
        #cls.app    = cls.service_fast_api.app()
        cls.app     = cls.test_objs.fast_api__app
        cls.client  = cls.test_objs.fast_api__client # TestClient(cls.app)
        cls.auth_key_name       = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME )
        cls.auth_key_value      = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE)
        cls.client.headers.update({cls.auth_key_name: cls.auth_key_value})
        cls.base_path = '/platform/open-router'
        # Test data
        cls.test_text = DEFAULT_PROMPT_TEXT

    def test_constants(self):                                                                             # Test route constants
        assert TAG__ROUTES_TEXT_ANALYSIS   == 'text-analysis'
        assert ROUTES_PATHS__TEXT_ANALYSIS == [ '/text-analysis/facts'       ,
                                                '/text-analysis/data-points' ,
                                                '/text-analysis/questions'   ,
                                                '/text-analysis/hypotheses'  ,
                                                '/text-analysis/analyze-all' ]

    def test_facts_endpoint(self):                                                                        # Test facts extraction endpoint
        response = self.client.post(self.base_path + "/text-analysis/facts",
                                   json={"text": self.test_text})

        assert response.status_code == 200
        data = response.json()

        assert "text"        in data
        assert "facts"       in data
        assert "facts_count" in data
        assert "model"       in data
        assert "provider"    in data

        assert data["text"] == self.test_text
        assert isinstance(data["facts"], list)
        assert len(data["facts"]) > 0
        assert data["facts_count"] == len(data["facts"])

        # Check that facts are relevant
        facts_str = ' '.join(data["facts"]).lower()
        assert any(term in facts_str for term in ["q3", "revenue", "$5.2 million", "5.2", "30%", "jane", "smith", "50", "employees", "december"])

    def test_data_points_endpoint(self):                                                                  # Test data points extraction endpoint
        response = self.client.post(self.base_path + "/text-analysis/data-points",
                                    json={"text": self.test_text})

        assert response.status_code == 200
        data = response.json()

        assert "data_points"       in data
        assert "data_points_count" in data

        assert isinstance(data["data_points"], list)
        assert len(data["data_points"]) > 0

        # Should extract numerical data
        data_str = ' '.join(data["data_points"]).lower()
        assert any(term in data_str for term in ["$5.2 million", "5.2", "30%", "50", "q3", "december"])

    def test_questions_endpoint(self):                                                                    # Test questions generation endpoint
        response = self.client.post(self.base_path + "/text-analysis/questions",
                                   json={"text": self.test_text})

        assert response.status_code == 200
        data = response.json()

        assert "questions"       in data
        assert "questions_count" in data

        assert isinstance(data["questions"], list)
        assert len(data["questions"]) > 0

        # Check questions format
        for question in data["questions"]:
            assert isinstance(question, str)
            assert len(question) > 5                                                                      # Not empty questions

    def test_hypotheses_endpoint(self):                                                                   # Test hypotheses generation endpoint
        response = self.client.post(self.base_path + "/text-analysis/hypotheses",
                                   json={"text": self.test_text})

        assert response.status_code == 200
        data = response.json()

        assert "hypotheses"       in data
        assert "hypotheses_count" in data

        assert isinstance(data["hypotheses"], list)
        assert len(data["hypotheses"]) > 0

        # Hypotheses should be substantive statements
        for hypothesis in data["hypotheses"]:
            assert isinstance(hypothesis, str)
            assert len(hypothesis) > 10

    def test_analyze_all_endpoint(self):                                                                  # Test comprehensive analysis endpoint
        response = self.client.post(self.base_path + "/text-analysis/analyze-all",
                                   json={"text": self.test_text})

        assert response.status_code == 200
        data = response.json()

        # Check all components present
        assert "facts"       in data
        assert "data_points" in data
        assert "questions"   in data
        assert "hypotheses"  in data
        assert "summary"     in data

        # Check summary structure
        summary = data["summary"]
        assert "facts_count"       in summary
        assert "data_points_count" in summary
        assert "questions_count"   in summary
        assert "hypotheses_count"  in summary

        # Verify counts match
        assert summary["facts_count"]       == len(data["facts"])
        assert summary["data_points_count"] == len(data["data_points"])
        assert summary["questions_count"]   == len(data["questions"])
        assert summary["hypotheses_count"]  == len(data["hypotheses"])

        # All should have content
        assert len(data["facts"])       > 0
        assert len(data["data_points"]) > 0
        assert len(data["questions"])   > 0
        assert len(data["hypotheses"])  > 0

    def test_empty_text(self):                                                                            # Test with empty text
        response = self.client.post(self.base_path + "/text-analysis/facts",
                                   json={"text": ""})

        assert response.status_code == 200
        data = response.json()
        assert "facts" in data
        assert isinstance(data["facts"], list)

    def test_technical_text(self):                                                                        # Test with technical content
        technical_text = """
        API endpoint latency: p50=45ms, p95=120ms, p99=250ms.
        Database throughput: 15,000 QPS with 2ms average query time.
        Cache hit rate: 92.5% across 3 Redis clusters.
        """

        response = self.client.post(self.base_path + "/text-analysis/data-points",
                                   json={"text": technical_text})

        assert response.status_code == 200
        data = response.json()

        assert len(data["data_points"]) >= 3                                                              # Should extract multiple metrics

        data_str = ' '.join(data["data_points"]).lower()
        assert any(term in data_str for term in ["45ms", "120ms", "250ms", "15,000", "15000", "92.5%", "qps", "redis"])

    def test_narrative_text(self):                                                                        # Test with narrative content
        narrative_text = """
        After three months of development, the team successfully launched the new feature.
        Initial user feedback has been overwhelmingly positive, with engagement increasing significantly.
        However, some performance issues were reported during peak hours.
        """

        response = self.client.post(self.base_path + "/text-analysis/hypotheses",
                                   json={"text": narrative_text})

        assert response.status_code == 200
        data = response.json()

        assert len(data["hypotheses"]) > 0

        # Should generate hypotheses about the situation
        hypotheses_str = ' '.join(data["hypotheses"]).lower()
        assert any(term in hypotheses_str for term in ["performance", "users", "feature", "team", "scale", "capacity", "load", "success"])

    def test_question_worthy_text(self):                                                                  # Test text that should generate good questions
        text = """
        The project is behind schedule by two weeks due to unexpected technical challenges.
        Budget has increased by 15% but stakeholder approval is pending.
        Three team members have requested additional resources.
        """

        response = self.client.post(self.base_path + "/text-analysis/questions",
                                   json={"text": text})

        assert response.status_code == 200
        data = response.json()

        assert len(data["questions"]) >= 3                                                                # Should generate multiple questions

        questions_str = ' '.join(data["questions"]).lower()
        # Questions should relate to the issues mentioned
        assert any(term in questions_str for term in ["schedule", "budget", "resources", "challenges", "stakeholder", "technical", "approval"])

    def test_routes_registered_in_app(self):                                                              # Test that routes are properly registered
        routes = self.test_objs.fast_api.routes_paths(expand_mounts=True)

        # Check that our text-analysis routes are registered
        assert self.base_path + "/text-analysis/facts"       in routes
        assert self.base_path + "/text-analysis/data-points" in routes
        assert self.base_path + "/text-analysis/questions"   in routes
        assert self.base_path + "/text-analysis/hypotheses"  in routes
        assert self.base_path + "/text-analysis/analyze-all" in routes

    def test_other_routes_still_work(self):                                                               # Test that other routes still function

        # Test that adding text-analysis didn't break other routes
        response = self.client.get("/info/health")
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}

        # Test LLM simple route still works
        response = self.client.get(self.base_path + "/llm-simple/models")
        assert response.status_code == 200
        assert "available_models" in response.json()