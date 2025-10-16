import datetime
from marshmallow import validate


class DateRangeYears(validate.Range):
    """Custom year-based date range validator."""
    def __init__(self, min, max, **kwargs):
        today = datetime.date.today()
        min_date = datetime.date(min, 1, 1)
        max_date = datetime.date(max, 12, 31)
        super().__init__(min=min_date, max=max_date, **kwargs)
