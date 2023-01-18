# update LockServer_pb2_grpc.py
with open('E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs\LockServer_pb2_grpc.py', 'r', encoding='utf-8') as file:
    data = file.readlines()
  
data[4] = "import APIs.LockServer_pb2 as LockServer__pb2\n"
  
with open('E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs\LockServer_pb2_grpc.py', 'w', encoding='utf-8') as file:
    file.writelines(data)

# update TrackerServer_pb2_grpc.py
with open('E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs\TrackerServer_pb2_grpc.py', 'r', encoding='utf-8') as file:
    data = file.readlines()

data[4] = "import APIs.TrackerServer_pb2 as TrackerServer__pb2\n"

with open('E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs\TrackerServer_pb2_grpc.py', 'w', encoding='utf-8') as file:
    file.writelines(data)

# update StorageServer_pb2_grpc.py
with open('E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs\StorageServer_pb2_grpc.py', 'r', encoding='utf-8') as file:
    data = file.readlines()

data[4] = "import APIs.StorageServer_pb2 as StorageServer__pb2\n"

with open('E:\Repositories\College\Homework\DistributedSystem\Final-Project\Distributed-File-System\generate\APIs\StorageServer_pb2_grpc.py', 'w', encoding='utf-8') as file:
    file.writelines(data)

