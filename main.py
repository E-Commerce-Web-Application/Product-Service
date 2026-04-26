# main.py
import threading
from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.middleware.cors import CORSMiddleware
import models, schema
from database import engine, SessionLocal, DATABASE_HOST
from constants import PRODUCT_NOT_FOUND, PRODUCT_NOT_FOUND_RESPONSES

# Import gRPC server function
from grpc_server import serve as start_grpc_server

# --- FastAPI app ---
app = FastAPI(title="Product Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/products/health")
async def health():
    return {"message": "Product service is running"}

# --- Start gRPC server in a background thread on FastAPI startup ---
@app.on_event("startup")
def startup_event():
    try:
        models.Base.metadata.create_all(bind=engine)
        print(f"Product tables are ready on database host: {DATABASE_HOST}")
    except SQLAlchemyError as exc:
        # Keep REST API alive so clients receive a proper HTTP error
        # instead of a browser-level "Network Error".
        print(f"Database initialization failed: {exc}")

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
    try:
        db_product = models.Products(
            shop_id=product.shop_id,
            product_name=product.product_name,
            product_description=product.product_description,
            product_price=product.product_price,
            product_sold=product.product_sold,
            product_review_id=product.product_review_id,
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create product in database ({DATABASE_HOST}): {exc}",
        )

@app.get(
    "/products/{product_id}",
    response_model=schema.ProductResponse,
    responses=PRODUCT_NOT_FOUND_RESPONSES,
)
async def get_product(product_id: int, db: db_dependency):
    product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=PRODUCT_NOT_FOUND)
    return product

@app.get(
    "/products/",
    response_model=List[schema.ProductResponse],
    responses=PRODUCT_NOT_FOUND_RESPONSES,
)
async def get_all_products(db: db_dependency):
    products = db.query(models.Products).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    return products

@app.patch(
    "/products/{product_id}",
    response_model=schema.ProductResponse,
    responses=PRODUCT_NOT_FOUND_RESPONSES,
)
async def update_product(product_id: int, product: schema.ProductUpdate, db: db_dependency):
    db_product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail=PRODUCT_NOT_FOUND)

    # Update fields dynamically
    for field, value in product.dict(exclude_unset=True).items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", responses=PRODUCT_NOT_FOUND_RESPONSES)
async def delete_product(product_id: int, db: db_dependency):
    db_product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail=PRODUCT_NOT_FOUND)
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}

@app.get(
    "/products/shop/{shop_id}",
    response_model=List[schema.ProductResponse],
    responses=PRODUCT_NOT_FOUND_RESPONSES,
)
async def get_products_by_shop(shop_id: str, db: db_dependency):
    products = db.query(models.Products).filter(models.Products.shop_id == shop_id).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this shop")
    return products
