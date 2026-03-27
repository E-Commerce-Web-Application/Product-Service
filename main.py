# main.py
import threading
from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
import models, schema
from database import engine, SessionLocal

# Import gRPC server function
from grpc_server import serve as start_grpc_server

# --- FastAPI app ---
app = FastAPI(title="Product Service")

# --- Create all tables using the engine explicitly ---
models.Base.metadata.create_all(bind=engine)

# --- Start gRPC server in a background thread on FastAPI startup ---
@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_grpc_server)
    thread.daemon = True
    thread.start()
    print("gRPC server thread started!")

# --- Database dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]



@app.post("/products/", response_model=schema.ProductResponse)
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

@app.get("/products/{product_id}", response_model=schema.ProductResponse)
async def get_product(product_id: int, db: db_dependency):
    product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/products/", response_model=List[schema.ProductResponse])
async def get_all_products(db: db_dependency):
    products = db.query(models.Products).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    return products

@app.patch("/products/{product_id}", response_model=schema.ProductResponse)
async def update_product(product_id: int, product: schema.ProductUpdate, db: db_dependency):
    db_product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update fields dynamically
    for field, value in product.dict(exclude_unset=True).items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: db_dependency):
    db_product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}

@app.get("/products/shop/{shop_id}", response_model=List[schema.ProductResponse])
async def get_products_by_shop(shop_id: str, db: db_dependency):
    products = db.query(models.Products).filter(models.Products.shop_id == shop_id).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this shop")
    return products