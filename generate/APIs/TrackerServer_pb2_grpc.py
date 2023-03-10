# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import APIs.TrackerServer_pb2 as TrackerServer__pb2


class TrackerServerStub(object):
    """tracker server inly provide the service of add user, delete user, add storage server, delete storage server, heartbeat, ask file operation, get file list, update file info, replicate, add storage server, delete file

    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.AddUser = channel.unary_unary(
                '/TrackerServer.TrackerServer/AddUser',
                request_serializer=TrackerServer__pb2.AddUserRequest.SerializeToString,
                response_deserializer=TrackerServer__pb2.AddUserResponse.FromString,
                )
        self.DeleteUser = channel.unary_unary(
                '/TrackerServer.TrackerServer/DeleteUser',
                request_serializer=TrackerServer__pb2.DeleteUserRequest.SerializeToString,
                response_deserializer=TrackerServer__pb2.DeleteUserResponse.FromString,
                )
        self.AddServer = channel.unary_unary(
                '/TrackerServer.TrackerServer/AddServer',
                request_serializer=TrackerServer__pb2.AddServerRequest.SerializeToString,
                response_deserializer=TrackerServer__pb2.AddServerResponse.FromString,
                )


class TrackerServerServicer(object):
    """tracker server inly provide the service of add user, delete user, add storage server, delete storage server, heartbeat, ask file operation, get file list, update file info, replicate, add storage server, delete file

    """

    def AddUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddServer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TrackerServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'AddUser': grpc.unary_unary_rpc_method_handler(
                    servicer.AddUser,
                    request_deserializer=TrackerServer__pb2.AddUserRequest.FromString,
                    response_serializer=TrackerServer__pb2.AddUserResponse.SerializeToString,
            ),
            'DeleteUser': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteUser,
                    request_deserializer=TrackerServer__pb2.DeleteUserRequest.FromString,
                    response_serializer=TrackerServer__pb2.DeleteUserResponse.SerializeToString,
            ),
            'AddServer': grpc.unary_unary_rpc_method_handler(
                    servicer.AddServer,
                    request_deserializer=TrackerServer__pb2.AddServerRequest.FromString,
                    response_serializer=TrackerServer__pb2.AddServerResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'TrackerServer.TrackerServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TrackerServer(object):
    """tracker server inly provide the service of add user, delete user, add storage server, delete storage server, heartbeat, ask file operation, get file list, update file info, replicate, add storage server, delete file

    """

    @staticmethod
    def AddUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TrackerServer.TrackerServer/AddUser',
            TrackerServer__pb2.AddUserRequest.SerializeToString,
            TrackerServer__pb2.AddUserResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TrackerServer.TrackerServer/DeleteUser',
            TrackerServer__pb2.DeleteUserRequest.SerializeToString,
            TrackerServer__pb2.DeleteUserResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddServer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TrackerServer.TrackerServer/AddServer',
            TrackerServer__pb2.AddServerRequest.SerializeToString,
            TrackerServer__pb2.AddServerResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
