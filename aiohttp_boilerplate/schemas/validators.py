from marshmallow import validate
from marshmallow.exceptions import ValidationError


class DateRangeYears(validate.Validator):
    message_min = "Must be {min_op} {{min}}."
    message_max = "Must be {max_op} {{max}}."
    message_all = "Must be {min_op} {{min}} and {max_op} {{max}}."

    message_gte = "greater than or equal to"
    message_gt = "greater than"
    message_lte = "less than or equal to"
    message_lt = "less than"

    def __init__(
        self,
        min=None,
        max=None,
        *,
        min_inclusive: bool = True,
        max_inclusive: bool = True,
        error: str | None = None,
    ):
        self.min = min
        self.max = max
        self.error = error
        self.min_inclusive = min_inclusive
        self.max_inclusive = max_inclusive

        # interpolate messages based on bound inclusivity
        self.message_min = self.message_min.format(
            min_op=self.message_gte if self.min_inclusive else self.message_gt
        )
        self.message_max = self.message_max.format(
            max_op=self.message_lte if self.max_inclusive else self.message_lt
        )
        self.message_all = self.message_all.format(
            min_op=self.message_gte if self.min_inclusive else self.message_gt,
            max_op=self.message_lte if self.max_inclusive else self.message_lt,
        )

    def _repr_args(self) -> str:
        return "min={!r}, max={!r}, min_inclusive={!r}, max_inclusive={!r}".format(
            self.min, self.max, self.min_inclusive, self.max_inclusive
        )

    def _format_error(self, value: validate._T, message: str) -> str:
        return (self.error or message).format(input=value, min=self.min, max=self.max)

    def __call__(self, value: validate._T) -> validate._T:
        if self.min is not None and (
            value.year - self.min > 0 if self.min_inclusive else value.year - self.min >= 0
        ):
            message = self.message_min if self.max is None else self.message_all
            raise ValidationError(self._format_error(value, message))

        if self.max is not None and (
            value.year - self.max < 0 if self.max_inclusive else value.year - self.max <= 0
        ):
            message = self.message_max if self.min is None else self.message_all
            raise ValidationError(self._format_error(value, message))

        return value
