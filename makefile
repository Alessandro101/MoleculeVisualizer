all: testpy

test: test.o libmol.so
	clang test.o -L. -lmol -lm -o test

test.o: test.c mol.h
	clang -c -std=c99 -Wall -pedantic test.c -o test.o

testpy: _molecule.so

mol.o: mol.c mol.h
	clang -c -std=c99 -Wall -pedantic mol.c -fPIC -o mol.o

libmol.so: mol.o
	clang mol.o -shared -o libmol.so

molecule_wrap.c: molecule.i
	swig3.0 -python molecule.i

molecule_wrap.o: molecule_wrap.c
	clang -c -std=c99 -Wall -pedantic molecule_wrap.c -fPIC -I/usr/include/python3.7m -o molecule_wrap.o

_molecule.so: molecule_wrap.o libmol.so
	clang molecule_wrap.o -shared -dynamiclib -L. -lmol -L/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -lpython3.7m -o _molecule.so

clean:
	rm -f *.o *.so test
