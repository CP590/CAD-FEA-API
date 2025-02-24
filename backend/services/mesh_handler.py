import threading
from pathlib import Path
import gmsh

current_file = Path(__file__)
root_dir = current_file.parent.parent
data_dir = root_dir / "data/"
geometries_dir = data_dir / "geometries/"
templates_dir = geometries_dir / "templates/"


# Instances gmsh model
def initialise_mesh():
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.model.add("model")


# Imports STEP file and adds to gmsh model
def import_step_file(name):
    step_file = str(geometries_dir) + "/" + name + ".step"
    gmsh.model.occ.importShapes(step_file)
    gmsh.model.occ.synchronize()


# Generates a simple mesh
def generate_mesh():
    gmsh.model.mesh.generate(3)
    result = gmsh.write(str(geometries_dir) + "/mesh.unv")
    return result


def return_unv_file_path():
    return str(geometries_dir) + "/" + "mesh.unv"


def parse_unv():
    unv_file = return_unv_file_path()
    nodes = {}
    elements = {}
    data = [nodes, elements]
    with open(unv_file, "r") as file:
        lines = [line for line in file.readlines()]

    i = 0
    while i < len(lines):
        if lines[i].strip() == "-1":
            i += 1
            continue

        if lines[i].strip() == "2411":
            i += 1
            while i < len(lines):
                if lines[i].strip() == "-1" and lines[i + 1].strip() == "-1":
                    i += 1
                    break
                parts = lines[i].split()
                if len(parts) >= 1:
                    node_id = int(parts[0])
                    i += 1
                if i >= len(lines): break

                coord_line = lines[i].strip().split()
                if len(coord_line) == 3:
                    x, y, z = map(lambda v: float(v.replace("D", "E")), coord_line)
                    nodes[node_id] = (x, y, z)
                    i += 1
        i += 1
        if lines[i].strip() == "2412":
            i += 1
            while i < len(lines):
                if lines[i].strip() == "-1" and lines[i + 1].strip() == "-1":
                    i += 2
                    break
                parts = lines[i].split()
                elem_id = int(parts[0])
                elem_type = int(parts[1])
                if i >= len(lines): break

                if elem_type == 21:
                    i += 2
                    coord_line = lines[i].strip().split()
                    x, y = tuple(map(int, coord_line))
                    elements[elem_id] = (x, y)
                    i += 1

                elif elem_type == 91:
                    i += 1
                    coord_line = lines[i].strip().split()
                    x, y, z = tuple(map(int, coord_line))
                    elements[elem_id] = (x, y, z)
                    i += 1

                elif elem_type == 111:
                    i += 1
                    coord_line = lines[i].strip().split()
                    w, x, y, z = tuple(map(int, coord_line))
                    elements[elem_id] = (w, x, y, z)
                    i += 1

                else:
                    i += 1
        else:
            i += 1

    print('Parse completed successfully')
    return data


def get_faces():
    entities = gmsh.model.getEntities()
    faces = [entity for entity in entities if entity[0] == 2]
    return faces


def add_face_name(id, name):
    faces = get_faces()
    face = next((f for f in faces if f[1] == id), None)

    if face:
        gmsh.model.addPhysicalGroup(2, [face[1]])
        gmsh.model.setPhysicalName(2, face[1], name)


def main_mesh_file():
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError("ERROR: main_mesh_file() is not running in the main thread")

    try:
        initialise_mesh()
        import_step_file("beam")
        result = generate_mesh()
        return result
    except Exception as e:
        print(f"Error during meshing: {e}")
        raise
    finally:
        gmsh.finalize()
