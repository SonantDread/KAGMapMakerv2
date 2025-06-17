import os
import subprocess
import sys

# --- script Setup ---
# ensures the script runs from the project's root directory
scripts_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(scripts_dir, "../"))
os.chdir(project_root)

print(f"Running script from: {project_root}", flush=True)

# --- configuration ---
spec_file_name = "KAGMapMaker.spec"
app_entry_point = "app.py"

# --- step 1: generate the .spec file WITHOUT a full build ---
print("Generating initial .spec file with pyi-makespec...", flush=True)
# this command is fast and only creates the .spec file
makespec_command = [
    "pyi-makespec",
    "--onefile",
    "--name=KAGMapMaker",
    f"--specpath={project_root}",
    "--hidden-import=tkinter",
    app_entry_point
]
# we use subprocess.run for better error handling than os.system
subprocess.run(makespec_command, check=True)
print(".spec file generated successfully.", flush=True)


# --- step 2: collect all the data files we want to bundle ---
print("Collecting data files...", flush=True)
PATHS = ["utils", "settings", "core", "base", "modded"]
BLACKLIST = ["__pycache__", "__init__.py", ".venv"]

added_files = []
for path_to_include in PATHS:
    for root, _, files in os.walk(os.path.join(project_root, path_to_include)):
        # skip any blacklisted directories
        if any(bl_item in root for bl_item in BLACKLIST):
            continue
        for f in files:
            src_path = os.path.join(root, f)
            # the destination path should be relative to the project root
            rel_path = os.path.relpath(root, project_root)
            added_files.append((src_path, rel_path))

print(f"Collected {len(added_files)} data files.", flush=True)


# --- step 3: modify the .spec file to include the data files ---
print("Modifying .spec file...", flush=True)
with open(spec_file_name, "r", encoding="utf-8") as f:
    spec_contents = f.readlines()

# find the line 'datas=[]' and replace it with our collected files
for i, line in enumerate(spec_contents):
    if line.strip().startswith("datas="):
        # format the list of tuples correctly for the spec file
        spec_contents[i] = f"datas={added_files},\n"
        break
else:
    # this else block runs if the for loop completes without `break`
    print(f"ERROR: Could not find 'datas=' line in {spec_file_name}", file=sys.stderr)
    sys.exit(1)

# write the changes back to the file
with open(spec_file_name, "w", encoding="utf-8") as f:
    f.writelines(spec_contents)
print(".spec file modified successfully.", flush=True)


# --- step 4: run the FINAL build using the modified .spec file ---
print("Building final executable from .spec file...", flush=True)
# this is the first and ONLY time the full build runs
build_command = [
    "pyinstaller",
    spec_file_name,
    "--clean", # clean cache and previous builds
    f'--distpath={scripts_dir}' # output to the .scripts folder
]
subprocess.run(build_command, check=True)

print("\nBuild successful!", flush=True)
print(f"Executable created in: {scripts_dir}", flush=True)