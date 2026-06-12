from pydantic import BaseModel
from typing import Optional

class Category(BaseModel):
    category_id: int
    name: str

class Product(BaseModel):
    product_id: int
    name: str
    image: Optional[str]
    ratings: Optional[float]
    no_of_ratings: Optional[int]
    discount_price: Optional[float]
    actual_price: Optional[float]
    category_id: Optional[int]
    category_name: Optional[str]   # we'll JOIN this in

class PaginatedProducts(BaseModel):
    total: int
    page: int
    page_size: int
    products: list[Product]