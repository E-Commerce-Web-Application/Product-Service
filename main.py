import threading
import grpc
from concurrent import futures
from handlers import ProductService
from app.generated.product import product_pb2_grpc

from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
import models, schema
from database import engine, SessionLocal
from sqlalchemy.orm import Session


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def start_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC running on port 50051...")
    server.wait_for_termination()


@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_grpc_server)
    thread.daemon = True
    thread.start()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]



@app.post("/products/")
async def create_product(product: schema.ProductBase, db: db_dependency):
    db_product = models.Products(
        shop_id=product.shop_id,
        product_name=product.product_name,
        product_description=product.product_description,
        product_price=product.product_price,
        product_sold=product.product_sold,
        product_review_id=product.product_review_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products/{product_id}")
async def get_product(product_id: int, db: db_dependency):
    result = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='Product not found')
    return result


@app.get("/products/", response_model=List[schema.ProductResponse])
async def getall_products(db: db_dependency):
    result = db.query(models.Products).all()
    if not result:
        raise HTTPException(status_code=404, detail='No products found')
    return result


@app.patch("/products/{product_id}")
async def update_product(product_id: int, product: schema.ProductUpdate, db: db_dependency):
    db_product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.shop_id is not None:
        db_product.shop_id = product.shop_id
    if product.product_name is not None:
        db_product.product_name = product.product_name
    if product.product_description is not None:
        db_product.product_description = product.product_description
    if product.product_price is not None:
        db_product.product_price = product.product_price
    if product.product_sold is not None:
        db_product.product_sold = product.product_sold
    if product.product_review_id is not None:
        db_product.product_review_id = product.product_review_id

    db.commit()
    db.refresh(db_product)

    return {"product": db_product, "message": "Product updated"}


@app.delete('/products/{product_id}')
async def delete_product(product_id: int, db: db_dependency):
    db_product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail='Product not found')
    db.delete(db_product)
    db.commit()
    return {"message": "Product Deleted"}

@app.get("/products/shop/{shop_id}", response_model=List[schema.ProductResponse])
async def get_products_by_shop(shop_id: str, db: db_dependency):
    products = db.query(models.Products).filter(
        models.Products.shop_id == shop_id
    ).all()

    if not products:
        raise HTTPException(
            status_code=404,
            detail="No products found for this shop"
        )

    return products