import subprocess
import tempfile
import os
import shutil
from mcp.server.fastmcp import FastMCP
animator_ctrl = FastMCP()

ANIM_BIN = os.getenv("ANIM_BINARY_PATH", "manim")  # /path/to/main.exe
WORKSPACE_REGISTRY = {}
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)  

@animator_ctrl.tool()
def render_animation_script(animation_source: str) -> str:
    """Process and render the animation source code"""
    
    workspace = os.path.join(OUTPUT_FOLDER, "animation_workspace")  
    os.makedirs(workspace, exist_ok=True)
    source_file = os.path.join(workspace, "animation_scene.py")
    
    try:
        
        with open(source_file, "w") as file_handle:
            file_handle.write(animation_source)
        
       
        process_result = subprocess.run(
            [ANIM_BIN, "-p", source_file],
            capture_output=True,
            text=True,
            cwd=workspace
        )
        if process_result.returncode == 0:
            WORKSPACE_REGISTRY[workspace] = True
            print(f"Animation successfully rendered at: {workspace}")
            return "Render completed successfully. Animation file generated."
        else:
            return f"Render process failed: {process_result.stderr}"
    except Exception as e:
        return f"Error during animation processing: {str(e)}"

@animator_ctrl.tool()
def purge_workspace(workspace_path: str) -> str:
    """Remove the specified animation workspace after rendering is complete."""
    try:
        if os.path.exists(workspace_path):
            shutil.rmtree(workspace_path)
            return f"Workspace cleanup completed: {workspace_path}"
        else:
            return f"Workspace not found: {workspace_path}"
    except Exception as e:
        return f"Failed to clean workspace: {workspace_path}. Error: {str(e)}"

if __name__ == "__main__":
    animator_ctrl.run(transport="stdio")
