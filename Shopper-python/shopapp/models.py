from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field

class ConversationMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ProductSearchPreferences(BaseModel):
    """
    Structured representation of what the user wants to buy.
    """
    query: str = Field(
        ...,
        description="Natural language description of the desired product.",
    )
    min_price: Optional[float] = Field(default=None)
    max_price: Optional[float] = Field(default=None)
    currency: str = Field(default="INR")
    min_rating: float = Field(default=0.0)
    marketplaces: List[str] = Field(default_factory=list)
    must_have_features: List[str] = Field(default_factory=list)
    nice_to_have_features: List[str] = Field(default_factory=list)
    exclude_brands: List[str] = Field(default_factory=list)
    prefer_brands: List[str] = Field(default_factory=list)

class AgentDecision(BaseModel):
    """
    The decision made by the agent after analyzing the conversation.
    """
    action: Literal["search", "ask"] = Field(
        ..., 
        description="The action to take: 'search' if enough info is present, 'ask' if clarifying questions are needed."
    )
    clarifying_questions: Optional[List[str]] = Field(
        default=None, 
        description="List of questions to ask the user if action is 'ask'."
    )
    search_params: Optional[ProductSearchPreferences] = Field(
        default=None, 
        description="Search parameters if action is 'search'."
    )
    reply_message: Optional[str] = Field(
        default=None,
        description="A conversational reply to the user."
    )
    is_comparison: bool = Field(
        default=False,
        description="True if the user is asking for a comparison between products."
    )

class Product(BaseModel):
    """
    Normalized product representation.
    """
    marketplace: str
    title: str
    url: str
    price: Optional[float] = None
    currency: str = "INR"
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    is_sponsored: bool = False
    thumbnail_url: Optional[str] = None
    primary_features: List[str] = Field(default_factory=list)
    delivery_info: Optional[str] = None
