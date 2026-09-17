# str-api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class LeaseFinancials(BaseModel):
    monthly_base_rent: float = Field(description="The starting monthly base rent amount in USD")
    security_deposit: float = Field(description="The total security deposit required")
    late_fee_percentage: Optional[float] = Field(None, description="The percentage fee charged for late payments, if specified")

class LeaseAnomaly(BaseModel):
    clause_title: str = Field(description="The title of the section where the anomaly was found")
    severity: str = Field(description="Severity classification: Low, Medium, or High")
    explanation: str = Field(description="Detailed explanation of why this clause deviates from standard legal practices or presents hidden risks")

class LeaseExtractionSchema(BaseModel):
    landlord_name: str = Field(description="The full legal name of the property owner/lessor")
    tenant_name: str = Field(description="The full legal name of the renter/lessee")
    commencement_date: str = Field(description="The official start date of the lease lease agreement (YYYY-MM-DD format prefered)")
    expiration_date: str = Field(description="The official termination date of the lease agreement")
    financial_details: LeaseFinancials = Field(description="Extracted financial definitions and fees")
    identified_anomalies: List[LeaseAnomaly] = Field(description="A comprehensive list of hidden risks, conflicting statements, or severe legal anomalies found in the text")