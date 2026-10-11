import pytest
import numpy as np
from core.services import calculate_probability, generate_chart_base64, process_calculation


class TestCalculateProbability:
    """Tests for calculate_probability function"""

    def test_basic_calculation(self):
        """Test basic probability calculation"""
        prob = calculate_probability(mean=0, std_dev=1, target_x=0)
        assert 0.49 < prob < 0.51  # Should be ~0.5 for mean

    def test_negative_values(self):
        """Test calculation with negative values"""
        prob = calculate_probability(mean=-10, std_dev=2, target_x=-10)
        assert 0.49 < prob < 0.51

    def test_large_std_dev(self):
        """Test with large standard deviation"""
        prob = calculate_probability(mean=100, std_dev=50, target_x=100)
        assert 0.49 < prob < 0.51

    def test_target_below_mean(self):
        """Test when target is below mean"""
        prob = calculate_probability(mean=10, std_dev=2, target_x=5)
        assert 0 < prob < 0.5

    def test_target_above_mean(self):
        """Test when target is above mean"""
        prob = calculate_probability(mean=10, std_dev=2, target_x=15)
        assert 0.5 < prob < 1.0

    def test_zero_std_dev_raises_error(self):
        """Test that zero std_dev raises ValueError"""
        with pytest.raises(ValueError, match="Standard deviation must be greater than zero"):
            calculate_probability(mean=10, std_dev=0, target_x=10)

    def test_negative_std_dev_raises_error(self):
        """Test that negative std_dev raises ValueError"""
        with pytest.raises(ValueError, match="Standard deviation must be greater than zero"):
            calculate_probability(mean=10, std_dev=-1, target_x=10)

    def test_extreme_values(self):
        """Test with extreme values"""
        prob = calculate_probability(mean=1000000, std_dev=100000, target_x=1000000)
        assert 0.49 < prob < 0.51

    def test_very_small_std_dev(self):
        """Test with very small standard deviation"""
        prob = calculate_probability(mean=10, std_dev=0.001, target_x=10)
        assert 0.49 < prob < 0.51


class TestGenerateChartBase64:
    """Tests for generate_chart_base64 function"""

    def test_generates_base64_string(self):
        """Test that function returns a base64 string"""
        result = generate_chart_base64(mean=10, std_dev=2, target_x=12)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_base64_is_valid(self):
        """Test that returned string is valid base64"""
        import base64
        result = generate_chart_base64(mean=10, std_dev=2, target_x=12)
        try:
            decoded = base64.b64decode(result)
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Invalid base64 string: {e}")

    def test_different_parameters_produce_different_charts(self):
        """Test that different parameters produce different outputs"""
        chart1 = generate_chart_base64(mean=10, std_dev=2, target_x=12)
        chart2 = generate_chart_base64(mean=20, std_dev=5, target_x=25)
        assert chart1 != chart2

    def test_with_negative_values(self):
        """Test chart generation with negative values"""
        result = generate_chart_base64(mean=-10, std_dev=3, target_x=-5)
        assert isinstance(result, str)
        assert len(result) > 0


class TestProcessCalculation:
    """Tests for process_calculation function"""

    def test_returns_dict_with_required_keys(self):
        """Test that function returns dict with probability and chart_base64"""
        result = process_calculation(mean=10, std_dev=2, target_x=12)
        assert isinstance(result, dict)
        assert "probability" in result
        assert "chart_base64" in result

    def test_probability_value_is_float(self):
        """Test that probability is a float"""
        result = process_calculation(mean=10, std_dev=2, target_x=12)
        assert isinstance(result["probability"], float)

    def test_chart_base64_is_string(self):
        """Test that chart_base64 is a string"""
        result = process_calculation(mean=10, std_dev=2, target_x=12)
        assert isinstance(result["chart_base64"], str)

    def test_probability_in_valid_range(self):
        """Test that probability is between 0 and 1"""
        result = process_calculation(mean=10, std_dev=2, target_x=12)
        assert 0 <= result["probability"] <= 1

    def test_invalid_std_dev_propagates_error(self):
        """Test that invalid std_dev raises ValueError"""
        with pytest.raises(ValueError):
            process_calculation(mean=10, std_dev=0, target_x=12)

    def test_integration_with_extreme_values(self):
        """Test end-to-end with extreme values"""
        result = process_calculation(mean=1000, std_dev=100, target_x=1200)
        assert 0 <= result["probability"] <= 1
        assert len(result["chart_base64"]) > 0
