import molecule

header = """<svg version="1.1" width="1000" height="1000"
xmlns="http://www.w3.org/2000/svg">""";
footer = """</svg>""";
offsetx = 500;
offsety = 500;

class Atom:
	#Initialize the atom object with a c_atom parameter
	def __init__(self, c_atom):
		self.c_atom = c_atom
		self.z = c_atom.z
	def __str__(self):
		return ("Element: %c X: %f Y: %f Z: %f") % (self.c_atom.element, self.c_atom.x,self.c_atom.y,self.z)
	#Create an svg string representing the atom object
	def svg(self):
		return ('  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n') % ((self.c_atom.x * 100 + offsetx),
		(self.c_atom.y * 100 + offsety),radius[self.c_atom.element],element_name[self.c_atom.element] )

class Bond:
	#Initalize the bond object with a c_bond parameter
	def __init__(self, bond):
		self.bond = bond
		self.z = bond.z
	def __str__(self):
		return ("a1: %u a2: %u epairs: %u x1: %f y1: %f x2: %f y2: %f dx: %f dy: %f") % (self.bond.a1, self.bond.a2, self.bond.epairs, self.bond.x1,self.bond.y1,self.bond.x2,
		self.bond.y2,self.bond.dx,self.bond.dy)
	#Create an svg string representing the bond
	def svg(self):
		x1Circle = self.bond.x1 * 100 + offsetx
		y1Circle = self.bond.y1 * 100 + offsety
		x2Circle = self.bond.x2 * 100 + offsetx
		y2Circle = self.bond.y2 * 100 + offsety
		dx = (self.bond.dx) * 10
		dy = (self.bond.dy) * 10
		cx1 = x1Circle + dy
		cy1 = y1Circle - dx
		cx2 = x1Circle - dy
		cy2 = y1Circle + dx
		cx3 = x2Circle + dy
		cy3 = y2Circle - dx
		cx4 = x2Circle - dy
		cy4 = y2Circle + dx
		return ('  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n') % (cx1,cy1,cx2,cy2,cx4,cy4,cx3,cy3)

class Molecule(molecule.molecule):
	def __str__(self):
		str = ""
		for i in range(self.atom_no):
			atom = Atom(self.get_atom(i))
			print(atom)
		for i in range(self.bond_no):
			bond = Bond(self.get_bond(i))
			print(bond)
		return str
	#Create an svg string containing all atoms and bonds in ascending z order
	def svg(self):
		atoms = []
		bonds = []
		k = 0
		j = 0
		str = ""
		str = str + header
		for i in range(self.atom_no):
			atom = Atom(self.get_atom(i))
			atoms.append(atom)
		for i in range(self.bond_no):
			bond = Bond(self.get_bond(i))
			bonds.append(bond)
		while k < self.atom_no and j < self.bond_no:
			if atoms[k].z < bonds[j].z:
				str = str + atoms[k].svg()
				k = k + 1
			else:
				str = str + bonds[j].svg()
				j = j + 1
		if k == self.atom_no:
			while j < self.bond_no:
				str = str + bonds[j].svg()
				j = j + 1
		else:
			while k < self.atom_no:
				str = str + atoms[k].svg()
				k = k + 1
		str = str + footer
		return str
	#Parse through sdf file and creates molecule object
	def parse(self, file):
		index = 4
		fileValues = []
		for line in file:
			values = line.split()
			fileValues.append(values)
		numOfAtoms = (int)(fileValues[3][0])
		numOfBonds = (int)(fileValues[3][1])
		for i in range(numOfAtoms):
			self.append_atom(fileValues[index][3],(float)(fileValues[index][0]),
			(float)(fileValues[index][1]),(float)(fileValues[index][2]))
			index = index + 1
		for i in range(numOfBonds):
			self.append_bond((int)(fileValues[index][0]) - 1,(int)(fileValues[index][1]) - 1,
			(int)(fileValues[index][2]))
			index = index + 1
