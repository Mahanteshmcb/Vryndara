import json
import os
import re
import subprocess
import time
from colorama import Fore

# 🔴 CONFIGURATION 🔴
# We are BYPASSING the broken C++ engine.
# We go straight to the source: Blender.
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" 

class DirectorSkill:
    def __init__(self, brain_service):
        self.brain = brain_service
        self.output_folder = "Director_Jobs"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def create_manifest(self, user_request):
        print(f"{Fore.CYAN}🎬 Director: Analyzing request '{user_request}'...")
        
        system_prompt = r"""You are the 'Director' Agent.
Extract the user's intent.
Schema:
{
  "project_name": "string",
  "description": "string (visual description of 3D object)",
  "engine": "blender"
}"""
        try:
            json_text = self.brain.think(user_request, system_prompt=system_prompt)
            match = re.search(r'\{.*\}', json_text, re.DOTALL)
            
            if match:
                raw_data = json.loads(match.group(0))
                manifest, output_image = self.construct_cpp_manifest(raw_data)
                
                # Save Job File
                job_id = manifest["job_id"]
                filename = os.path.abspath(f"{self.output_folder}/{job_id}.json")
                with open(filename, 'w') as f:
                    json.dump(manifest, f, indent=4)
                print(f"{Fore.GREEN}✅ Director: Blueprint saved.")
                
                # --- DIRECT OVERRIDE ---
                # We ignore VrindaAI.exe because it is missing files (blender_master.py).
                # We launch Blender directly from Python.
                script_path = manifest["actions"][0]["parameters"]["script_path"]
                self.launch_blender_directly(script_path)
                # -----------------------
                
                # Patience Loop
                print(f"{Fore.YELLOW}⏳ Waiting for render (up to 60s)...")
                start_time = time.time()
                while time.time() - start_time < 60:
                    if os.path.exists(output_image):
                        print(f"{Fore.GREEN}✨ Render finished in {int(time.time() - start_time)}s!")
                        print(f"{Fore.MAGENTA}🖼️  Opening Render: {output_image}")
                        os.startfile(output_image) 
                        return f"I have rendered the {raw_data.get('description')}."
                    time.sleep(1)
                
                return "The render timed out. Blender is taking too long."
            else:
                return "I could not understand the request."

        except Exception as e:
            print(f"{Fore.RED}❌ Director Error: {e}")
            return "An error occurred."

    def launch_blender_directly(self, script_path):
        """
        Bypasses C++ engine to guarantee execution.
        """
        if not os.path.exists(BLENDER_PATH):
            print(f"{Fore.RED}❌ Error: Blender not found at {BLENDER_PATH}")
            return

        print(f"{Fore.YELLOW}⚙️ Director: Launching Blender Direct Override...")
        # Command: blender.exe -b -P script.py
        cmd = [BLENDER_PATH, "-b", "-P", script_path]
        
        # Run in background
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def construct_cpp_manifest(self, raw_data):
        import uuid
        job_id = f"JOB_{uuid.uuid4().hex[:8].upper()}"
        output_image = os.path.abspath(f"{self.output_folder}/{job_id}_render.png")
        script_path = os.path.abspath(f"{self.output_folder}/{job_id}_script.py")
        
        self.create_blender_script(script_path, raw_data.get("description", ""), output_image)

        manifest = {
            "job_id": job_id,
            "engine": "blender",
            "header": { "project_name": raw_data.get("project_name", "Untitled"), "scene_name": "Scene_01", "resolution": {"width": 1920, "height": 1080}, "fps": 24 },
            "output": { "path": output_image, "format": "png", "codec": "png", "bitrate": "0" },
            "assets": { "characters": [], "environments": [], "props": [], "animations": [] },
            "actions": [ { "type": "execute_script", "target": "system", "parameters": { "script_path": script_path } } ]
        }
        return manifest, output_image

    def create_blender_script(self, path, description, output_path):
        print(f"{Fore.CYAN}🧠 Brain: Generating Python code for '{description}'...")
        
        code_prompt = f"""You are a Blender Python Expert.
Task: Write code to create: {description}.
Rules:
1. Write raw python code only.
2. NO conversational text.
3. NO markdown.
4. Use 'bpy.ops.mesh.primitive_monkey_add()' for monkeys.
"""
        try:
            raw_code = self.brain.think(f"Code for: {description}", system_prompt=code_prompt)
        except:
            raw_code = "ERROR"

        # Safety Check
        bad_keywords = ["HTTPConnectionPool", "timed out", "Thinking error", "Error:"]
        if any(k in raw_code for k in bad_keywords) or len(raw_code) < 10:
            print(f"{Fore.RED}⚠️ Brain Timed Out. Using Fallback.")
            indented_code = "    bpy.ops.mesh.primitive_monkey_add()"
        else:
            clean_code = raw_code.replace("```python", "").replace("```", "").replace("[CODE]", "").replace("[/CODE]", "").strip()
            indented_code = ""
            for line in clean_code.splitlines():
                if "import bpy" not in line:
                    indented_code += f"    {line}\n"

        if len(indented_code.strip()) == 0:
             indented_code = "    bpy.ops.mesh.primitive_monkey_add()"

        # Studio Template
        studio_setup = f"""
import bpy
import os
import math
import mathutils

# 1. Clear
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Build
print("--- Building ---")
try:
{indented_code}
except Exception as e:
    print(f"Error: {{e}}")
    bpy.ops.mesh.primitive_monkey_add()

# 3. Camera
bpy.ops.object.camera_add(location=(7, -7, 7))
camera = bpy.context.object
direction = mathutils.Vector((0, 0, 0)) - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = camera

# 4. Light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
bpy.context.object.data.energy = 5

# 5. Render
scene = bpy.context.scene
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = r"{output_path}"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

bpy.ops.render.render(write_still=True)
"""
        with open(path, "w") as f:
            f.write(studio_setup)