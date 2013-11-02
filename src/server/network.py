import ctypes

# Location of network DLL
cent = ctypes.CDLL("../network/cent.so")

# Functions to copy from DLL
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

# types
CENTCB = ctypes.CFUNCTYPE( ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p );

def my_callback_function( conn, data, ids ):
        fields = CentGetDataFromCent_Float( data );

# Set the server ip address and port here
server_handle = StartCentServer(b"0.0.0.0", 8553);
CentServerAddCB( server_handle, b"/*", CENTCB(my_callback_function), 44 );

# This is used to send a packet to the clients to update entity information
def update(entityType, name, data):
  ChangeValue( server_handle, CreateCent( b"/e/"+entityType+"/"+name+"/"+data.string() ), 1 );
  
# This is used to convert python datatypes to the network types we use
class data:
  def __init__(self, dataType, contents):
    self.dataType = dataType
    self.contents = contents
  def string(self):
    if self.dataType == "loc":  
      floats = ctypes.c_float * 3
      return bytes("loc")+bytes(0x80)+bytes(1)+bytes(12)+bytes(floats(*self.contents))

      
    

#Network system loadout:


#s = strike craft
#u = unmanned thing (i.e. missile)
#c = corvette ship


#i.e.

#s0/pvr  [posx posy posz velx vely velz rotW rotX rotY rotZ (all floats)]
#s0/pwr  [power (energy) (float)]
#s0/name [ship human-readable name (string)]
#u0/mod  [ship model] (string)
#c3/hull [remaining hull]
#c3/bang [posx posy posz size] (positions in global) size in meters  (Causes appearance of explosion)