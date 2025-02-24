import asyncio
import os
import queue
import sys
import threading
import time

from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse

from api.schemas import BeamSelection, MaterialSelection, STEPParameters
from services import freecad_handler, mesh_handler

router = APIRouter()

main_thread_queue = queue.Queue()

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


main_loop = asyncio.new_event_loop()


def start_event_loop():
    asyncio.set_event_loop(main_loop)
    main_loop.run_forever()


if not asyncio.get_event_loop().is_running():
    threading.Thread(target=start_event_loop, daemon=True).start()


def mesh_file():
    if threading.current_thread() is threading.main_thread():
        return mesh_handler.main_mesh_file()
    else:
        result_queue = queue.Queue()
        main_thread_queue.put((mesh_handler.main_mesh_file, result_queue))
        return result_queue.get()


async def wait_for_mesh_file_update(file_path, check_interval=0.1, max_wait=5.0):
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return True
        await asyncio.sleep(check_interval)
        return False


def main_thread_worker():
    while True:
        func, result_queue = main_thread_queue.get()
        try:
            result = func()
            result_queue.put(result)
        except Exception as e:
            result_queue.put(e)


threading.Thread(target=main_thread_worker, daemon=True).start()


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
    unv_file = mesh_handler.return_unv_file_path()
    if await wait_for_mesh_file_update(unv_file):

        result = await asyncio.to_thread(mesh_file)
        data_list = mesh_handler.parse_unv()

        flattened_nodes = [coord for node in data_list[0].values() for coord in node]
        flattened_elements = [elem for element in data_list[1].values() for elem in element]
        data_json = {
            "node_list": flattened_nodes,
            "element_list": flattened_elements
        }

        return JSONResponse(content=data_json)


@router.post("/material")
def select_material(material: MaterialSelection):
    return {"message": f"Material {material.name} selected"}
