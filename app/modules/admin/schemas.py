from pydantic import BaseModel


class AdminAnalyticsResponse(BaseModel):
    users: int
    doctors: int
    patients: int
    consultations: int
    completed_consultations: int
    total_revenue: float