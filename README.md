# MoleculeVisualizer
This program allows users to import and display molecules of different chemical compounds through .mol files. Users can add and change the way atoms are represented. For example, a user can create an Oxygen atom with a green colour and a Hydrogen atom with a blue colour. These are then added to an SQL database and retrieved from python to send to the webpage once a user wants to display a molecule. Components of the molecule (atoms, bonds) are created and manipulated in C with pointers.   

# Compilation
```
make testpy
```
```
python3 server.py PORT#
```
Open index.html
