# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: StorageServer.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13StorageServer.proto\"3\n\rCreateRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\x12\x11\n\tfile_name\x18\x02 \x01(\t\"-\n\x0e\x43reateResponse\x12\x0e\n\x06status\x18\x01 \x01(\x08\x12\x0b\n\x03msg\x18\x02 \x01(\t\"3\n\rDeleteRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\x12\x11\n\tfile_name\x18\x02 \x01(\t\"-\n\x0e\x44\x65leteResponse\x12\x0e\n\x06status\x18\x01 \x01(\x08\x12\x0b\n\x03msg\x18\x02 \x01(\t\"1\n\x0bReadRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\x12\x11\n\tfile_name\x18\x02 \x01(\t\"<\n\x0cReadResponse\x12\x0e\n\x06status\x18\x01 \x01(\x08\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\x12\x0b\n\x03msg\x18\x03 \x01(\t\"Q\n\x0cWriteRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\x12\x11\n\tfile_name\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\x12\x0c\n\x04mode\x18\x04 \x01(\x05\",\n\rWriteResponse\x12\x0e\n\x06status\x18\x01 \x01(\x08\x12\x0b\n\x03msg\x18\x02 \x01(\t\"\x1e\n\x0bListRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\"!\n\x0cListResponse\x12\x11\n\tfile_name\x18\x01 \x03(\t\"4\n\x0eGetTimeRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\x12\x11\n\tfile_name\x18\x02 \x01(\t\"$\n\x0fGetTimeResponse\x12\x11\n\tfile_time\x18\x01 \x01(\t2\x91\x02\n\rStorageServer\x12+\n\x06\x43reate\x12\x0e.CreateRequest\x1a\x0f.CreateResponse\"\x00\x12+\n\x06\x44\x65lete\x12\x0e.DeleteRequest\x1a\x0f.DeleteResponse\"\x00\x12%\n\x04Read\x12\x0c.ReadRequest\x1a\r.ReadResponse\"\x00\x12(\n\x05Write\x12\r.WriteRequest\x1a\x0e.WriteResponse\"\x00\x12%\n\x04List\x12\x0c.ListRequest\x1a\r.ListResponse\"\x00\x12.\n\x07GetTime\x12\x0f.GetTimeRequest\x1a\x10.GetTimeResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'StorageServer_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CREATEREQUEST._serialized_start=23
  _CREATEREQUEST._serialized_end=74
  _CREATERESPONSE._serialized_start=76
  _CREATERESPONSE._serialized_end=121
  _DELETEREQUEST._serialized_start=123
  _DELETEREQUEST._serialized_end=174
  _DELETERESPONSE._serialized_start=176
  _DELETERESPONSE._serialized_end=221
  _READREQUEST._serialized_start=223
  _READREQUEST._serialized_end=272
  _READRESPONSE._serialized_start=274
  _READRESPONSE._serialized_end=334
  _WRITEREQUEST._serialized_start=336
  _WRITEREQUEST._serialized_end=417
  _WRITERESPONSE._serialized_start=419
  _WRITERESPONSE._serialized_end=463
  _LISTREQUEST._serialized_start=465
  _LISTREQUEST._serialized_end=495
  _LISTRESPONSE._serialized_start=497
  _LISTRESPONSE._serialized_end=530
  _GETTIMEREQUEST._serialized_start=532
  _GETTIMEREQUEST._serialized_end=584
  _GETTIMERESPONSE._serialized_start=586
  _GETTIMERESPONSE._serialized_end=622
  _STORAGESERVER._serialized_start=625
  _STORAGESERVER._serialized_end=898
# @@protoc_insertion_point(module_scope)
