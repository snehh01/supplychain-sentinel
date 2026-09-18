from datetime import date

from src.risk_engine import assess_risk


def test_risk_engine_is_bounded_and_actionable() -> None:
    decision = assess_risk(as_of_date=date(2024, 1, 1), probability=0.9, current_inventory=40, average_daily_demand=20, supplier_lead_time=8, demand_growth_rate=0.2)
    assert 0 <= decision.risk_score <= 100
    assert decision.risk_level in {"HIGH", "CRITICAL"}
    assert decision.units_required > 0
    assert "Expedite" in decision.recommended_action

