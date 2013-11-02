OUTS := servertest clientonly
all : $(OUTS)

CFLAGS:=-O0 -g -fPIC -I../util
LDFLAGS:=-lpthread -O0 -g

cent.so : cent.o ../util/os_generic.o chash.o
	gcc -shared -o $@ $^ $(LDFLAGS)

servertest : servertest.o cent.so
	gcc -o $@ servertest.o $(LDFLAGS) ./cent.so

clientonly : clientonly.o cent.so
	gcc -o $@ clientonly.o $(LDFLAGS) ./cent.so

clean :
	rm -rf *.o *~ $(OUTS) cent.so
