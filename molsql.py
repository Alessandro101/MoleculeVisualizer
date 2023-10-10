import MolDisplay;
import os;
import sqlite3;

class Database:
    #This constructor should create/open a database connection to a file in the local directory called "molecules.db"
    def __init__(self, reset):
        if reset == True and os.path.exists('molecules.db'):
            os.remove('molecules.db');
        self.conn = sqlite3.connect('molecules.db');
    #This method will create the tables if they don't already exist
    def create_tables(self):
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements(
                            ELEMENT_NO INTEGER NOT NULL,
                            ELEMENT_CODE VARCHAR(3) NOT NULL,
                            ELEMENT_NAME VARCHAR(32) NOT NULL,
                            COLOUR1 CHAR(6) NOT NULL,
                            COLOUR2 CHAR(6) NOT NULL,
                            COLOUR3 CHAR(6) NOT NULL,
                            RADIUS DECIMAL(3) NOT NULL,
                            PRIMARY KEY(ELEMENT_CODE));""");
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms(
                            ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            ELEMENT_CODE VARCHAR(3) NOT NULL,
                            X DECIMAL(7,4) NOT NULL,
                            Y DECIMAL(7,4) NOT NULL,
                            Z DECIMAL(7,4) NOT NULL,
                            FOREIGN KEY(ELEMENT_CODE) REFERENCES Elements);""");
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Bonds(
                            BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            A1 INTEGER NOT NULL,
                            A2 INTEGER NOT NULL,
                            EPAIRS INTEGER NOT NULL)""");
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Molecules(
                            MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            NAME TEXT NOT NULL UNIQUE);""");
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom(
                            MOLECULE_ID INTEGER NOT NULL,
                            ATOM_ID INTEGER NOT NULL,
                            PRIMARY KEY(MOLECULE_ID,ATOM_ID),
                            FOREIGN KEY(MOLECULE_ID) REFERENCES Molecules,
                            FOREIGN KEY(ATOM_ID) REFERENCES Atoms);""");
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond(
                            MOLECULE_ID INTEGER NOT NULL,
                            BOND_ID INTEGER NOT NULL,
                            PRIMARY KEY(MOLECULE_ID,BOND_ID)
                            FOREIGN KEY(MOLECULE_ID) REFERENCES Molecules,
                            FOREIGN KEY(BOND_ID) REFERENCES Bonds);""");
    #This method will allow the use of indexing to insert elements into a table
    def __setitem__(self,table,values):
        if table == 'Atoms':
            self.conn.execute("""INSERT
                                 INTO {} (ELEMENT_CODE, X, Y, Z)
                                 VALUES {};""".format(table,values));
        if table == 'Bonds':
            self.conn.execute("""INSERT
                                 INTO {} (A1, A2, EPAIRS)
                                 VALUES {};""".format(table,values));
        if table == 'Molecules':
            self.conn.execute("""INSERT
                                 INTO {} (NAME)
                                 VALUES ('{}');""".format(table,values));
        if table == 'Elements' or table == 'MoleculeBond' or table == 'MoleculeAtom':
            self.conn.execute("""INSERT
                                 INTO {}
                                 VALUES {};""".format(table,values));
        self.conn.commit();
    #This method will insert an entry into the Atoms and MoleculeAtom tables using given atom and molname
    def add_atom(self, molname, atom):
        self['Atoms'] = (atom.c_atom.element, atom.c_atom.x, atom.c_atom.y, atom.c_atom.z);
        molId = self.conn.execute("""SELECT MOLECULE_ID FROM Molecules
                        WHERE NAME = '{}';""".format(molname));
        atomId = self.conn.execute("""SELECT MAX(ATOM_ID) FROM Atoms;""");
        self['MoleculeAtom'] = (molId.fetchone()[0],atomId.fetchone()[0]);
    #This method will insert an entry into the Bonds and MoleculeBond tables using given bond and molname
    def add_bond(self, molname, bond):
        self['Bonds'] = (bond.bond.a1,bond.bond.a2,bond.bond.epairs);
        molId = self.conn.execute("""SELECT MOLECULE_ID FROM Molecules
                                WHERE NAME = '{}';""".format(molname));
        bondId = self.conn.execute("""SELECT MAX(BOND_ID) FROM Bonds;""");
        self['MoleculeBond'] = (molId.fetchone()[0],bondId.fetchone()[0]);
    #This method will create a MolDisplay Molecule object, parse an sdf file and add all atoms and bonds from the file
    def add_molecule(self, name, fp):
        mol = MolDisplay.Molecule();
        mol.parse(fp);
        self['Molecules'] = (name);
        for i in range(mol.atom_no):
            self.add_atom(name, MolDisplay.Atom(mol.get_atom(i)));
        for i in range(mol.bond_no):
            self.add_bond(name, MolDisplay.Bond(mol.get_bond(i)));
    #This method will create a MolDisplay Molecule object, and add all atoms and bonds associated with the molecule to the object
    def load_mol(self,name):
        mol = MolDisplay.Molecule();
        atoms = self.conn.execute("""SELECT * FROM Atoms, MoleculeAtom, Molecules
                                    WHERE Molecules.NAME = '{}' AND MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID
                                    AND Atoms.ATOM_ID = MoleculeAtom.ATOM_ID
                                    ORDER BY ATOM_ID""".format(name)).fetchall();
        for atom in atoms:
            mol.append_atom(atom[1],atom[2],atom[3],atom[4]);
        bonds = self.conn.execute("""SELECT * FROM Bonds, MoleculeBond, Molecules
                                    WHERE Molecules.NAME = '{}' AND MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID
                                    AND Bonds.BOND_ID = MoleculeBond.BOND_ID
                                    ORDER BY BOND_ID""".format(name)).fetchall();
        for bond in bonds:
            mol.append_bond(bond[1],bond[2],bond[3]);
        return mol;
    #This method returns a Python dictionary mapping ELEMENT_CODE values to RADIUS values
    def radius(self):
        rad = {};
        elements = self.conn.execute("""SELECT * FROM Elements""").fetchall();
        for element in elements:
            mapping = {element[1]:element[6]};
            rad.update(mapping);
        return rad;
    #This method returns a Python dictionary mapping ELEMENT_CODE values to ELEMENT_NAME values
    def element_name(self):
        ele = {};
        elements = self.conn.execute("""SELECT * FROM Elements""").fetchall();
        for element in elements:
            mapping = {element[1]:element[2]};
            ele.update(mapping);
        return ele;
    #This method returns a Python string that contains all the radial gradient svgs for each element
    def radial_gradients(self):
        str = "";
        radialGradientSVG = """
  <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
    <stop offset="0%%" stop-color="#%s"/>
    <stop offset="50%%" stop-color="#%s"/>
    <stop offset="100%%" stop-color="#%s"/>
  </radialGradient>""";
        elements = self.conn.execute("""SELECT * FROM Elements""").fetchall();
        for element in elements:
            str += (radialGradientSVG % (element[2], element[3],element[4],element[5]));
        return str;
