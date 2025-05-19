import subprocess
import tempfile
import os
import shutil
import json
import glob
import time
from datetime import datetime
from typing import List, Dict, Optional, Union
from mcp.server.fastmcp import FastMCP

animator_ctrl = FastMCP()

ANIM_BIN = os.getenv("ANIM_BINARY_PATH", "manim")  # /path/to/main.exe
WORKSPACE_REGISTRY = {}
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# Create necessary directories
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TEMPLATE_FOLDER, exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "quality": "medium",  # low, medium, high
    "resolution": "1080p",
    "fps": 30,
    "background_color": "#333333",
    "preview_mode": False,
    "max_renders": 10,
    "cleanup_old_renders": True,
    "auto_cleanup_days": 7
}

# Initialize configuration
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as config_file:
        json.dump(DEFAULT_CONFIG, config_file, indent=4)

def load_config():
    """Load configuration from file"""
    try:
        with open(CONFIG_PATH, "r") as config_file:
            return json.load(config_file)
    except Exception:
        return DEFAULT_CONFIG

@animator_ctrl.tool()
def render_animation_script(animation_source: str) -> str:
    """Process and render the animation source code"""
    
    workspace = os.path.join(OUTPUT_FOLDER, f"animation_workspace_{int(time.time())}")  
    os.makedirs(workspace, exist_ok=True)
    source_file = os.path.join(workspace, "animation_scene.py")
    
    try:
        # Write animation source to file
        with open(source_file, "w") as file_handle:
            file_handle.write(animation_source)
        
        # Execute animation rendering
        config = load_config()
        quality_flag = "-ql" if config["quality"] == "low" else "-qm" if config["quality"] == "medium" else "-qh"
        
        cmd = [ANIM_BIN, quality_flag]
        if config["preview_mode"]:
            cmd.append("-p")
        else:
            cmd.extend(["-o", workspace])
        
        cmd.append(source_file)
        
        process_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=workspace
        )
        
        if process_result.returncode == 0:
            WORKSPACE_REGISTRY[workspace] = {
                "created_at": datetime.now().isoformat(),
                "status": "complete"
            }
            
            # Find generated files and create a report
            output_files = glob.glob(os.path.join(workspace, "*.mp4")) + \
                          glob.glob(os.path.join(workspace, "*.gif")) + \
                          glob.glob(os.path.join(workspace, "*.png"))
            
            return f"Render completed successfully. Generated files: {', '.join(output_files)}"
        else:
            WORKSPACE_REGISTRY[workspace] = {
                "created_at": datetime.now().isoformat(),
                "status": "failed"
            }
            return f"Render process failed: {process_result.stderr}"
    except Exception as e:
        return f"Error during animation processing: {str(e)}"

@animator_ctrl.tool()
def purge_workspace(workspace_path: str) -> str:
    """Remove the specified animation workspace after rendering is complete."""
    try:
        if os.path.exists(workspace_path):
            shutil.rmtree(workspace_path)
            if workspace_path in WORKSPACE_REGISTRY:
                del WORKSPACE_REGISTRY[workspace_path]
            return f"Workspace cleanup completed: {workspace_path}"
        else:
            return f"Workspace not found: {workspace_path}"
    except Exception as e:
        return f"Failed to clean workspace: {workspace_path}. Error: {str(e)}"

@animator_ctrl.tool()
def list_workspaces() -> str:
    """List all existing animation workspaces and their status."""
    try:
        workspace_folders = glob.glob(os.path.join(OUTPUT_FOLDER, "animation_workspace*"))
        result = []
        
        for workspace in workspace_folders:
            status = "registered" if workspace in WORKSPACE_REGISTRY else "untracked"
            creation_time = WORKSPACE_REGISTRY.get(workspace, {}).get("created_at", "unknown")
            
            # Check for output files
            output_files = glob.glob(os.path.join(workspace, "*.mp4")) + \
                          glob.glob(os.path.join(workspace, "*.gif")) + \
                          glob.glob(os.path.join(workspace, "*.png"))
            
            result.append({
                "path": workspace,
                "status": status,
                "created_at": creation_time,
                "output_files": len(output_files)
            })
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error listing workspaces: {str(e)}"

@animator_ctrl.tool()
def cleanup_old_workspaces(days_old: int = 7) -> str:
    """Remove workspaces older than the specified number of days."""
    try:
        current_time = time.time()
        deleted_count = 0
        
        workspace_folders = glob.glob(os.path.join(OUTPUT_FOLDER, "animation_workspace*"))
        for workspace in workspace_folders:
            # Get folder creation time
            folder_time = os.path.getctime(workspace)
            age_days = (current_time - folder_time) / (24 * 3600)
            
            if age_days > days_old:
                shutil.rmtree(workspace)
                if workspace in WORKSPACE_REGISTRY:
                    del WORKSPACE_REGISTRY[workspace]
                deleted_count += 1
        
        return f"Cleaned up {deleted_count} workspace(s) older than {days_old} days"
    except Exception as e:
        return f"Cleanup error: {str(e)}"

@animator_ctrl.tool()
def update_configuration(config_updates: str) -> str:
    """Update animation configuration settings."""
    try:
        current_config = load_config()
        updates = json.loads(config_updates)
        
        # Validate and apply updates
        for key, value in updates.items():
            if key in current_config:
                current_config[key] = value
            else:
                return f"Invalid configuration key: {key}"
        
        # Save updated configuration
        with open(CONFIG_PATH, "w") as config_file:
            json.dump(current_config, config_file, indent=4)
        
        return f"Configuration updated successfully: {json.dumps(current_config, indent=2)}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for configuration updates"
    except Exception as e:
        return f"Error updating configuration: {str(e)}"

@animator_ctrl.tool()
def save_animation_template(template_name: str, template_source: str) -> str:
    """Save an animation template for future use."""
    try:
        # Sanitize template name
        clean_name = ''.join(c for c in template_name if c.isalnum() or c in '_-')
        if not clean_name.endswith('.py'):
            clean_name += '.py'
        
        template_path = os.path.join(TEMPLATE_FOLDER, clean_name)
        
        with open(template_path, "w") as file_handle:
            file_handle.write(template_source)
        
        return f"Template saved successfully: {clean_name}"
    except Exception as e:
        return f"Error saving template: {str(e)}"

@animator_ctrl.tool()
def list_templates() -> str:
    """List all available animation templates."""
    try:
        templates = glob.glob(os.path.join(TEMPLATE_FOLDER, "*.py"))
        result = []
        
        for template_path in templates:
            template_name = os.path.basename(template_path)
            size = os.path.getsize(template_path)
            modified = datetime.fromtimestamp(os.path.getmtime(template_path)).isoformat()
            
            result.append({
                "name": template_name,
                "size_bytes": size,
                "last_modified": modified
            })
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error listing templates: {str(e)}"

@animator_ctrl.tool()
def load_template(template_name: str) -> str:
    """Load an animation template by name."""
    try:
        # Sanitize template name
        if not template_name.endswith('.py'):
            template_name += '.py'
        
        template_path = os.path.join(TEMPLATE_FOLDER, template_name)
        
        if not os.path.exists(template_path):
            return f"Template not found: {template_name}"
        
        with open(template_path, "r") as file_handle:
            content = file_handle.read()
        
        return content
    except Exception as e:
        return f"Error loading template: {str(e)}"

@animator_ctrl.tool()
def render_with_parameters(template_name: str, parameters: str) -> str:
    """Render an animation using a template and custom parameters."""
    try:
        # Load template
        template_content = load_template(template_name)
        if template_content.startswith("Template not found") or template_content.startswith("Error loading"):
            return template_content
        
        # Parse parameters
        param_dict = json.loads(parameters)
        
        # Create a workspace for this render
        workspace = os.path.join(OUTPUT_FOLDER, f"param_render_{int(time.time())}")
        os.makedirs(workspace, exist_ok=True)
        
        # Create a modified version of the template with parameters
        parameter_setup = "\n".join([f"{key} = {repr(value)}" for key, value in param_dict.items()])
        modified_template = f"""
# Parameter values
{parameter_setup}

# Original template
{template_content}
"""
        
        # Write to file and render
        source_file = os.path.join(workspace, "parameterized_scene.py")
        with open(source_file, "w") as file_handle:
            file_handle.write(modified_template)
        
        # Use the render function logic
        config = load_config()
        quality_flag = "-ql" if config["quality"] == "low" else "-qm" if config["quality"] == "medium" else "-qh"
        
        cmd = [ANIM_BIN, quality_flag, "-o", workspace, source_file]
        
        process_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=workspace
        )
        
        if process_result.returncode == 0:
            WORKSPACE_REGISTRY[workspace] = {
                "created_at": datetime.now().isoformat(),
                "status": "complete",
                "template": template_name,
                "parameters": param_dict
            }
            
            # Find generated files
            output_files = glob.glob(os.path.join(workspace, "*.mp4")) + \
                          glob.glob(os.path.join(workspace, "*.gif")) + \
                          glob.glob(os.path.join(workspace, "*.png"))
            
            return f"Parameterized render completed successfully. Files: {', '.join(output_files)}"
        else:
            return f"Render process failed: {process_result.stderr}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for parameters"
    except Exception as e:
        return f"Error in parameterized rendering: {str(e)}"

@animator_ctrl.tool()
def convert_animation_format(input_file: str, output_format: str) -> str:
    """Convert animation between formats (mp4, gif, webm)."""
    try:
        # Validate input file
        if not os.path.exists(input_file):
            return f"Input file not found: {input_file}"
        
        # Validate output format
        valid_formats = ["mp4", "gif", "webm"]
        if output_format.lower() not in valid_formats:
            return f"Invalid output format. Supported formats: {', '.join(valid_formats)}"
        
        # Create output filename
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.{output_format.lower()}"
        
        # Use ffmpeg for conversion
        ffmpeg_cmd = ["ffmpeg", "-i", input_file, output_file]
        process_result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True
        )
        
        if process_result.returncode == 0:
            return f"Conversion successful. Output saved to: {output_file}"
        else:
            return f"Conversion failed: {process_result.stderr}"
    except Exception as e:
        return f"Error during format conversion: {str(e)}"

@animator_ctrl.tool()
def extract_frames(animation_file: str, output_folder: str = None, fps: int = 5) -> str:
    """Extract frames from an animation file at specified fps."""
    try:
        # Validate input file
        if not os.path.exists(animation_file):
            return f"Animation file not found: {animation_file}"
        
        # Create output folder if not specified
        if output_folder is None:
            output_folder = os.path.join(
                os.path.dirname(animation_file), 
                f"frames_{os.path.basename(animation_file).split('.')[0]}"
            )
        
        os.makedirs(output_folder, exist_ok=True)
        
        # Extract frames using ffmpeg
        output_pattern = os.path.join(output_folder, "frame_%04d.png")
        ffmpeg_cmd = [
            "ffmpeg", 
            "-i", animation_file, 
            "-vf", f"fps={fps}", 
            output_pattern
        ]
        
        process_result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True
        )
        
        if process_result.returncode == 0:
            frame_count = len(glob.glob(os.path.join(output_folder, "frame_*.png")))
            return f"Extracted {frame_count} frames to {output_folder}"
        else:
            return f"Frame extraction failed: {process_result.stderr}"
    except Exception as e:
        return f"Error during frame extraction: {str(e)}"

if __name__ == "__main__":
    animator_ctrl.run(transport="stdio")
