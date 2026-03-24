from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    shop_id:Optional[str] = None
    product_name:str
    product_description: Optional[str] = None
    product_price:int
    product_sold:Optional[bool] = False
    product_review_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id:int
    
    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    shop_id: Optional[str] = None
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    product_price: Optional[int] = None
    product_sold: Optional[bool] = False
    product_review_id: Optional[int] = None


