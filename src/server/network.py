import ctypes

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

CENTCB = ctypes.CFUNCTYPE( ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p );
server_handle = StartCentServer(b"0.0.0.0", 8553);

gencallback = CENTCB(my_callback_function)
CentServerAddCB( server_handle, b"/*", gencallback, 44 )

def update(entityType, name, data):
  ChangeValue( server_handle, CreateCent(data.type(), 0x80, 1, data.length(), data.string() ), 1 );
  
class data:
  def __init__(self, dataType, contents):
    self.dataType = dataType
    self.contents = contents
  def string(self):
    if self.dataType == "loc":  
      floats = ctypes.c_float * 3
      return floats(*self.contents)
  def type(self):
    if self.dataType == "loc":
      return b"/sta"
  def length(self):
    if self.dataType == "loc":
      return 12