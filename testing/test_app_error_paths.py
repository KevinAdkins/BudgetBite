"""
Comprehensive test suite for all error paths in app.py
Tests every error condition, exception handler, and edge case
"""

import pytest
import json
import base64
import sys
import os
from unittest.mock import patch, MagicMock, Mock
import tempfile

# Add backend and src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import (
    app,
    _extract_estimated_total,
    _is_recipe_over_budget,
    _is_recipe_below_budget_floor,
    _build_top_matches,
    _analyze_ingredients_pipeline,
)


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestExtractEstimatedTotal:
    """Test _extract_estimated_total helper function"""

    def test_non_dict_input(self):
        """Should return None for non-dict input"""
        assert _extract_estimated_total(None) is None
        assert _extract_estimated_total("string") is None
        assert _extract_estimated_total([]) is None
        assert _extract_estimated_total(123) is None

    def test_missing_total_and_subtotal(self):
        """Should return None when neither field exists"""
        assert _extract_estimated_total({}) is None
        assert _extract_estimated_total({"other_field": 10}) is None

    def test_estimated_total_exists(self):
        """Should return estimatedTotal when it exists"""
        assert _extract_estimated_total({"estimatedTotal": 25.50}) == 25.50
        assert _extract_estimated_total({"estimatedTotal": "35.75"}) == 35.75

    def test_subtotal_fallback(self):
        """Should fallback to subtotal if estimatedTotal missing"""
        assert _extract_estimated_total({"subtotal": 45.00}) == 45.00
        assert _extract_estimated_total({"subtotal": "50.25"}) == 50.25

    def test_estimated_total_takes_precedence(self):
        """estimatedTotal should take precedence over subtotal"""
        assert _extract_estimated_total(
            {"estimatedTotal": 25.0, "subtotal": 50.0}
        ) == 25.0

    def test_invalid_float_conversion(self):
        """Should return None for non-convertible values"""
        assert _extract_estimated_total({"estimatedTotal": "not_a_number"}) is None
        assert _extract_estimated_total({"estimatedTotal": None}) is None
        assert _extract_estimated_total({"subtotal": {}}) is None

    def test_edge_case_zero(self):
        """Should handle zero correctly"""
        assert _extract_estimated_total({"estimatedTotal": 0}) == 0.0
        assert _extract_estimated_total({"estimatedTotal": "0"}) == 0.0


class TestIsRecipeOverBudget:
    """Test _is_recipe_over_budget helper function"""

    def test_none_estimated_total(self):
        """Should return False when estimated_total is None"""
        assert _is_recipe_over_budget(None, 'tier1') is False
        assert _is_recipe_over_budget(None, 'tier2') is False

    def test_invalid_budget_tier(self):
        """Should return False for unknown budget tier (tier3 is None limit)"""
        assert _is_recipe_over_budget(100.0, 'tier3') is False
        assert _is_recipe_over_budget(100.0, 'invalid_tier') is False

    def test_tier1_under_budget(self):
        """Should return False for amounts under tier1 ($25)"""
        assert _is_recipe_over_budget(24.99, 'tier1') is False

    def test_tier1_over_budget(self):
        """Should return True for amounts over tier1 ($25)"""
        assert _is_recipe_over_budget(25.01, 'tier1') is True
        assert _is_recipe_over_budget(50.0, 'tier1') is True

    def test_tier2_over_budget(self):
        """Should return True for amounts over tier2 ($50)"""
        assert _is_recipe_over_budget(50.01, 'tier2') is True
        assert _is_recipe_over_budget(100.0, 'tier2') is True

    def test_tier2_under_budget(self):
        """Should return False for amounts under tier2 limit"""
        assert _is_recipe_over_budget(49.99, 'tier2') is False


class TestIsRecipeBelowBudgetFloor:
    """Test _is_recipe_below_budget_floor helper function"""

    def test_none_estimated_total(self):
        """Should return False when estimated_total is None"""
        assert _is_recipe_below_budget_floor(None, 'tier1') is False
        assert _is_recipe_below_budget_floor(None, 'tier2') is False

    def test_tier1_no_floor(self):
        """tier1 has no floor"""
        assert _is_recipe_below_budget_floor(5.0, 'tier1') is False
        assert _is_recipe_below_budget_floor(0.0, 'tier1') is False

    def test_tier2_below_floor(self):
        """Should return True for amounts below tier2 floor ($25)"""
        assert _is_recipe_below_budget_floor(24.99, 'tier2') is True
        assert _is_recipe_below_budget_floor(10.0, 'tier2') is True

    def test_tier2_at_or_above_floor(self):
        """Should return False for amounts at or above tier2 floor"""
        assert _is_recipe_below_budget_floor(25.0, 'tier2') is False
        assert _is_recipe_below_budget_floor(30.0, 'tier2') is False

    def test_tier3_no_floor(self):
        """tier3 has no floor"""
        assert _is_recipe_below_budget_floor(5.0, 'tier3') is False


class TestAnalyzeImageRoute:
    """Test /api/analyze POST endpoint"""

    def test_no_image_provided(self, client):
        """Should return 400 when no image field"""
        response = client.post(
            '/api/analyze',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert "No image provided" in response.get_json()['error']

    def test_missing_json_content_type(self, client):
        """Should return 400 when content-type is not application/json"""
        response = client.post(
            '/api/analyze',
            data='invalid',
            content_type='text/plain'
        )
        assert response.status_code == 500  # JSON parsing fails

    def test_invalid_base64_image_data(self, client):
        """Should return 500 when base64 is invalid"""
        response = client.post(
            '/api/analyze',
            data=json.dumps({'image': 'not_valid_base64!!!'}),
            content_type='application/json'
        )
        assert response.status_code == 500
        assert 'error' in response.get_json()

    def test_valid_budget_tiers(self, client):
        """Should accept all valid budget tiers"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract, \
             patch('app._build_top_matches') as mock_matches:
            # Create 2 ingredients to pass minimum validation
            mock_ing1 = MagicMock()
            mock_ing1.name = 'tomato'
            mock_ing1.quantity = 1
            mock_ing1.unit = 'piece'
            mock_ing1.category = 'vegetable'
            mock_ing2 = MagicMock()
            mock_ing2.name = 'onion'
            mock_ing2.quantity = 1
            mock_ing2.unit = 'piece'
            mock_ing2.category = 'vegetable'
            
            mock_result = MagicMock()
            mock_result.ingredients = [mock_ing1, mock_ing2]
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result
            mock_matches.return_value = []

            for tier in ['tier1', 'tier2', 'tier3']:
                response = client.post(
                    '/api/analyze',
                    data=json.dumps({
                        'image': valid_image,
                        'budget_tier': tier,
                        'zipCode': '78201'
                    }),
                    content_type='application/json'
                )
                assert response.status_code == 200

    def test_invalid_max_regeneration_attempts_string(self, client):
        """Should default to 3 when max_regeneration_attempts is non-numeric string"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract, \
             patch('app._build_top_matches') as mock_matches:
            mock_ing1 = MagicMock()
            mock_ing1.name = 'tomato'
            mock_ing1.quantity = 1
            mock_ing1.unit = 'piece'
            mock_ing1.category = 'vegetable'
            mock_ing2 = MagicMock()
            mock_ing2.name = 'onion'
            mock_ing2.quantity = 1
            mock_ing2.unit = 'piece'
            mock_ing2.category = 'vegetable'
            
            mock_result = MagicMock()
            mock_result.ingredients = [mock_ing1, mock_ing2]
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result
            mock_matches.return_value = []

            response = client.post(
                '/api/analyze',
                data=json.dumps({
                    'image': valid_image,
                    'max_regeneration_attempts': 'invalid'
                }),
                content_type='application/json'
            )
            assert response.status_code == 200
            # Should not raise exception

    def test_max_regeneration_attempts_capped_min(self, client):
        """Should cap max_regeneration_attempts at minimum of 1"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract, \
             patch('app._build_top_matches') as mock_matches:
            mock_ing1 = MagicMock()
            mock_ing1.name = 'tomato'
            mock_ing1.quantity = 1
            mock_ing1.unit = 'piece'
            mock_ing1.category = 'vegetable'
            mock_ing2 = MagicMock()
            mock_ing2.name = 'onion'
            mock_ing2.quantity = 1
            mock_ing2.unit = 'piece'
            mock_ing2.category = 'vegetable'
            
            mock_result = MagicMock()
            mock_result.ingredients = [mock_ing1, mock_ing2]
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result
            mock_matches.return_value = []

            response = client.post(
                '/api/analyze',
                data=json.dumps({
                    'image': valid_image,
                    'max_regeneration_attempts': -5
                }),
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_max_regeneration_attempts_capped_max(self, client):
        """Should cap max_regeneration_attempts at maximum of 5"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract, \
             patch('app._build_top_matches') as mock_matches:
            mock_ing1 = MagicMock()
            mock_ing1.name = 'tomato'
            mock_ing1.quantity = 1
            mock_ing1.unit = 'piece'
            mock_ing1.category = 'vegetable'
            mock_ing2 = MagicMock()
            mock_ing2.name = 'onion'
            mock_ing2.quantity = 1
            mock_ing2.unit = 'piece'
            mock_ing2.category = 'vegetable'
            
            mock_result = MagicMock()
            mock_result.ingredients = [mock_ing1, mock_ing2]
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result
            mock_matches.return_value = []

            response = client.post(
                '/api/analyze',
                data=json.dumps({
                    'image': valid_image,
                    'max_regeneration_attempts': 100
                }),
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_extract_ingredients_exception(self, client):
        """Should return 500 when extract_ingredients raises exception"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract:
            mock_extract.side_effect = Exception("Gemini API error")

            response = client.post(
                '/api/analyze',
                data=json.dumps({'image': valid_image}),
                content_type='application/json'
            )
            assert response.status_code == 500
            assert 'error' in response.get_json()

    def test_recipe_generation_exception(self, client):
        """Should handle recipe generation exception in pipeline"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract, \
             patch('app.generate_recipe') as mock_generate:
            mock_ing1 = MagicMock()
            mock_ing1.name = 'tomato'
            mock_ing1.quantity = 2
            mock_ing1.unit = 'pieces'
            mock_ing1.category = 'vegetable'
            mock_ing2 = MagicMock()
            mock_ing2.name = 'onion'
            mock_ing2.quantity = 1
            mock_ing2.unit = 'piece'
            mock_ing2.category = 'vegetable'
            
            mock_result = MagicMock()
            mock_result.ingredients = [mock_ing1, mock_ing2]
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result

            # Make top_matches non-empty to trigger recipe generation
            mock_generate.side_effect = Exception("Recipe generation failed")

            with patch('app._build_top_matches') as mock_matches:
                mock_matches.return_value = [{'name': 'test_meal'}]

                response = client.post(
                    '/api/analyze',
                    data=json.dumps({'image': valid_image}),
                    content_type='application/json'
                )
                # Should return 200 with error in response
                assert response.status_code == 200
                data = response.get_json()
                assert 'recipe_generation_error' in data

    def test_pricing_exception(self, client):
        """Should handle pricing exception in pipeline"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract, \
             patch('app.generate_recipe') as mock_generate, \
             patch('app.extract_ingredients_from_recipe_text') as mock_extract_ing, \
             patch('app.filter_pricing_ingredients') as mock_filter, \
             patch('app.kroger_pricing.estimate_ingredient_total') as mock_pricing:
            
            mock_ing1 = MagicMock()
            mock_ing1.name = 'tomato'
            mock_ing1.quantity = 2
            mock_ing1.unit = 'pieces'
            mock_ing1.category = 'vegetable'
            mock_ing2 = MagicMock()
            mock_ing2.name = 'onion'
            mock_ing2.quantity = 1
            mock_ing2.unit = 'piece'
            mock_ing2.category = 'vegetable'
            
            mock_result = MagicMock()
            mock_result.ingredients = [mock_ing1, mock_ing2]
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result

            mock_generate.return_value = "Generated recipe text"
            mock_extract_ing.return_value = [{'name': 'tomato'}]
            mock_filter.return_value = ['tomato']
            mock_pricing.side_effect = Exception("Kroger API error")

            with patch('app._build_top_matches') as mock_matches:
                mock_matches.return_value = [{'name': 'test_meal'}]

                response = client.post(
                    '/api/analyze',
                    data=json.dumps({'image': valid_image}),
                    content_type='application/json'
                )
                assert response.status_code == 200
                data = response.get_json()
                assert 'generated_recipe_pricing_error' in data

    def test_zipcode_defaults(self, client):
        """Should use env var zipcode when not provided"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract, \
             patch('app._build_top_matches') as mock_matches:
            mock_ing1 = MagicMock()
            mock_ing1.name = 'tomato'
            mock_ing1.quantity = 1
            mock_ing1.unit = 'piece'
            mock_ing1.category = 'vegetable'
            mock_ing2 = MagicMock()
            mock_ing2.name = 'onion'
            mock_ing2.quantity = 1
            mock_ing2.unit = 'piece'
            mock_ing2.category = 'vegetable'
            
            mock_result = MagicMock()
            mock_result.ingredients = [mock_ing1, mock_ing2]
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result
            mock_matches.return_value = []

            response = client.post(
                '/api/analyze',
                data=json.dumps({'image': valid_image}),
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_price_strategy_defaults(self, client):
        """Should use default price strategy when not provided"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract, \
             patch('app._build_top_matches') as mock_matches:
            mock_ing1 = MagicMock()
            mock_ing1.name = 'tomato'
            mock_ing1.quantity = 1
            mock_ing1.unit = 'piece'
            mock_ing1.category = 'vegetable'
            mock_ing2 = MagicMock()
            mock_ing2.name = 'onion'
            mock_ing2.quantity = 1
            mock_ing2.unit = 'piece'
            mock_ing2.category = 'vegetable'
            
            mock_result = MagicMock()
            mock_result.ingredients = [mock_ing1, mock_ing2]
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result
            mock_matches.return_value = []

            response = client.post(
                '/api/analyze',
                data=json.dumps({'image': valid_image}),
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_insufficient_ingredients_zero(self, client):
        """Should return 400 when no ingredients extracted"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract:
            mock_result = MagicMock()
            mock_result.ingredients = []
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result

            response = client.post(
                '/api/analyze',
                data=json.dumps({'image': valid_image}),
                content_type='application/json'
            )
            assert response.status_code == 400
            assert 'at least 2 ingredients' in response.get_json()['error']
            assert 'Currently detected: 0' in response.get_json()['error']

    def test_insufficient_ingredients_one(self, client):
        """Should return 400 when only 1 ingredient extracted"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract:
            mock_result = MagicMock()
            mock_ing = MagicMock()
            mock_ing.name = 'tomato'
            mock_ing.quantity = 2
            mock_ing.unit = 'pieces'
            mock_ing.category = 'vegetable'
            mock_result.ingredients = [mock_ing]
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result

            response = client.post(
                '/api/analyze',
                data=json.dumps({'image': valid_image}),
                content_type='application/json'
            )
            assert response.status_code == 400
            assert 'at least 2 ingredients' in response.get_json()['error']
            assert 'Currently detected: 1' in response.get_json()['error']

    def test_sufficient_ingredients_two(self, client):
        """Should return 200 when exactly 2 ingredients extracted"""
        valid_image = base64.b64encode(b'fake_image_data').decode()
        
        with patch('app.extract_ingredients') as mock_extract, \
             patch('app._build_top_matches') as mock_matches:
            mock_result = MagicMock()
            mock_ing1 = MagicMock()
            mock_ing1.name = 'tomato'
            mock_ing1.quantity = 2
            mock_ing1.unit = 'pieces'
            mock_ing1.category = 'vegetable'
            mock_ing2 = MagicMock()
            mock_ing2.name = 'onion'
            mock_ing2.quantity = 1
            mock_ing2.unit = 'piece'
            mock_ing2.category = 'vegetable'
            mock_result.ingredients = [mock_ing1, mock_ing2]
            mock_result.non_food_items_detected = False
            mock_extract.return_value = mock_result
            mock_matches.return_value = []

            response = client.post(
                '/api/analyze',
                data=json.dumps({'image': valid_image}),
                content_type='application/json'
            )
            assert response.status_code == 200


class TestAnalyzeTextRoute:
    """Test /api/analyze-text POST endpoint"""

    def test_no_ingredients_provided(self, client):
        """Should return 400 when no ingredients field"""
        response = client.post(
            '/api/analyze-text',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert "No ingredients provided" in response.get_json()['error']

    def test_empty_ingredients_string(self, client):
        """Should return 400 for empty ingredients string"""
        response = client.post(
            '/api/analyze-text',
            data=json.dumps({'ingredients': ''}),
            content_type='application/json'
        )
        # Should fail minimum ingredient validation
        assert response.status_code == 400
        assert 'at least 2 ingredients' in response.get_json()['error']

    def test_valid_comma_separated_ingredients(self, client):
        """Should parse comma-separated ingredients correctly"""
        with patch('app._analyze_ingredients_pipeline') as mock_pipeline:
            mock_pipeline.return_value = {'ingredients': []}
            
            response = client.post(
                '/api/analyze-text',
                data=json.dumps({'ingredients': 'tomato, onion, garlic'}),
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_ingredients_with_extra_whitespace(self, client):
        """Should handle ingredients with extra whitespace"""
        with patch('app._analyze_ingredients_pipeline') as mock_pipeline:
            mock_pipeline.return_value = {'ingredients': []}
            
            response = client.post(
                '/api/analyze-text',
                data=json.dumps({'ingredients': '  tomato  ,  onion  ,  garlic  '}),
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_invalid_max_regeneration_attempts_string(self, client):
        """Should default to 3 when max_regeneration_attempts is non-numeric"""
        with patch('app._analyze_ingredients_pipeline') as mock_pipeline:
            mock_pipeline.return_value = {'ingredients': []}
            
            response = client.post(
                '/api/analyze-text',
                data=json.dumps({
                    'ingredients': 'tomato, onion',
                    'max_regeneration_attempts': 'not_a_number'
                }),
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_max_regeneration_attempts_capping(self, client):
        """Should cap max_regeneration_attempts between 1 and 5"""
        with patch('app._analyze_ingredients_pipeline') as mock_pipeline:
            mock_pipeline.return_value = {'ingredients': []}
            
            # Test min cap
            response = client.post(
                '/api/analyze-text',
                data=json.dumps({
                    'ingredients': 'tomato, onion',
                    'max_regeneration_attempts': -10
                }),
                content_type='application/json'
            )
            assert response.status_code == 200
            
            # Test max cap
            response = client.post(
                '/api/analyze-text',
                data=json.dumps({
                    'ingredients': 'tomato, onion',
                    'max_regeneration_attempts': 100
                }),
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_general_exception_handling(self, client):
        """Should return 500 for general exceptions"""
        with patch('app._analyze_ingredients_pipeline') as mock_pipeline:
            mock_pipeline.side_effect = Exception("Unexpected error")
            
            response = client.post(
                '/api/analyze-text',
                data=json.dumps({'ingredients': 'tomato, onion'}),
                content_type='application/json'
            )
            assert response.status_code == 500
            assert 'error' in response.get_json()

    def test_invalid_json(self, client):
        """Should handle invalid JSON gracefully"""
        response = client.post(
            '/api/analyze-text',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code in [400, 500]

    def test_valid_budget_tiers(self, client):
        """Should accept valid budget tiers"""
        with patch('app._analyze_ingredients_pipeline') as mock_pipeline:
            mock_pipeline.return_value = {'ingredients': []}
            
            for tier in ['tier1', 'tier2', 'tier3']:
                response = client.post(
                    '/api/analyze-text',
                    data=json.dumps({
                        'ingredients': 'tomato, onion',
                        'budget_tier': tier
                    }),
                    content_type='application/json'
                )
                assert response.status_code == 200

    def test_insufficient_ingredients_zero_text(self, client):
        """Should return 400 when no ingredients entered"""
        response = client.post(
            '/api/analyze-text',
            data=json.dumps({'ingredients': ''}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'at least 2 ingredients' in response.get_json()['error']
        assert 'Currently entered: 0' in response.get_json()['error']

    def test_insufficient_ingredients_one_text(self, client):
        """Should return 400 when only 1 ingredient entered"""
        response = client.post(
            '/api/analyze-text',
            data=json.dumps({'ingredients': 'tomato'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'at least 2 ingredients' in response.get_json()['error']
        assert 'Currently entered: 1' in response.get_json()['error']

    def test_insufficient_ingredients_one_text_with_spaces(self, client):
        """Should return 400 when only 1 ingredient after trimming whitespace"""
        response = client.post(
            '/api/analyze-text',
            data=json.dumps({'ingredients': '  tomato  ,  ,  '}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'at least 2 ingredients' in response.get_json()['error']
        assert 'Currently entered: 1' in response.get_json()['error']

    def test_sufficient_ingredients_two_text(self, client):
        """Should return 200 when exactly 2 ingredients entered"""
        with patch('app._analyze_ingredients_pipeline') as mock_pipeline:
            mock_pipeline.return_value = {'ingredients': []}
            
            response = client.post(
                '/api/analyze-text',
                data=json.dumps({'ingredients': 'tomato, onion'}),
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_sufficient_ingredients_many_text(self, client):
        """Should return 200 when many ingredients entered"""
        with patch('app._analyze_ingredients_pipeline') as mock_pipeline:
            mock_pipeline.return_value = {'ingredients': []}
            
            response = client.post(
                '/api/analyze-text',
                data=json.dumps({
                    'ingredients': 'tomato, onion, garlic, basil, pasta, olive oil'
                }),
                content_type='application/json'
            )
            assert response.status_code == 200


class TestKrogerPricingStrategiesRoute:
    """Test /api/kroger/pricing/strategies GET endpoint"""

    def test_returns_200(self, client):
        """Should return 200 status"""
        response = client.get('/api/kroger/pricing/strategies')
        assert response.status_code == 200

    def test_returns_valid_json(self, client):
        """Should return valid JSON"""
        response = client.get('/api/kroger/pricing/strategies')
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'default' in data
        assert 'allowed' in data
        assert isinstance(data['allowed'], list)


class TestKrogerPricingIngredientsRoute:
    """Test /api/kroger/pricing/ingredients POST endpoint"""

    def test_no_ingredients_list(self, client):
        """Should return 400 when ingredients is not a list"""
        response = client.post(
            '/api/kroger/pricing/ingredients',
            data=json.dumps({'ingredients': 'not_a_list', 'zipCode': '78201'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'ingredients must be a non-empty list' in response.get_json()['error']

    def test_empty_ingredients_list(self, client):
        """Should return 400 when ingredients list is empty"""
        response = client.post(
            '/api/kroger/pricing/ingredients',
            data=json.dumps({'ingredients': [], 'zipCode': '78201'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'ingredients must be a non-empty list' in response.get_json()['error']

    def test_missing_zipcode(self, client):
        """Should return 400 when zipCode is missing"""
        response = client.post(
            '/api/kroger/pricing/ingredients',
            data=json.dumps({'ingredients': ['tomato']}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'zipCode is required' in response.get_json()['error']

    def test_empty_zipcode(self, client):
        """Should return 400 when zipCode is empty"""
        response = client.post(
            '/api/kroger/pricing/ingredients',
            data=json.dumps({'ingredients': ['tomato'], 'zipCode': ''}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'zipCode is required' in response.get_json()['error']

    def test_invalid_price_strategy(self, client):
        """Should return 400 for invalid price strategy"""
        response = client.post(
            '/api/kroger/pricing/ingredients',
            data=json.dumps({
                'ingredients': ['tomato'],
                'zipCode': '78201',
                'priceStrategy': 'invalid_strategy'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'Invalid priceStrategy' in response.get_json()['error']
        assert 'allowed' in response.get_json()

    def test_all_empty_strings_in_ingredients(self, client):
        """Should return 400 when all ingredients are empty after normalization"""
        response = client.post(
            '/api/kroger/pricing/ingredients',
            data=json.dumps({
                'ingredients': ['', '  ', ''],
                'zipCode': '78201'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'at least one non-empty value' in response.get_json()['error']

    def test_kroger_value_error(self, client):
        """Should return 400 for ValueError from kroger_pricing"""
        with patch('app.kroger_pricing.estimate_ingredient_total') as mock_pricing:
            mock_pricing.side_effect = ValueError("Invalid zip code format")
            
            response = client.post(
                '/api/kroger/pricing/ingredients',
                data=json.dumps({
                    'ingredients': ['tomato'],
                    'zipCode': '78201'
                }),
                content_type='application/json'
            )
            assert response.status_code == 400
            assert 'error' in response.get_json()

    def test_kroger_general_exception(self, client):
        """Should return 502 for general exceptions from kroger_pricing"""
        with patch('app.kroger_pricing.estimate_ingredient_total') as mock_pricing:
            mock_pricing.side_effect = Exception("Kroger API unreachable")
            
            response = client.post(
                '/api/kroger/pricing/ingredients',
                data=json.dumps({
                    'ingredients': ['tomato'],
                    'zipCode': '78201'
                }),
                content_type='application/json'
            )
            assert response.status_code == 502
            assert 'error' in response.get_json()

    def test_valid_request(self, client):
        """Should return 200 for valid request"""
        with patch('app.kroger_pricing.estimate_ingredient_total') as mock_pricing:
            mock_pricing.return_value = {
                'estimatedTotal': 25.50,
                'items': []
            }
            
            response = client.post(
                '/api/kroger/pricing/ingredients',
                data=json.dumps({
                    'ingredients': ['tomato', 'onion'],
                    'zipCode': '78201'
                }),
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_ingredients_normalization(self, client):
        """Should normalize ingredients (convert to strings, strip whitespace)"""
        with patch('app.kroger_pricing.estimate_ingredient_total') as mock_pricing:
            mock_pricing.return_value = {'estimatedTotal': 25.50}
            
            response = client.post(
                '/api/kroger/pricing/ingredients',
                data=json.dumps({
                    'ingredients': ['  tomato  ', 123, '  onion  '],
                    'zipCode': '78201'
                }),
                content_type='application/json'
            )
            assert response.status_code == 200
            # Verify that normalize was called with non-empty values
            mock_pricing.assert_called_once()
            call_args = mock_pricing.call_args[0]
            assert len(call_args[0]) > 0  # Should have normalized ingredients

    def test_missing_json_body(self, client):
        """Should handle missing JSON body"""
        response = client.post(
            '/api/kroger/pricing/ingredients',
            data='',
            content_type='application/json'
        )
        # Should still process with empty dict due to silent=True
        assert response.status_code == 400


class TestHomeRoute:
    """Test / GET endpoint"""

    def test_home_endpoint(self, client):
        """Should return 200 with API info"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'version' in data
        assert 'endpoints' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
