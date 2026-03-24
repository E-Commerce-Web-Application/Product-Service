import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.empty_pb2 import Empty

from app.generated.product import product_pb2
from app.generated.product import product_pb2_grpc

from datetime import datetime
from database import get_connection


class ProductService(product_pb2_grpc.ProductServiceServicer):


    def CreateProduct(self, request, context):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO products
            (shop_id, product_name, product_description, product_price, product_sold, product_review_id)
            VALUES (%s,%s,%s,%s,%s,%s)
            RETURNING id, product_date
        """, (
            request.shop_id,
            request.product_name,
            request.product_description,
            request.product_price,
            request.product_sold,
            request.product_review_id
    ))

        row = cursor.fetchone()
        conn.commit()

        cursor.close()
        conn.close()

        timestamp = Timestamp()
        timestamp.FromDatetime(row[1])

        return product_pb2.ProductResponse(
            id=str(row[0]),
            shop_id=request.shop_id,
            product_name=request.product_name,
            product_description=request.product_description,
            product_price=request.product_price,
            product_sold=request.product_sold,
            product_review_id=request.product_review_id,
            product_date=timestamp
    )

    def GetProduct(self, request, context):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id,shop_id,product_name,product_description,product_price,product_sold,product_date,product_review_id
            FROM products WHERE id=%s
        """, (request.product_id,))

        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return product_pb2.ProductResponse()

        timestamp = Timestamp()
        timestamp.FromDatetime(row[6])

        return product_pb2.ProductResponse(
            id=str(row[0]),
            shop_id=row[1],
            product_name=row[2],
            product_description=row[3],
            product_price=row[4],
            product_sold=row[5],
            product_review_id=row[7] if row[7] is not None else 0,
            product_date=timestamp
        )

    def GetAllProducts(self, request, context):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id,shop_id,product_name,product_description,product_price,product_sold,product_date,product_review_id
            FROM products
        """)

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        products = []

        for row in rows:
            timestamp = Timestamp()
            timestamp.FromDatetime(row[6])

            products.append(
                product_pb2.ProductResponse(
                    id=str(row[0]),
                    shop_id=row[1],
                    product_name=row[2],
                    product_description=row[3],
                    product_price=row[4],
                    product_sold=row[5],
                    product_review_id=row[7] if row[7] is not None else 0,
                    product_date=timestamp
                )
            )

        return product_pb2.ProductListResponse(products=products)

    def UpdateProduct(self, request, context):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE products
            SET shop_id=%s,
                product_name=%s,
                product_description=%s,
                product_price=%s,
                product_sold=%s,
                product_review_id=%s
            WHERE id=%s
            RETURNING id,shop_id,product_name,product_description,product_price,product_sold,product_date,product_review_id
        """, (
            request.shop_id,
            request.product_name,
            request.product_description,
            request.product_price,
            request.product_sold,
            request.product_review_id,
            request.product_id
        ))

        row = cursor.fetchone()
        conn.commit()

        cursor.close()
        conn.close()

        if not row:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return product_pb2.ProductUpdateResponse()

        timestamp = Timestamp()
        timestamp.FromDatetime(row[6])

        product = product_pb2.ProductResponse(
            id=str(row[0]),
            shop_id=row[1],
            product_name=row[2],
            product_description=row[3],
            product_price=row[4],
            product_sold=row[5],
            product_review_id=row[7] if row[7] is not None else 0,
            product_date=timestamp
        )

        return product_pb2.ProductUpdateResponse(
            product=product,
            message="Product updated successfully"
        )

    def DeleteProduct(self, request, context):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM products WHERE id=%s",
            (request.product_id,)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return product_pb2.DeleteResponse(
            message="Product deleted successfully"
        )
    

    def GetProductsFromShopID(self, request, context):
    
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, shop_id, product_name, product_description, product_price, product_sold, product_date, product_review_id
            FROM products
            WHERE shop_id = %s
        """, (request.shop_id,)) 

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("No products found for this shop")
            return product_pb2.ProductListResponse(products=[])

        products = []
        for row in rows:
            timestamp = Timestamp()
            timestamp.FromDatetime(row[6])

            products.append(
                product_pb2.ProductResponse(
                    id=str(row[0]),
                    shop_id=row[1],
                    product_name=row[2],
                    product_description=row[3],
                    product_price=row[4],
                    product_sold=row[5],
                    product_review_id=row[7] if row[7] is not None else 0,
                    product_date=timestamp
                )
            )

        return product_pb2.ProductListResponse(products=products)
    

    
    