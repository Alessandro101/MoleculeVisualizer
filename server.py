import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import MolDisplay
import molsql
import io
import json
from molecule import *

pages = ["index.html","element.html","sdf.html","displaymol.html"];

class Handler(BaseHTTPRequestHandler):
    mol = None;
    def do_GET(self):

        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type","text/html")
            fp = open(pages[0])
            homepage = fp.read()
            fp.close()
            self.send_header("Content-length",len(homepage))
            self.end_headers()
            self.wfile.write(bytes(homepage,"utf-8"))

        elif self.path == "/element.html":
            self.send_response(200)
            self.send_header("Content-type","text/html")
            fp = open(pages[1])
            elementpage = fp.read()
            fp.close()
            self.send_header("Content-length",len(elementpage))
            self.end_headers()
            self.wfile.write(bytes(elementpage,"utf-8"))

        elif self.path == "/sdf.html":
            self.send_response(200)
            self.send_header("Content-type","text/html")
            fp = open(pages[2])
            sdfpage = fp.read()
            fp.close()
            self.send_header("Content-length",len(sdfpage))
            self.end_headers()
            self.wfile.write(bytes(sdfpage,"utf-8"))

        elif self.path == "/displaymol.html":
            self.send_response(200)
            self.send_response(200)
            self.send_header("Content-type","text/html")
            fp = open(pages[3])
            displaypage = fp.read()
            fp.close()
            self.send_header("Content-length",len(displaypage))
            self.end_headers()
            self.wfile.write(bytes(displaypage,"utf-8"))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))
    def do_POST(self):

         if self.path == "/addElement":
            length = int(self.headers.get('Content-length'))
            data = self.rfile.read(length)
            jsonDict = json.loads(data)
            found = 0
            elements = database.conn.execute("""SELECT * FROM Elements""").fetchall();
            for element in elements:
                if jsonDict["elementCode"] in element:
                    found = 1;
            if found == 0:
                self.send_response(200)
                col1 = jsonDict["colour1"][1:]
                col2 = jsonDict["colour2"][1:]
                col3 = jsonDict["colour3"][1:]
                database['Elements'] = (int(jsonDict["elementNum"]),jsonDict["elementCode"],jsonDict["elementName"],col1,col2,col3,int(jsonDict["radius"]));
            else:
                self.send_response(404)
            updatedElements = database.conn.execute("""SELECT * FROM Elements""").fetchall();
            jsonstring = json.dumps(updatedElements)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(jsonstring.encode("utf-8"));

         elif self.path == "/inittable":
            self.send_response(200)
            updatedElements = database.conn.execute("""SELECT * FROM Elements""").fetchall();
            jsonstring = json.dumps(updatedElements)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(jsonstring.encode("utf-8"));

         elif self.path == "/delElement":
            length = int(self.headers.get('Content-length'))
            data = self.rfile.read(length)
            jsonDict = json.loads(data)
            found = 0
            elements = database.conn.execute("""SELECT * FROM Elements""").fetchall();
            for element in elements:
                if jsonDict["elementCode"] in element:
                    found = 1;
            if found == 1:
                self.send_response(200)
                database.conn.execute("""DELETE FROM Elements WHERE ELEMENT_CODE = '{}'""".format(jsonDict["elementCode"]))
            else:
                self.send_response(404)
            updatedElements = database.conn.execute("""SELECT * FROM Elements""").fetchall();
            jsonstring = json.dumps(updatedElements)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(jsonstring.encode("utf-8"));

         elif self.path == "/uploadSDF":
            length = int(self.headers.get('Content-length'))
            data = self.rfile.read(length)
            bytes = io.BytesIO(data)
            file = io.TextIOWrapper(bytes)
            for i in range(3):
                file.readline()
            molName = file.readline().split()[0];
            molecules = database.conn.execute("""SELECT * FROM Molecules""").fetchall()
            found = 0
            for molecule in molecules:
                if molName == molecule[1]:
                    found = 1
            if found == 1:
                self.send_response(404)
                error = "Molecule already in system"
                self.send_header("Content-type","text/plain")
                self.send_header("Content-length",len(error))
                self.end_headers()
                self.wfile.write(error.encode("utf-8"))
            else:
                for i in range(4):
                    file.readline()
                database.add_molecule(molName, file);
                message = "Successfully uploaded SDF file"
                distinctAtoms = database.conn.execute("""SELECT DISTINCT ELEMENT_CODE
                                                      FROM Atoms WHERE ELEMENT_CODE NOT IN
                                                      (SELECT ELEMENT_CODE FROM Elements)""").fetchall()
                for atom in distinctAtoms:
                    database['Elements'] = (0, atom[0], "DEFAULT" + atom[0], "FFFFFF", "050505", "020202",40)
                self.send_response(200)
                self.send_header("Content-type","text/plain")
                self.send_header("Content-length",len(message))
                self.end_headers()
                self.wfile.write(message.encode("utf-8"))

         elif self.path ==  "/initList":
             self.send_response(200)
             mols = database.conn.execute("""SELECT * FROM Molecules""").fetchall()
             molList = []
             for molecule in mols:
                 atoms = database.conn.execute("""SELECT COUNT(*) FROM Atoms, MoleculeAtom, Molecules
                                    WHERE Molecules.NAME = '{}' AND MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID
                                    AND Atoms.ATOM_ID = MoleculeAtom.ATOM_ID""".format(molecule[1])).fetchone()
                 bonds = database.conn.execute("""SELECT COUNT(*) FROM Bonds, MoleculeBond, Molecules
                                    WHERE Molecules.NAME = '{}' AND MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID
                                    AND Bonds.BOND_ID = MoleculeBond.BOND_ID""".format(molecule[1])).fetchone()
                 molList.append([molecule[1],atoms[0],bonds[0]])
             jsonstring = json.dumps(molList)
             self.send_header("Content-type","application/json")
             self.end_headers()
             self.wfile.write(jsonstring.encode("utf-8"));

         elif self.path == "/loadMol":
             self.send_response(200)
             length = int(self.headers.get('Content-length'))
             data = self.rfile.read(length)
             jsonDict = json.loads(data)
             distinctAtoms = database.conn.execute("""SELECT DISTINCT ELEMENT_CODE
                                                      FROM Atoms WHERE ELEMENT_CODE NOT IN
                                                      (SELECT ELEMENT_CODE FROM Elements)""").fetchall()
             for atom in distinctAtoms:
                 database['Elements'] = (0, atom[0], "DEFAULT" + atom[0], "FFFFFF", "050505", "020202",40)
             MolDisplay.radius = database.radius();
             MolDisplay.element_name = database.element_name();
             MolDisplay.header += database.radial_gradients();

             Handler.mol = database.load_mol(jsonDict["molName"])
             Handler.mol.sort()
             svgString = Handler.mol.svg()
             self.send_header("Content-type","text/html")
             self.send_header("Content-length",len(svgString))
             self.end_headers()
             self.wfile.write(svgString.encode("utf-8"))

         elif self.path == "/xrotation":
             self.send_response(200)
             length = int(self.headers.get('Content-length'))
             data = self.rfile.read(length)
             jsonDict = json.loads(data)
             mx = mx_wrapper(int(jsonDict['xRotation']),0,0)
             Handler.mol.xform( mx.xform_matrix );
             Handler.mol.sort()
             svgString = Handler.mol.svg()
             self.send_header("Content-type","text/html")
             self.send_header("Content-length",len(svgString))
             self.end_headers()
             self.wfile.write(svgString.encode("utf-8"))

         elif self.path == "/yrotation":
             self.send_response(200)
             length = int(self.headers.get('Content-length'))
             data = self.rfile.read(length)
             jsonDict = json.loads(data)
             mx = mx_wrapper(0,int(jsonDict['yRotation']),0)
             Handler.mol.xform( mx.xform_matrix );
             Handler.mol.sort()
             svgString = Handler.mol.svg()
             self.send_header("Content-type","text/html")
             self.send_header("Content-length",len(svgString))
             self.end_headers()
             self.wfile.write(svgString.encode("utf-8"))

         elif self.path == "/zrotation":
             self.send_response(200)
             length = int(self.headers.get('Content-length'))
             data = self.rfile.read(length)
             jsonDict = json.loads(data)
             mx = mx_wrapper(0,0,int(jsonDict['zRotation']))
             Handler.mol.xform( mx.xform_matrix );
             Handler.mol.sort()
             svgString = Handler.mol.svg()
             self.send_header("Content-type","text/html")
             self.send_header("Content-length",len(svgString))
             self.end_headers()
             self.wfile.write(svgString.encode("utf-8"))

         else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))

database = molsql.Database(reset=False);
database.create_tables();

http = HTTPServer(('localhost', int(sys.argv[1])), Handler)
http.serve_forever()
