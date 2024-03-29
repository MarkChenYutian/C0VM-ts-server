from pathlib import Path
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
async def compile_project(
    filenames: List[str],
    codes: List[str],
    is_binaries: List[bool],
    dyn_check: bool
):
    """
    Compile C0 source code to BC0 bytecode
    """
    session_id = str(uuid.uuid4())
    filenames = list(map(path_sanitizer, filenames))

    create_workspace(session_id, filenames, codes, is_binaries)

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
        return {
            "bytecode": "",
            "error": f"Internal Server Error: {e}"
        }


@app.get("/interface")
async def get_interface(content: str):
    session_id = str(uuid.uuid4())
    try:
        create_workspace(session_id, ["input.o0"], [content], [True])    # ./cache/{session_id}

        output_filename = f"./cache/{session_id}/input.o0"
        stdout_str, stderr_str, retval = await execute_command(
            "cc0", "-i", output_filename
        )

        destroy_workspace(session_id)

        if retval == 0:
            return {
                "interface": f"/* Interface resolved by remote server */\n\n" + stdout_str,
                "error": ""
            }
        else:
            return {
                "interface": "",
                "error": f"/* Interface resolve failed or the object file does not have interface exposed! */\n\n" + stdout_str
            }
    except Exception as e:
        destroy_workspace(session_id)
        return {
            "interface": "",
            "error": f"Internal Server Error: {e}"
        }


@app.get("/decode")
async def get_content(content: str):
    session_id = str(uuid.uuid4())
    try:
        create_workspace(session_id, ["input.o0"], [content], [True])    # ./cache/{session_id}

        output_filename = f"./cache/{session_id}/input.o0"
        await execute_command(
            "mkdir", f"./cache/{session_id}/_c0vm_internal_cache"
        )
        await execute_command(
            "tar", "xfz", output_filename, "-C", f"./cache/{session_id}/_c0vm_internal_cache"
        )

        decompressed_c0 = [
            c0_ref
            for c0_ref in Path(".", "cache", session_id).glob("**/*.c0")
        ]
        decompressed_c1 = [
            c1_ref
            for c1_ref in Path(".", "cache", session_id).glob("**/*.c1")
        ]
        
        content = None
        for result in decompressed_c0 + decompressed_c1:
            if result.is_file():
                with open(result, "r") as f: content = f.read()
                break

        destroy_workspace(session_id)

        if content is None:
            return {
                "result": "",
                "error": "/* Failed to retrieve decoded content from the object file */"
            }
        else:
            return {
                "result": content,
                "error": ""
            }
    except Exception as e:
        destroy_workspace(session_id)
        return {
            "result": "",
            "error": f"Internal Server Error: {e}"
        }


app.mount(
    "/", StaticFiles(directory="./static", html=True), name="static"
)

