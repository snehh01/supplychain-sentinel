"""Transparent risk scoring and deterministic replenishment recommendations."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class RiskDecision:
    risk_score: int
    risk_level: str
    days_until_stockout: float
    expected_stockout_date: str
    units_required: int
    urgency: str
    recommended_action: str


def assess_risk(
    *, as_of_date: date, probability: float, current_inventory: float,
    average_daily_demand: float, supplier_lead_time: float, demand_growth_rate: float,
) -> RiskDecision:
    demand = max(float(average_daily_demand), 0.1)
    days_remaining = max(float(current_inventory), 0) / demand
    probability_component = 60 * min(max(float(probability), 0), 1)
    inventory_component = 25 * max(0, 1 - min(days_remaining / 14, 1))
    lead_component = 10 * min(max((supplier_lead_time - days_remaining) / max(supplier_lead_time, 1), 0), 1)
    trend_component = 5 * min(max(float(demand_growth_rate), 0), 1)
    score = int(round(min(100, probability_component + inventory_component + lead_component + trend_component)))
    level = "CRITICAL" if score >= 75 else "HIGH" if score >= 50 else "MEDIUM" if score >= 25 else "LOW"
    urgency = "Immediate" if level == "CRITICAL" else "Within 24 hours" if level == "HIGH" else "Monitor this week" if level == "MEDIUM" else "Routine monitoring"
    stockout_date = as_of_date + timedelta(days=math.ceil(days_remaining))
    units_required = max(0, math.ceil(demand * (supplier_lead_time + 7) - current_inventory))
    if days_remaining < supplier_lead_time:
        action = (
            f"{level.title()} risk: inventory is expected to last about {days_remaining:.1f} days, "
            f"shorter than the {supplier_lead_time:.0f}-day supplier lead time. Expedite the open order "
            f"or reallocate stock, and replenish at least {units_required:,} units."
        )
    elif level in {"CRITICAL", "HIGH"}:
        action = f"{level.title()} risk: place or increase replenishment by at least {units_required:,} units and review demand daily."
    else:
        action = "Inventory coverage currently exceeds lead time. Continue routine monitoring and reorder-point review."
    return RiskDecision(score, level, round(days_remaining, 1), stockout_date.isoformat(), units_required, urgency, action)


def decision_as_dict(**kwargs: object) -> dict[str, object]:
    return asdict(assess_risk(**kwargs))

