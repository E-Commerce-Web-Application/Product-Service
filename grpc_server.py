import grpc
from concurrent import futures
from handlers import ProductService
from app.generated.product import product_pb2_grpc

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Product gRPC Server running on port 50051...")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nShutting down gRPC server gracefully...")
        server.stop(0)

if __name__ == "__main__":
    serve()