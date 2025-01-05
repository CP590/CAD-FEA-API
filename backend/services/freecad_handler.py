import sys
from pathlib import Path
import shutil

FREECADBINPATH = r'D:\Program Files\FreeCAD 1.0\bin'
current_file = Path(__file__)
root_dir = current_file.parent.parent
data_dir = root_dir / "data/"
geometries_dir = data_dir / "geometries/"
templates_dir = geometries_dir / "templates/"

sys.path.append(FREECADBINPATH)

try:
    import FreeCAD
    import Part
    import Sketcher
    print("FreeCAD imported successfully.")
except ImportError as e:
    print(f"Failed to import FreeCAD: {e}")


def open_geometry(file):
    doc = FreeCAD.open(str(file))
    part = doc.getObject("Body")
    return part


def return_available_templates():
    template_list = []
    for file in templates_dir.iterdir():
        cross_section = return_beam_cross_section(file)
        template_list.append((file.name, cross_section))
    return template_list


def return_beam_cross_section(name):
    part = open_geometry(name)
    if hasattr(part, "cross_section"):
        return part.cross_section


def copy_template(source_file):
    destination_file = geometries_dir / "beam.FCStd"
    shutil.copy(source_file, destination_file)


def return_template_file_path(name):
    for file in templates_dir.iterdir():
        if file.name == name + ".FCStd":
            return file


def set_beam_parameters(beam_type, width, depth, length):
    file_path = return_template_file_path(beam_type)  # TODO: Sort out difference between file name "rectangular" and cross_section "Rectangular"
    copy_template(file_path)
    part = open_geometry(file_path)
    sketch = part.getObject("Sketch")
    pad = part.getObject("Pad")
    sketch.setDatum("width", FreeCAD.Units.Quantity(str(width) + ' mm'))
    sketch.setDatum("depth", FreeCAD.Units.Quantity(str(depth) + ' mm'))
    pad.Length = length
    part.Document.recompute()
    result = part.Document.save()
    return result != 0


def return_beam_file_path():
    for file in geometries_dir.iterdir():
        if file.name == "beam.FCStd":
            return file


def save_as_step_file():
    step_file_path = str(geometries_dir) + "/beam.step"
    file = return_beam_file_path()
    part = open_geometry(file)
    Part.export([part], step_file_path)
