import ctypes
import time

cent = ctypes.CDLL("../network/cent.so")

StartCentServer = cent.StartCentServer;
StartCentServer.restype = ctypes.c_void_p;
CreateCent = cent.CreateCent;
CreateCent.restype = ctypes.c_void_p;
ChangeValue = cent.ChangeValue;
ChangeValue.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
CentServerAddCB = cent.CentServerAddCB;
CentServerAddCB.argtypes = [ ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p ];
CentGetDataFromCent_Float = cent.CentGetDataFromCent;
CentGetDataFromCent_Float.argtypes = [ ctypes.c_void_p ];
CentGetDataFromCent_Float.restype = ctypes.POINTER(ctypes.c_float)

def my_callback_function( conn, data, ids ):
        fields = CentGetDataFromCent_Float( data );
        print (fields[0])
        print (fields[1])
        print (ids)

CENTCB = ctypes.CFUNCTYPE( ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p );
server_handle = StartCentServer(b"0.0.0.0", 8553);

gencallback = CENTCB(my_callback_function)
CentServerAddCB( server_handle, b"/*", gencallback, 44 )

#CentServerAddCB( server_handle, b"/*", CENTCB(my_callback_function), 44 )

compatBytes = bytes
try:
  bytes("foo")
except TypeError:
  def compatBytes(string):
    return bytes(string, 'ascii')

def update(dataName, dataList):
  floats = ctypes.c_float * len(dataList)
  ChangeValue(server_handle, CreateCent(compatBytes(dataName), 0x80, 1, 4*len(dataList), floats(*dataList)), 1)
