import grpc
import test_pb2
import test_pb2_grpc

class testClient:
    def __init__(self) -> None:
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = test_pb2_grpc.TestServiceStub(self.channel)

    def TestMethod(self):
        request = test_pb2.TestRequest()
        return self.stub.TestMethod(request)

if __name__ == '__main__':
    client = testClient()
    print(client.TestMethod())
