all : test test32.exe

CFLAGS:=-Os
CFLAGSWIN32:=$(CFLAGS)  -Ifreeglut  -m32
LINLDFLAGS:=-lGL -lglut
WINLDFLAGS32:=\
	/usr/i586-mingw32msvc/lib/libopengl32.a \
	./freeglut-i686.dll
#WINLDFLAGS64:=\
#	/usr/i686-w64-mingw32/lib/libopengl32.a \
#	./freeglut-x86_64.dll

#MINGW64:=/usr/bin/x86_64-w64-mingw32-
MINGW32:=/usr/bin/i686-w64-mingw32-


test : test.c graphicscore.c
	gcc -o $@ $^ $(LINLDFLAGS)

test32.exe : test.c graphicscore.c
	$(MINGW32)gcc $(CFLAGSWIN32) -o $@ $^ $(WINLDFLAGS32)


clean :
	rm -rf *.o *~ test test32.exe test64.exe
