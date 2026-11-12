"""Request and response models for the loan API."""
from typing import Literal

from pydantic import BaseModel, Field


class LoanFeatures(BaseModel):
    amount_usd: int = Field(gt=0, le=8000)
    term_months: Literal[3, 6, 12, 18, 24]
    monthly_income_usd: float = Field(gt=0)
    previous_loans: int = Field(ge=0)
    late_payments: int = Field(ge=0)


class ApplicationCreate(LoanFeatures):
    borrower_id: int = Field(gt=0)


class Prediction(BaseModel):
    default_probability: float = Field(ge=0, le=1)
    risk_band: Literal["low", "medium", "high"]
    model_version: str


class Application(ApplicationCreate):
    id: int
    status: str
    prediction: Prediction
