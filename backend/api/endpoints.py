import asyncio
import threading
from fastapi import APIRouter
from fastapi.responses import FileResponse
from api.schemas import BeamSelection, MaterialSelection, STEPParameters
from services import freecad_handler, mesh_handler

router = APIRouter()

main_loop = asyncio.new_event_loop()


def start_event_loop():
    asyncio.set_event_loop(main_loop)
    main_loop.run_forever()


if not asyncio.get_event_loop().is_running():
    threading.Thread(target=start_event_loop(), daemon=True).start()


@router.get("/beams")
def get_beams():
    beam_list = freecad_handler.return_available_templates()
    return [{"beam_list": beam_list}]


@router.post("/set_step_parameters")
async def set_step_parameters(params: STEPParameters):
    success = freecad_handler.set_beam_parameters(params.cross_section, params.width, params.depth, params.length)
    freecad_handler.save_as_step_file()
    freecad_handler.save_as_stl_file()
    await mesh_geometry()
    if success:
        return {"message": "STEP file parameters set successfully."}
    else:
        return {"message": "Failed to set STEP file parameters."}


@router.get("/get-stl")
def get_stl():
    file_path = freecad_handler.return_beam_stl_file()
    if not file_path:
        return {"error": "File not found"}
    return FileResponse(file_path, media_type="model/stl", filename="beam")


@router.get("/mesh")
async def mesh_geometry():
    success = asyncio.run_coroutine_threadsafe(
        asyncio.to_thread(mesh_handler.main_mesh_file()), main_loop
    )
    result = success.result()
    return {"message": result}


@router.post("/material")
def select_material(material: MaterialSelection):
    return {"message": f"Material {material.name} selected"}
