"""
A module for msg in the app schemas package.
"""
from pydantic import BaseModel, Field


class Msg(BaseModel):
    """
    Schema for representing a message.
    """
    msg: str = Field(..., title="Message", description="Message to display")

    class Config:
        """
        Config class for Msg.
        """
        schema_extra: dict[str, dict[str, str]] = {
            "example": {"msg": "Hello, World!!!"}}
