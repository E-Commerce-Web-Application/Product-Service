from sqlalchemy import Boolean, Column,Integer,String,DateTime
from sqlalchemy.sql import func
from database import Base


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True,index=True)
    seller_id = Column(String)
    product_name = Column(String,nullable=False)
    product_description = Column(String,nullable=True)
    product_price = Column(Integer,nullable=False)
    product_sold = Column(Boolean,default=False)
    product_date = Column(DateTime(timezone=True),server_default=func.now())
    
