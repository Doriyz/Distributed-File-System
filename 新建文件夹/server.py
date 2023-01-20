# test as server

import grpc
import test_pb2
import test_pb2_grpc
from concurrent import futures

class TestService(test_pb2_grpc.TestService):
    def __init__(self) -> None:
        pass

    def TestMethod(self, request, context):
        return test_pb2.TestResponse(status=1)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    test_pb2_grpc.add_TestServiceServicer_to_server(TestService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()