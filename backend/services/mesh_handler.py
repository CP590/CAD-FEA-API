import threading
from pathlib import Path
import gmsh

current_file = Path(__file__)
root_dir = current_file.parent.parent
data_dir = root_dir / "data/"
geometries_dir = data_dir / "geometries/"
templates_dir = geometries_dir / "templates/"


def initialise_mesh():
    gmsh.initialize()
    gmsh.model.add("model")


def import_step_file(name):
    step_file = str(geometries_dir) + "/" + name + ".step"
    gmsh.model.occ.importShapes(step_file)
    gmsh.model.occ.synchronize()


def generate_mesh():
    gmsh.model.mesh.generate(3)
    result = gmsh.write(str(geometries_dir) + "/mesh.inp")
    return result


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


def mesh_file():
    if threading.current_thread() is threading.main_thread():
        return main_mesh_file()
    else:
        raise RuntimeError("Gmsh operations much run in the main thread.")
