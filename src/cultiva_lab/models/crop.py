from dataclasses import dataclass
from datetime import datetime
from .daily_condition import DailyCondition


@dataclass
class Crop:
    """
    A crop class, that the user can use to create new crops.
    """

    id: str
    name: str
    user_id: str
    crop_type_id: str
    start_date: datetime
    last_sim_date: datetime
    conditions: list[DailyCondition]
    # List that will be filled
    # with DailyCondition objects per day
    active: bool
