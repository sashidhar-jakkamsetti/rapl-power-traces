
CC=g++
CFLAGS=-lpthread -lrt -Os
LDFLAGS=-Lbin/
IFLAGS=-Imeasure/
OUTPUT=bin/measureapi
RM=rm

################ MEASUREMENT API ####################

all: measureapi

measureapi: main.o libmeasure.a
	$(CC) bin/main.o $(LDFLAGS) $(IFLAGS) -l:libmeasure.a -o $(OUTPUT) $(CFLAGS) 

main.o: measure/main.cpp 
	$(CC) -c measure/main.cpp $(IFLAGS) -o bin/main.o

libmeasure.a: measure/measure.cpp measure/measure.h
	$(CC) -c measure/measure.cpp $(IFLAGS) -o bin/measure.o
	ar rcs bin/libmeasure.a bin/measure.o

clean:
	$(RM) bin/measureapi bin/libmeasure.a bin/*.o

