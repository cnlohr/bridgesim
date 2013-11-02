import ctypes

cent = CDLL("../network/cent.so")
StartCentServer = cent.StartCentServer;
StartCentServer.restype = c_void_p;
CreateCent = cent.CreateCent;
CreateCent.restype = c_void_p;
ChangeValue = cent.ChangeValue;
ChangeValue.argtypes = [c_void_p, c_void_p, c_int]
CentServerAddCB = cent.CentServerAddCB;
CentServerAddCB.argtypes = [ c_void_p, c_char_p, c_void_p, c_void_p ];
CentGetDataFromCent_Float = cent.CentGetDataFromCent;
CentGetDataFromCent_Float.argtypes = [ c_void_p ];
CentGetDataFromCent_Float.restype = POINTER(c_float)

#types
CENTCB = CFUNCTYPE( c_void_p, c_void_p, c_void_p, c_void_p );

def my_callback_function( conn, data, ids ):
        fields = CentGetDataFromCent_Float( data );

server_handle = StartCentServer(b"0.0.0.0", 8553);
CentServerAddCB( server_handle, b"/*", CENTCB(my_callback_function), 44 );