#include "mol.h"

/*This function should copy the values pointed to by element, x, y, and z into the atom stored at
atom*/
void atomset( atom *atom, char element[3], double *x, double *y, double *z )
{
  strcpy(atom->element,element);
  atom->x = *x;
  atom->y = *y;
  atom->z = *z;
}

/*This function should copy the values in the atom stored at atom to the locations pointed to by
element, x, y, and z*/
void atomget( atom *atom, char element[3], double *x, double *y, double *z )
{
  strcpy(element, atom->element);
  *x = atom->x;
  *y = atom->y;
  *z = atom->z;
}

/*This function should copy the values pointed to by a1, a2, atoms, and epairs into the
corresponding structure attributes in bond*/
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom
**atoms, unsigned char *epairs ){
  bond->a1 = *a1;
  bond->a2 = *a2;
  bond->atoms = *atoms;
  bond->epairs = *epairs;
  compute_coords(bond);
}

/*This function should copy the structure attributes in bond to their corresponding arguments:
a1, a2, atoms, and epairs*/
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom
**atoms, unsigned char *epairs ){
  *a1 = bond->a1;
  *a2 = bond->a2;
  *atoms = bond->atoms;
  *epairs = bond->epairs;
}

/*This function should compute the z, x1, y1, x2, y2, len, dx, and dy values of the bond and set
them in the appropriate structure member variables*/
void compute_coords( bond *bond )
{
  bond->x1 = bond->atoms[bond->a1].x;
  bond->y1 = bond->atoms[bond->a1].y;
  bond->x2 = bond->atoms[bond->a2].x;
  bond->y2 = bond->atoms[bond->a2].y;
  bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z)/2;
  bond->len = sqrt((bond->x2 - bond->x1)*(bond->x2 - bond->x1)+(bond->y2 - bond->y1)*(bond->y2 - bond->y1));
  bond->dx = (bond->x2 - bond->x1)/bond->len;
  bond->dy = (bond->y2 - bond->y1)/bond->len;
}

/*This function returns the address of a malloced area of memory, large enough to hold a
molecule. The molecule will allocate enough space for atom_max atoms and atom_ptrs, as
well as enough space for bond_max bonds and bond_ptrs. Returns NULL if malloc fails.*/
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max )
{
  molecule *mol = malloc(sizeof(molecule));
  if (mol == NULL)
  {
    return NULL;
  }
  mol->atom_max = atom_max;
  mol->atom_no = 0;
  mol->bond_max = bond_max;
  mol->bond_no = 0;
  mol->atoms = malloc(sizeof(struct atom) * atom_max);
  if (mol->atoms == NULL)
  {
    return NULL;
  }
  mol->atom_ptrs = malloc(sizeof(struct atom *) * atom_max);
  if (mol->atom_ptrs == NULL)
  {
    return NULL;
  }
  mol->bonds = malloc(sizeof(struct bond) * bond_max);
  if (mol->bonds == NULL)
  {
    return NULL;
  }
  mol->bond_ptrs = malloc(sizeof(struct bond *) * bond_max);
  if (mol->bond_ptrs == NULL)
  {
    return NULL;
  }
  return mol;
}

void reassignBond(bond * bond, atom ** atoms){
  bond->atoms = *atoms;
}

/*This function allocates enough space for molecule, and copies the contents
of another molecule called src into the structure*/
molecule *molcopy( molecule *src )
{
  molecule *mol = molmalloc(src->atom_max, src->bond_max);
  if (mol == NULL)
  {
    return NULL;
  }
  for (int i = 0; i < src->atom_no;i++)
  {
    molappend_atom(mol, &src->atoms[i]);
  }
  for (int j = 0; j < src->bond_no;j++)
  {
    molappend_bond(mol, &src->bonds[j]);
    reassignBond(&mol->bonds[j],&mol->atoms);
  }
  return mol;
}

/*This function frees the memory allocated to a molecule and its elements*/
void molfree( molecule *ptr )
{
  free(ptr->atoms);
  free(ptr->atom_ptrs);
  free(ptr->bonds);
  free(ptr->bond_ptrs);
  free(ptr);
}

/*This function will copy the data pointed to by atom to the first “empty” atom in atoms in the
molecule pointed to by molecule, and set the first “empty” pointer in atom_ptrs to the same
atom in the atoms array incrementing the value of atom_no*/
void molappend_atom( molecule *molecule, atom *atom )
{
  if (molecule->atom_max == 0)
  {
    molecule->atom_max = molecule->atom_max + 1;
    molecule->atoms = realloc(molecule->atoms,sizeof(struct atom) * 1);
    if (molecule->atoms == NULL)
    {
      printf("Memory error has occured");
      exit(0);
    }
    molecule->atom_ptrs = realloc(molecule->atom_ptrs,sizeof(struct atom *) * 1);
    if (molecule->atom_ptrs == NULL)
    {
      printf("Memory error has occured");
      exit(0);
    }
    molecule->atoms[molecule->atom_no] = *atom;
    molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];
    molecule->atom_no = molecule->atom_no + 1;
   }
  else
  {
    if (molecule->atom_max == molecule->atom_no)
    {
      molecule->atom_max = molecule->atom_max * 2;
      molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
      if (molecule->atoms == NULL)
      {
        printf("Memory error has occured");
        exit(0);
      }
      molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom *) * molecule->atom_max);
      if (molecule->atom_ptrs == NULL)
      {
        printf("Memory error has occured");
        exit(0);
      }
      for (int i = 0; i < molecule->atom_no; i++)
      {
        molecule->atom_ptrs[i] = &molecule->atoms[i];
      }
    }
    molecule->atoms[molecule->atom_no] = *atom;
    molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];
    molecule->atom_no = molecule->atom_no + 1;
  }
}

/*This function will copy the data pointed to by bond to the first “empty” bond in bonds in the
molecule pointed to by molecule, and set the first “empty” pointer in bond_ptrs to the same
bond in the bonds array incrementing the value of bond_no*/
void molappend_bond( molecule *molecule, bond *bond )
{
  if (molecule->bond_max == 0)
  {
    molecule->bond_max = molecule->bond_max + 1;
    molecule->bonds = realloc(molecule->bonds,sizeof(struct bond) * 1);
    if (molecule->bonds == NULL)
    {
      printf("Memory error has occured");
      exit(0);
    }
    molecule->bond_ptrs = realloc(molecule->bond_ptrs,sizeof(struct bond *) * 1);
    if (molecule->bond_ptrs == NULL)
    {
      printf("Memory error has occured");
      exit(0);
    }
    molecule->bonds[molecule->bond_no] = *bond;
    molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no];
    molecule->bond_no = molecule->bond_no + 1;
  }
  else
  {
    if (molecule->bond_max == molecule->bond_no)
    {
      molecule->bond_max = molecule->bond_max * 2;
      molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
      if (molecule->bonds == NULL)
      {
        printf("Memory error has occured");
        exit(0);
      }
      molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond *) * molecule->bond_max);
      if (molecule->bond_ptrs == NULL)
      {
        printf("Memory error has occured");
        exit(0);
      }
      for (int i = 0; i < molecule->bond_no; i++)
      {
        molecule->bond_ptrs[i] = &molecule->bonds[i];
      }
    }
    molecule->bonds[molecule->bond_no] = *bond;
    molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no];
    molecule->bond_no = molecule->bond_no + 1;
  }
}

/*This function will sort the atom_ptrs array in order of increasing z value.
This function will also sort the bond_ptrs array in order of increasing average z value*/
void molsort( molecule *molecule )
{
  qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom *),atom_comp);
  qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond *),bond_comp);
}

//Comparison function for bond structure (qsort)
int atom_comp(const void * a, const void * b)
{
  double x,y;

  x = (*(atom**)a)->z;
  y = (*(atom**)b)->z;

  if (x > y)
  {
    return 1;
  }
  if (x < y)
  {
    return -1;
  }
  else
  {
    return 0;
  }
}

//Comparison function for bond structure (qsort)
int bond_comp(const void * a, const void * b){
  double x,y;

  x = (*(bond**)a)->z;
  y = (*(bond**)b)->z;

 if (x > y){
    return 1;
  }
  if (x < y){
    return -1;
  }
  else{
    return 0;
  }
}

/*This function will set the values in an affine transformation
matrix, xform_matrix, corresponding to a rotation of deg degrees around the x-axis*/
void xrotation( xform_matrix xform_matrix, unsigned short deg )
{
  double rad = deg * (M_PI/180);

  xform_matrix[0][0] = 1;
  xform_matrix[0][1] = 0;
  xform_matrix[0][2] = 0;
  xform_matrix[1][0] = 0;
  xform_matrix[1][1] = cos(rad);
  xform_matrix[1][2] = -sin(rad);
  xform_matrix[2][0] = 0;
  xform_matrix[2][1] = sin(rad);
  xform_matrix[2][2] = cos(rad);
}

/*This function will set the values in an affine transformation
matrix, xform_matrix, corresponding to a rotation of deg degrees around the y-axis*/
void yrotation( xform_matrix xform_matrix, unsigned short deg )
{
  double rad = deg * (M_PI/180);

  xform_matrix[0][0] = cos(rad);
  xform_matrix[0][1] = 0;
  xform_matrix[0][2] = sin(rad);
  xform_matrix[1][0] = 0;
  xform_matrix[1][1] = 1;
  xform_matrix[1][2] = 0;
  xform_matrix[2][0] = -sin(rad);
  xform_matrix[2][1] = 0;
  xform_matrix[2][2] = cos(rad);
}

/*This function will set the values in an affine transformation
matrix, xform_matrix, corresponding to a rotation of deg degrees around the z-axis*/
void zrotation( xform_matrix xform_matrix, unsigned short deg )
{
  double rad = deg * (M_PI/180);

  xform_matrix[0][0] = cos(rad);
  xform_matrix[0][1] = -sin(rad);
  xform_matrix[0][2] = 0;
  xform_matrix[1][0] = sin(rad);
  xform_matrix[1][1] = cos(rad);
  xform_matrix[1][2] = 0;
  xform_matrix[2][0] = 0;
  xform_matrix[2][1] = 0;
  xform_matrix[2][2] = 1;
}

/*This function will apply the transformation matrix to all the atoms of the molecule by
performing a vector matrix multiplication on the x, y, z coordinates*/
void mol_xform( molecule *molecule, xform_matrix matrix )
{
  double newX, newY, newZ;

  for (int i = 0; i < molecule->atom_no; i++)
  {
    newX = (molecule->atoms[i].x * matrix[0][0]) + (molecule->atoms[i].y * matrix[0][1]) + (molecule->atoms[i].z * matrix[0][2]);
    newY = (molecule->atoms[i].x * matrix[1][0]) + (molecule->atoms[i].y * matrix[1][1]) + (molecule->atoms[i].z * matrix[1][2]);
    newZ = (molecule->atoms[i].x * matrix[2][0]) + (molecule->atoms[i].y * matrix[2][1]) + (molecule->atoms[i].z * matrix[2][2]);

    molecule->atoms[i].x = newX;
    molecule->atoms[i].y = newY;
    molecule->atoms[i].z = newZ;
  }

  for (int j = 0; j < molecule->bond_no;j++)
  {
    compute_coords(&(molecule->bonds[j]));
  }
}
