import os

# supposed to be run from KAGMapMaker/.scripts
scripts_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
os.chdir(project_root)

os.system("pyinstaller --onefile --name KAGMapMaker --specpath . --hidden-import=tkinter app.py")

PATHS = ["utils", "settings", "core", "base", "modded"]
BLACKLIST = ["__pycache__", "__init__.py", ".venv"]

# collect all files
added_files = []
for root, _, files in os.walk(project_root):
    if any(path in root for path in PATHS) and not any(path in root for path in BLACKLIST):
        for f in files:
            src_path = os.path.join(root, f)
            rel_path = os.path.relpath(root, project_root)
            added_files.append((src_path, rel_path))

# modify the spec file
spec_file = "KAGMapMaker.spec"
with open(spec_file, "r", encoding="utf-8") as f:
    spec_contents = f.readlines()

# insert data files into the "Analysis" section
for i, line in enumerate(spec_contents):
    if line.strip().startswith("datas="):
        spec_contents[i] = f"    datas={added_files},\n"
        break

# write back the modified spec file
with open(spec_file, "w", encoding="utf-8") as f:
    f.writelines(spec_contents)

os.system(f'pyinstaller KAGMapMaker.spec --clean --distpath="{scripts_dir}"')
