import pytest
from unittest.mock import MagicMock
from kpi_monitor import evaluate_kpi, load_config



def test_evaluate_kpi_green():
    assert evaluate_kpi(120, 100) == "GREEN"

def test_evaluate_kpi_yellow():
    assert evaluate_kpi(75, 100) == "YELLOW"

def test_evaluate_kpi_red():
    assert evaluate_kpi(50, 100) == "RED"



def test_load_config(monkeypatch):
    sample_config = {
        "monthly_revenue": 1000,
        "weekly_orders": 100,
        "aov_by_category": 50,
        "customer_retention": 40,
        "top_products": 20
    }

    def mock_open(*args, **kwargs):
        from io import StringIO
        return StringIO(str(sample_config).replace("'", '"'))

    monkeypatch.setattr("builtins.open", mock_open)

    cfg = load_config()
    assert cfg["monthly_revenue"] == 1000
    assert cfg["weekly_orders"] == 100
    assert cfg["aov_by_category"] == 50
    assert cfg["customer_retention"] == 40
    assert cfg["top_products"] == 20


def test_evaluate_kpi_with_mocked_kpi():
    mock_kpis = MagicMock()
    mock_kpis.__getitem__.side_effect = lambda key: {
        'monthly_revenue': [1200],
        'weekly_orders': [110],
        'aov_by_category': [60],
        'customer_retention': [50],
        'top_products': [30]
    }[key]

    
    assert evaluate_kpi(mock_kpis['monthly_revenue'][0], 1000) == "GREEN"
    assert evaluate_kpi(mock_kpis['weekly_orders'][0], 120) == "YELLOW"
    assert evaluate_kpi(mock_kpis['top_products'][0], 50) == "RED"