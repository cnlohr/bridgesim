all : test test32.exe

CFLAGS:=-O0 -g -I../util
CFLAGSWIN32:=$(CFLAGS)  -Ifreeglut  -m32  -Iglew -DGLEW_STATIC -I../util
#include "graphicscore.h"

LINLDFLAGS:=-lGL -lglut -lGLU -lGLEW -lm -lpthread -lpng -ljpeg
WINLDFLAGS32:=\
	/usr/i586-mingw32msvc/lib/libopengl32.a \
	/usr/i586-mingw32msvc/lib/libglu32.a \
	./freeglut-i686.dll \
	-lkernel32 -lm -lgdiplus -lole32


MINGW32:=/usr/bin/i686-w64-mingw32-


test : test.c graphicscore.c bitmapfont.c ../util/os_generic.c
	gcc $(CFLAGS) -o $@ $^ $(LINLDFLAGS)

test32.exe : test.c graphicscore.c bitmapfont.c ../util/os_generic.c
	$(MINGW32)gcc $(CFLAGSWIN32) -o $@ $^ glew/glew-i586.a  $(WINLDFLAGS32) 


clean :
	rm -rf *.o *~ test test32.exe test64.exe
