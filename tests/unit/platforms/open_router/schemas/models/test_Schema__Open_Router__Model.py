from typing                                                                                             import List
from unittest                                                                                           import TestCase
from osbot_aws.testing.skip_tests                                                                       import skip__if_not__in_github_actions
from osbot_utils.helpers.duration.decorators.print_duration                                             import print_duration
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.Safe_Str                                                 import Safe_Str
from mgraph_ai_service_llms.platforms.open_router.Service__Open_Router__Models                          import Service__Open_Router__Models
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Model             import Schema__Open_Router__Model
from mgraph_ai_service_llms.platforms.open_router.schemas.models.Schema__Open_Router__Models__Response  import Schema__Open_Router__Models__Response



class test_Schema__Open_Router__Model(TestCase):


    def test__regression__not_all_models_serialise_ok(self):
        #skip__if_not__in_github_actions()
        with print_duration(action_name='download data'):                                   # ~ 0.744 seconds
            raw_data        = Service__Open_Router__Models().download__api__models()
            raw_models_data = raw_data.get('data')
            assert len(raw_models_data) > 300
        with print_duration(action_name='convert to model (each one at the time)'):         # ~ 0.156 seconds
            for raw_model_data in raw_models_data:       #there are 300(ish) models
                model_id   = raw_model_data.get('id'  , 'NA')
                model_name = raw_model_data.get('name', 'NA')
                model = Schema__Open_Router__Model.from_json(raw_model_data)
                assert str(model.description) == raw_model_data.get('description')
                if model.json() == raw_model_data:
                    #print(f'match for: {model_id}')
                    pass
                else:
                    print(f'fails for match for: {model_id}')
                    #assert model.round_trip_json() == raw_model_data
        with print_duration(action_name='convert to model (all at once)'):                  # ~ 0.092 seconds
            models_response = Schema__Open_Router__Models__Response.from_json(raw_data)

        with print_duration(action_name='create json'):                                     # ~ 0.016 seconds
            assert models_response.json() == raw_data

            # try:
            #     model = Schema__Open_Router__Model.from_json(raw_model_data)
            # except ValueError as e:
            #     print(f"error failed: {model_name:30} | {model_id} ")
            #     pprint(raw_model_data)
            #     return
            #         print({str(e)})
            #         print()
            #         print()



    def test__bug__in_type_safe__list__nested_conversion(self):
        class Schema__Model(Type_Safe):
            an_list : List[Safe_Str]

        class Schema__Models(Type_Safe):
            data: List[Schema__Model]

        model        = Schema__Model (an_list=[Safe_Str('abc')])
        models       = Schema__Models(data=[model])
        model__json  = model.json()
        models__json = models.json()

        assert model__json  == {'an_list': ['abc']}
        assert models__json == {'data': [{'an_list': ['abc']}]}

        model__roundtrip = Schema__Model.from_json(model__json)                     # roundtrip model directly
        assert model__roundtrip.json() == model__json                               # works

        # BUG
        # error_message_2 = "In Type_Safe__List: Invalid type for item: Expected 'Safe_Str', but got 'str'"
        # with pytest.raises(TypeError, match=error_message_2):
        #     Schema__Model (an_list=['abc'])                     # BUG this should support just 'abc'
        Schema__Model(an_list=['abc'])

        # error_message_2 = "In Type_Safe__List: Invalid type for item: Expected 'Safe_Str', but got 'str'"
        # with pytest.raises(TypeError, match=error_message_2):
        #     Schema__Models.from_json(models__json)              # BUG but roundtrip from list fails
        Schema__Models.from_json(models__json)




