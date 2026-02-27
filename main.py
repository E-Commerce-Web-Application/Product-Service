from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated,List
import models, schema
from database import engine, SessionLocal
from sqlalchemy.orm import Session


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/products/")
async def create_product(
    product: schema.ProductBase,db: db_dependency,
    ):
    
    db_product = models.Products(
        seller_id = product.seller_id,
        product_name = product.product_name,
        product_description = product.product_description,
        product_price = product.product_price,
        product_sold = product.product_sold
        
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/{product_id}")
async def get_product(product_id:int,db:db_dependency):
    result = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not result:
        raise HTTPException(status_code=404,detail='Product not found')
    return result

@app.get("/products/",response_model=List[schema.ProductResponse])
async def getall_products(db:db_dependency):
    result = db.query(models.Products).all()
    if not result:
        raise HTTPException(status_code=404,detail='No products found')
    return result

@app.patch("/products/{product_id}")
async def update_product(product_id: int,product: schema.ProductUpdate,db: db_dependency):
    
    db_product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    
    if product.product_name is not None:
        db_product.product_name = product.product_name
    if product.product_description is not None:
        db_product.product_description = product.product_description
    if product.product_price is not None:
        db_product.product_price = product.product_price
    if product.product_sold is not None:
        db_product.product_sold = product.product_sold

    db.commit()
    db.refresh(db_product)

    return {"product": db_product,"message": "Product updated"}

@app.delete('/products/{product_id}')
async def delete_product(product_id:int,db:db_dependency):
    db_product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404,detail='Product not found')
    db.delete(db_product)
    db.commit()
    return {"message": "Product Deleted"}
