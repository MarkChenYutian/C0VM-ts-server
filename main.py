import uuid

from typing import List
from helpers import execute_command, create_workspace, destroy_workspace, path_sanitizer

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from strip_ansi import strip_ansi

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compile")
async def compile_project(filenames: List[str], codes: List[str], dyn_check: bool):
    """
    Compile C0 source code to BC0 bytecode
    """
    session_id = str(uuid.uuid4())
    filenames = list(map(path_sanitizer, filenames))

    create_workspace(session_id, filenames, codes)

    try:
        compile_filenames = list(map(lambda s: f"./cache/{session_id}/" + s, filenames))
        output_filename = f"./cache/{session_id}/out.bc0"
        args = []

        if (dyn_check):
            args.append("-d")
        args.append("-b")               # set bytecode compiler
        args.append("--bytecode-ext")   # thanks Iliano & Frank for supporting this project!
        args.append("-o")               # set output file name
        args.append(output_filename)    # set output_file
        args += compile_filenames       # compile files in given order

        stdout_str, stderr_str, retval = await execute_command(
            "cc0", *args
        )

        stdout_str = strip_ansi(stdout_str)

        if (retval == 0):
            with open(output_filename, "r") as F:
                bytecode_content = F.read()
            destroy_workspace(session_id)
            return {
                "bytecode": bytecode_content,
                "error": ""
            }
        else:
            destroy_workspace(session_id)
            return {
                "bytecode": "",
                "error": stdout_str
            }

    except Exception as e:
        destroy_workspace(session_id)
        raise e


app.mount(
    "/", StaticFiles(directory="./static", html=True), name="static"
)

