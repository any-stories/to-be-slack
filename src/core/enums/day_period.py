from enum import StrEnum

class DayPeriod(StrEnum):
    LATE_NIGHT = "late_night"
    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    EVENING = "evening"

    @classmethod
    def from_hour(cls, hour: int) -> "DayPeriod":
        if not 0 <= hour < 24:
            raise ValueError(f"Invalid hour: {hour}")
        if 0 <= hour < 5:
            return cls.LATE_NIGHT
        if hour < 7:
            return cls.DAWN
        if hour < 11:
            return cls.MORNING
        if hour < 13:
            return cls.NOON
        if hour < 17:
            return cls.AFTERNOON
        if hour < 19:
            return cls.DUSK
        return cls.EVENING
