from fastapi import APIRouter
from api.schemas import BeamSelection, MaterialSelection, STEPParameters
from services import freecad_handler, mesh_handler

router = APIRouter()


@router.get("/beams")
def get_beams():
    beam_list = freecad_handler.return_available_templates()
    return [{"beam_list": beam_list}]


@router.post("/set_step_parameters")
def set_step_parameters(params: STEPParameters):
    success = freecad_handler.set_beam_parameters(params.cross_section, params.width, params.depth, params.length)
    freecad_handler.save_as_step_file()
    if success:
        return {"message": "STEP file parameters set successfully."}
    else:
        return {"message": "Failed to set STEP file parameters."}


@router.get("/mesh")
def mesh_geometry():
    success = mesh_handler.mesh_file()
    if success:
        return {"message": "Mesh generated successfully."}
    else:
        return {"message": "Failed to generate mesh."}


@router.post("/material")
def select_material(material: MaterialSelection):
    return {"message": f"Material {material.name} selected"}
