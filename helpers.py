import os
import shutil

import asyncio
from typing import List, Tuple

async def execute_command(program: str, *args: List[str]) -> Tuple[str, str, int]:
    """
    Execute command `$ program *args` in an async manner 
    with subprocess in the background.

    Return a tuple of form `(stdout, stderr, retval)`
    """

    print(f"exec: ${program} {' '.join(args)}")

    # Create an async subprocess from current process
    child_proc = await asyncio.create_subprocess_exec(
        program,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Receive stdout, stderr from child process
    stdout, stderr = await child_proc.communicate()

    return_val = child_proc.returncode
    stdout_str = stdout.decode().strip()
    stderr_str = stderr.decode().strip()

    return (stdout_str, stderr_str, return_val)


def path_sanitizer(file_name: str) -> str:
    """
    Sanitize file names to prevent the file names like "../../../config" 
    being injected to the server
    """
    return file_name.split("/")[-1]


def create_workspace(session_id: str, file_names: List[str], codes: List[str]) -> None:
    """
    Initialize the workspace for session
    """
    os.mkdir(f"./cache/{session_id}")

    for file_name, code in zip(file_names, codes):
        with open(f"./cache/{session_id}/{file_name}", "w") as F:
            F.write(code)
    return

def destroy_workspace(session_id: str) -> None:
    """
    Destroy the session workspace to release resources
    """
    shutil.rmtree(f"./cache/{session_id}")
    return

if __name__ == "__main__":
    asyncio.run(
        execute_command(
            "cc0",
            *['-b', '-o', './cache/f7acaeaa-3288-4a62-821e-39d1aeba9657/out.bc0', './cache/f7acaeaa-3288-4a62-821e-39d1aeba9657/something.c0'],
        )
    )