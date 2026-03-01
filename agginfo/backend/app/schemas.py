from pydantic import BaseModel


class StatRecord(BaseModel):
    source: str
    theme: str
    label: str
    prefecture_code: str
    prefecture_name: str
    value: float
    unit: str
    year: int
