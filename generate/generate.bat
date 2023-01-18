@echo off
title Generate gRPC Python Code


python -m grpc_tools.protoc --proto_path=E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs/TrackerServer.proto --python_out=E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs --grpc_python_out=E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs

python -m grpc_tools.protoc --proto_path=E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs/StorageServer.proto --python_out=E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs --grpc_python_out=E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs

python -m grpc_tools.protoc --proto_path=E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs/LockServer.proto --python_out=E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs --grpc_python_out=E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs

echo Successfully generated gRPC Python code

python E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\update.py

echo Successfully updated gRPC Python code

echo A | xcopy "E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs" "E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\Client\APIs"

echo A | xcopy "E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs" "E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\LockServer\APIs"

echo A | xcopy "E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs" "E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\LockServer\APIs"

echo A | xcopy "E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs" "E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\LockServer\APIs"

echo copy API files

echo Done

exit