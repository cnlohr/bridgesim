all : test test32.exe

CFLAGS:=-Os
CFLAGSWIN32:=$(CFLAGS)  -Ifreeglut  -m32  -Iglew -DGLEW_STATIC
#include "graphicscore.h"

LINLDFLAGS:=-lGL -lglut -lGLU -lGLEW
WINLDFLAGS32:=\
	/usr/i586-mingw32msvc/lib/libopengl32.a \
	/usr/i586-mingw32msvc/lib/libglu32.a \
	./freeglut-i686.dll \
	-lkernel32


MINGW32:=/usr/bin/i686-w64-mingw32-


test : test.c graphicscore.c
	gcc -o $@ $^ $(LINLDFLAGS)

test32.exe : test.c graphicscore.c
	$(MINGW32)gcc $(CFLAGSWIN32) -o $@ $^ glew/glew-i586.a  $(WINLDFLAGS32) 


clean :
	rm -rf *.o *~ test test32.exe test64.exe
