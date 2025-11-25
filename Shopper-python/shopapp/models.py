from typing import List, Optional, Literal
from pydantic import BaseModel, Field

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
    marketplaces: List[Literal["amazon", "flipkart"]] = Field(
        default_factory=lambda: ["flipkart"]
    )
    must_have_features: List[str] = Field(default_factory=list)
    nice_to_have_features: List[str] = Field(default_factory=list)
    exclude_brands: List[str] = Field(default_factory=list)
    prefer_brands: List[str] = Field(default_factory=list)

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
