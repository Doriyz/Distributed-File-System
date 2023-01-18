# Client function
# 1. get command and pass it to tracker server
# 2. get the storage server info and file info from tracker server
# 3. pass command to lock server
# 4. get lock from lock server
# 5. get connection with storage server
# 5. operate file in local cache
# 6. update file in storage server and other storage servers
# 7. if write, update file info in tracker server
# 7. release lock

import socket
import os
from os.path import isfile, join
import time as tm
import sys
from datetime import datetime
from APIs.setting import *
from concurrent import futures

import grpc
import APIs.TrackerServer_pb2 as TS_pb2
import APIs.TrackerServer_pb2_grpc as TS_pb2_grpc
import APIs.LockServer_pb2 as LS_pb2
import APIs.LockServer_pb2_grpc as LS_pb2_grpc
import APIs.StorageServer_pb2 as SS_pb2
import APIs.StorageServer_pb2_grpc as SS_pb2_grpc
import shutil

debug = False

ROOT_PATH = "./DATA" # to be defined in run()
cache_PATH = "" # to be defined in run()

if not os.path.exists(ROOT_PATH):
    os.mkdir(ROOT_PATH)


class FileInfo():
    def __init__(self, file_name, file_path, group_id, update_time):    
        self.file_name = file_name
        self.file_path = file_path
        self.group_id = group_id
        self.update_time = update_time


def is_cache_hit(group_id, file_path, file_name, cache_info):
    for file_info in cache_info:
        if(file_info.group_id == group_id and file_info.file_path == file_path and file_info.file_name == file_name):
            return file_info.update_time
    return "0"

def update_file_in_cache(group_id, file_path, file_name, update_time, content , cache_info):
    for i in range(len(cache_info)):
        if(cache_info[i].group_id == group_id and cache_info[i].file_path == file_path and cache_info[i].file_name == file_name):
            cache_info[i].update_time = update_time
            # update file content
            if(content != ""):
                global ROOT_PATH, cache_PATH
                file = open(ROOT_PATH + cache_PATH + file_path + file_name, 'w')
                file.write(content)
                file.close()
            print(f'[INFO] Successfully update cached file')
            return
    # the file is not in cache, create it in cache and synchronize the update with storage server
    print(f'[INFO] The file is not in cache.')
    create_file_in_cache(group_id, file_path, file_name, content, update_time,  cache_info)

def delete_file_in_cache(group_id, file_path, file_name, cache_info):
    for i in range(len(cache_info)):
        if(cache_info[i].group_id == group_id and cache_info[i].file_path == file_path and cache_info[i].file_name == file_name):
            cache_info.pop(i)
            # delete in local cache
            global ROOT_PATH, cache_PATH
            os.remove(ROOT_PATH + cache_PATH + file_path + file_name)
            print(f'[INFO] Successfully delete cached file')
            return
    print(f'[INFO] Fail to delete cached file')

def create_file_in_cache(group_id, file_path, file_name, content, update_time, cache_info):
    # create file in local cache
    global ROOT_PATH, cache_PATH
    file = open(ROOT_PATH + cache_PATH + file_path + file_name, 'w')
    file.write(content)
    file.close()
    # update cache info
    cache_info.append(FileInfo(group_id=group_id, file_path=file_path, file_name=file_name, update_time=update_time))
    print(f'[INFO] Successfully create cached file')

# message AddACLRequest {
#     string filename = 1;
#     string path = 2;
#     int32 group_id = 3;
#     int32 user_id = 4;
#     bool is_read = 5;
#     bool is_write = 6;
#     bool is_delete = 7;
# }

# temp
def addACL(filename, path, group_id, user_id, is_read, is_write, is_delete):
    try:
        with grpc.insecure_channel(TrackerServer_IP + ':' + str(TrackerServer_PORT)) as channel:
            stub = TS_pb2_grpc.TrackerServerStub(channel)
            print(f'[INIT] Connecting to Tracker Server')
            response = stub.AddACL(TS_pb2.AddACLRequest(filename=filename, path=path, group_id=group_id, user_id=user_id, is_read=is_read, is_write=is_write, is_delete=is_delete))
            print(f'[INIT] Add ACL to file')
            print(f'[INIT] {response}')
    except Exception as e:
        print(f'[ERROR] {e}')



def run():
    global ROOT_PATH, cache_PATH
    # get the hostname and ip address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    if(debug):
        user_id = 1
    else:
        user_id = int(input("[INPUT] Please input your user id: "))
    ROOT_PATH = './DATA/Client' + str(user_id) + '/' # also the path for data
    cache_PATH = 'cache/' # actually should be hidden to user
    if os.path.exists(ROOT_PATH):
        shutil.rmtree(ROOT_PATH)
        print(f'[INIT] Remove the old client datat directory.')
        
    
    os.mkdir(ROOT_PATH)
    os.mkdir(ROOT_PATH + cache_PATH)
    print(f'[INIT] Client data directory is created.')


    cache_Info = [] # list of FileInfo

    # connect to tracker server
    try:
        with grpc.insecure_channel(TrackerServer_IP + ':' + str(TrackerServer_PORT)) as channel:
            stub = TS_pb2_grpc.TrackerServerStub(channel)
            print(f'[INIT] Connecting to Tracker Server successfully.')

            print("[INFO] Client is ready to serve.")
            print(f'[INPUT] You can input "help" if you need help.')
            # get command from user
            while True:
                command = input("[INPUT] Please input your command: ")
                if(command == 'exit'):
                    break
                if(command == 'help'):
                    # if file_path = "", just mark it as ' "" '
                    print(f'[HELP] <your command> --- <description>')
                    print(f'[HELP] list local --- list all files in local directory')
                    print(f'[HELP] list remote --- list all files in remote directory')
                    
                    print(f'[HELP] read <file_path> <file_name> <group_id> --- read the file in certain group')
                    print(f'[HELP] write <file_path> <file_name> <group_id> --- write the file in certain group')
                    print(f'[HELP] delete <file_path> <file_name> <group_id> --- delete the file in certain group')
                    print(f'[HELP] create <file_name> <group_id> --- create the file in certain group')

                    # to be realized
                    print(f'[HELP] download <file_path> <file_name> <group_id> --- download the file to local directory')
                    print(f'[HELP] upload <file_path> <file_name> <group_id> --- upload the file to remote directory')
                    print(f'[HELP] asl <user_id> <file_path> <file_name> <group_id> <read> <write> <delete> --- add access control list')

                    print(f'[HELP] help --- show help message')
                    print(f'[HELP] exit --- exit the client')
                    continue
                # get the file name and operation from command
                command_list = command.split()
                if(len(command_list) == 2):
                    target = command_list[1]
                    operation = command_list[0]
                    if(operation == 'list'):
                        if(target == 'local'):
                            if(len(os.listdir(ROOT_PATH)) == 0):
                                print(f'[INFO] ')
                            else:
                                print(f'[INFO] List all files in local directory:')
                                print(f'[INFO] ', end='')
                                for file in os.listdir(ROOT_PATH):
                                    if(isfile(join(ROOT_PATH, file))):
                                        print(file, end=' ')
                                print()
                            continue
                        if(target == 'remote'):
                            print(f'[INFO] List all files in remote directory:')
                            response = stub.GetFileList(TS_pb2.GetFileListRequest(operation = ""))
                            for group in response.groups:
                                print(f'[INFO] Group ' + str(group.group_id))
                                for file in group.files:
                                    print(f'[INFO] {file.file_path}: {file.file_name}')
                            if(len(response.groups) == 0):
                                print(f'[INFO]')
                            continue
                    
                if(len(command_list) == 4):
                    group_id = int(command_list[3])
                    file_name = command_list[2]
                    file_path = command_list[1]
                    operation = command_list[0]
                    if file_path == '""':
                        file_path = ''
                    if(operation == 'read' or operation == 'write' or operation == 'delete' or operation == 'create' or operation == 'download' or operation == 'upload'):
                        # get the storsage server info from tracker server
                        response = stub.AskFileOperation(TS_pb2.AskFileOperationRequest(filename=file_name, group_id=group_id, operation=operation, path = file_path))
                        if(response.status == 0):
                            print("[ERROR] Request op in tracker server failed.")
                            continue
                        ss_ip = response.ip
                        ss_port = response.port
                        update_time = response.time

                        lock_type = 1
                        if(operation == 'read'):
                            lock_type = 0

                        if(operation == 'create'):
                            # create the file
                            if os.path.exists(ROOT_PATH + file_name):
                                print(f'[ERROR] The file already exists in local.')
                                continue
                            with grpc.insecure_channel(ss_ip + ':' + str(ss_port)) as channel:  
                                storage_stub = SS_pb2_grpc.StorageServerStub(channel)
                                response = storage_stub.Create(SS_pb2.CreateRequest(filename=file_name, path = file_path, content = ""))
                                if(response.status == 1):
                                    print(f'[INFO] Successfully create the file in storage server.')
                                    response = stub.UpdateFileInfo(TS_pb2.UpdateFileInfoRequest(filename=file_name, filepath = file_path, group_id=group_id))
                                    if(response.status == 1):
                                        f = open(ROOT_PATH + file_name, 'w')
                                        f.close()
                                        update_time = response.time
                                        print(f'[INFO] Create file info in tracker server in {update_time}.')
                                        # create the cache
                                        content = ""
                                        create_file_in_cache(group_id, file_path, file_name, content,update_time, cache_Info)
                                        continue
                                    else:
                                        print(f'[ERROR] Fail in tracker server')
                                else:
                                    print(f'[ERROR] File has exist in storage server.')
                                continue

                        # get the lock from lock server
                        with grpc.insecure_channel(LockServer_IP + ':' + str(LockServer_PORT)) as channel:
                            lock_stub = LS_pb2_grpc.LockServerStub(channel)
                            response = lock_stub.Lock(LS_pb2.LockRequest(filename=file_name, path = file_path, group_id=group_id, user_id = int(user_id), lock_type = lock_type))
                            if(response.status == 0):
                                print("[ERROR] The file is locked.")
                                print(f'[INFO] Retry to lock the file in 5 seconds...')
                                tm.sleep(5)
                                response = lock_stub.Lock(LS_pb2.LockRequest(filename=file_name, path = file_path, group_id=group_id, user_id = user_id, lock_type = lock_type))
                                if(response.status == 0):
                                    print("[ERROR] The file is locked.")
                                    print(f'[INFO] Please try to lock the file later.')
                                    continue
                            print("[INFO] The file is locked successfully.")

                        # if read, cache hit and file is the latest, read from cache 
                        if operation == 'read':
                            time = is_cache_hit(group_id, file_path, file_name, update_time, cache_Info)
                            if time == update_time:
                                print(f'[INFO] cache hit.')
                                print(f'[INFO] Read the file from cache.')
                                with open(join(ROOT_PATH + file_path, file_name), 'r') as f:
                                    print(f.read())
                                continue
                            elif time == "":
                                print(f'[INFO] cache miss.')
                            else:
                                print(f'[INFO] cache hit.')
                                print(f'[INFO] The file is out of date.')
                                print(f'[INFO] Update the cache from storage server.')
                        # connect to storage server
                        with grpc.insecure_channel(ss_ip + ':' + str(ss_port)) as channel:  
                            storage_stub = SS_pb2_grpc.StorageServerStub(channel)
                            # read
                            if operation == 'read':
                                response = storage_stub.Read(SS_pb2.ReadRequest(filename=file_name, path = file_path))
                                if(response.status == 1):
                                    print(f'[INFO] Read the file {file_name} from storage server.')
                                    print(f'[READ] {response.content}')
                                    # update the cache
                                    if time != "":
                                        with open(join(ROOT_PATH + file_path, file_name), 'w') as f:
                                            f.write(response.content)
                                            update_file_in_cache(group_id, file_path, file_name, update_time, response.content, cache_Info)
                                else:
                                    print(f'[ERROR] Fail to read the file.')

                            elif operation == 'write':
                                content = input('[INFO] Please input the content you want to write:\n')
                                response = storage_stub.Write(SS_pb2.WriteRequest(filename=file_name, content=content, path = file_path, mode = 0))
                                if(response.status == 1):
                                    print(f'[INFO] Write the file to storage server.')
                                    # update in tracker server
                                    response = stub.UpdateFileInfo(TS_pb2.UpdateFileInfoRequest(filename=file_name, filepath = file_path, group_id=group_id))
                                    if(response.status == 1):
                                        print(f'[INFO] Successfully update file info in tracker server.')
                                        update_time = response.time
                                        # update the cache
                                        with open(join(ROOT_PATH + file_path, file_name), 'w') as f:
                                            f.write(content)
                                            update_file_in_cache(group_id, file_path, file_name, update_time, content, cache_Info)
                                    else:
                                        print(f'[ERROR] Fail to update file info in tracker server.')
                                else:
                                    print(f'[ERROR] Fail to write the file.')

                            elif operation == 'delete':
                                response = storage_stub.Delete(SS_pb2.DeleteRequest(filename=file_name, path = file_path, group_id = group_id))
                                if(response.status == 1):
                                    print(f'[INFO] Delete the file from storage server.')
                                    # delete the cache
                                    delete_file_in_cache(group_id, file_path, file_name, cache_Info)
                                    # delete in tracker server
                                    response = stub.DeleteFile(TS_pb2.DeleteFileRequest(filename=file_name, path = file_path, group_id=group_id))
                                    if(response.status == 1):
                                        print(f'[INFO] Successfully delete file info in tracker server.')
                                        continue
                                    else:
                                        print(f'[ERROR] Fail to delete file info in tracker server.')
                                else:
                                    print(f'[ERROR] Fail to delete the file.')
                                                      
                            else:
                                print(f'[ERROR] Invalid operation.')

                        # release the lock
                        with grpc.insecure_channel(LockServer_IP + ':' + str(LockServer_PORT)) as channel:
                            lock_stub = LS_pb2_grpc.LockServerStub(channel)
                            response = lock_stub.Unlock(LS_pb2.UnlockRequest(filename=file_name, path = file_path, group_id=group_id, user_id = user_id, lock_type = lock_type))
                            if(response.status == 1):
                                print("[INFO] Successfully release the lock.")
                            else:
                                print("[ERROR] Fail to release the lock.")
                        
                    else:
                        print("[ERROR] Invalid command.")
                else:
                    print(f'[ERROR] Invalid command.')
            
        print(f'[INFO] Exit the client.')

                
    except KeyboardInterrupt:
        print(f'[ERROR] Keyboard interrupt.')
        sys.exit(0)

if __name__ == '__main__':
    run()