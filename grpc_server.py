import os
import grpc
from concurrent import futures
from handlers import ProductService
from app.generated.product import product_pb2_grpc

def serve():

    GRPC_PORT = os.getenv("GRPC_SERVER_PORT", "50050")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)

    server.add_insecure_port(f'[::]:{GRPC_PORT}')
    server.start()
    print(f"Product gRPC Server running on port {GRPC_PORT}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nShutting down gRPC server gracefully...")
        server.stop(0)

if __name__ == "__main__":
    serve()