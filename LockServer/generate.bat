python -m grpc_tools.protoc --proto_path=./APIs ./APIs/TrackerServer.proto --python_out=./APIs --grpc_python_out=./APIs

python -m grpc_tools.protoc --proto_path=./APIs ./APIs/StorageServer.proto --python_out=./APIs --grpc_python_out=./APIs

python -m grpc_tools.protoc --proto_path=./APIs ./APIs/LockServer.proto --python_out=./APIs --grpc_python_out=./APIs