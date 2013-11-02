from ctypes import *
import time
import math

# Load in functions
cent = CDLL("cent.so")
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
	print fields[0]
	print fields[1]
	print ids


server_handle = StartCentServer(b"0.0.0.0", 8553);
gencallback = CENTCB(my_callback_function); #Needs to be in global space to prevent garbage collection from hitting it.
CentServerAddCB( server_handle, b"/*", gencallback, 44 );


for x in range( 0, 100000 ):
	fields = c_float * 2;
	myvar = fields( x, math.sin(x) );
	ChangeValue( server_handle, CreateCent( b"/hi", 0x80, 1, 8, myvar ), 1 );
	time.sleep(.01);




