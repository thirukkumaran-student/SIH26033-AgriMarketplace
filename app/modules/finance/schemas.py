from decimal import Decimal

from pydantic import BaseModel, Field


class FinancingRelationshipCreate(BaseModel):
    buyer_id: int
    financier_id: int
    credit_limit: Decimal = Field(gt=0)
    interest_rate: Decimal = Field(ge=0)
    tenure_days: int = Field(gt=0)


class FinancingRelationshipResponse(BaseModel):
    id: int
    buyer_id: int
    financier_id: int
    credit_limit: Decimal
    interest_rate: Decimal
    tenure_days: int
    status: str

    model_config = {"from_attributes": True}


class FinancingRequestCreate(BaseModel):
    financier_id: int


class FinancingRequestResponse(BaseModel):
    id: int
    buyer_id: int
    financier_id: int
    status: str
    credit_limit: Decimal
    interest_rate: Decimal
    tenure_days: int

    model_config = {"from_attributes": True}


class FinancingDecision(BaseModel):
    credit_limit: Decimal = Field(gt=0)
    interest_rate: Decimal = Field(ge=0)
    tenure_days: int = Field(gt=0)

class FinancingTransactionCreate(BaseModel):
    relationship_id: int
    order_id: int
    principal: Decimal = Field(gt=0)


class FinancingTransactionResponse(BaseModel):
    id: int
    relationship_id: int
    order_id: int
    principal: Decimal
    interest: Decimal
    total_repayment: Decimal
    status: str

    model_config = {"from_attributes": True}