import os

PATH = r"C:\Program Files (x86)\Steam\steamapps\common\King Arthur's Gold\Base\Entities"
filelist = []
for root, dirs, files in os.walk(PATH):
    for file in files:
        if "cfg" in file:
            filelist.append(file)

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "itemlist.txt"), "w+", encoding="utf-8") as f:
    for item in filelist:
        f.write(item + "\n")