from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, field_serializer, field_validator
from uuid import UUID
from datetime import datetime


class ProductListingBase(BaseModel):
    source: str = Field(..., description="Marketplace source")
    run_id: Optional[UUID] = None
    price: Optional[float] = Field(None, ge=0)
    discount: Optional[int] = Field(None, ge=0, le=100)
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    url: HttpUrl = Field(..., description="Listing URL")
    image_url: Optional[HttpUrl] = None

    @field_serializer("url")
    def serialize_url(self, value: HttpUrl) -> str:
        return str(value)

    @field_serializer("image_url")
    def serialize_image_url(self, value: Optional[HttpUrl]) -> Optional[str]:
        return str(value) if value else None


class ProductListingCreate(ProductListingBase):
    product_id: UUID


class ProductListingUpdate(BaseModel):
    price: Optional[float] = Field(None, ge=0)
    discount: Optional[int] = Field(None, ge=0, le=100)
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    url: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None

    @field_serializer("url")
    def serialize_url(self, value: Optional[HttpUrl]) -> Optional[str]:
        return str(value) if value else None

    @field_serializer("image_url")
    def serialize_image_url(self, value: Optional[HttpUrl]) -> Optional[str]:
        return str(value) if value else None


class ProductListingResponse(ProductListingBase):
    id: UUID
    product_id: UUID
    scraped_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    model_number: str = Field(..., min_length=1)
    brand: Optional[str] = None
    series: Optional[str] = None
    processor: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    screen_size: Optional[str] = None
    graphic_processor: Optional[str] = None
    colour: Optional[str] = None

    @field_validator("model_number")
    @classmethod
    def validate_model_number(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Model number cannot be empty")
        return v.strip()


class ProductCreate(ProductBase):
    source: str = Field(..., description="Marketplace source")
    run_id: Optional[UUID] = None
    price: Optional[float] = Field(None, ge=0)
    discount: Optional[int] = Field(None, ge=0, le=100)
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    url: HttpUrl = Field(..., description="Listing URL")
    image_url: Optional[HttpUrl] = None

    @field_serializer("url")
    def serialize_url(self, value: HttpUrl) -> str:
        return str(value)

    @field_serializer("image_url")
    def serialize_image_url(self, value: Optional[HttpUrl]) -> Optional[str]:
        return str(value) if value else None


class ProductUpdate(BaseModel):
    model_number: Optional[str] = Field(None, min_length=1)
    brand: Optional[str] = None
    series: Optional[str] = None
    processor: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    screen_size: Optional[str] = None
    graphic_processor: Optional[str] = None
    colour: Optional[str] = None


class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductSummaryResponse(ProductBase):
    id: UUID
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sources: List[str] = Field(default_factory=list)
    image_url: Optional[HttpUrl] = None

    @field_serializer("image_url")
    def serialize_image_url(self, value: Optional[HttpUrl]) -> Optional[str]:
        return str(value) if value else None

    class Config:
        from_attributes = True


class AdminProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    product_details: List[ProductListingResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CompareRequest(BaseModel):
    product_ids: List[UUID] = Field(..., min_length=1)
