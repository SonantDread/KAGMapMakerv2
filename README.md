# KAGMapMakerV2

<p align="center">
  <a href="http://unlicense.org/">
    <img alt="License: Unlicense" src="https://img.shields.io/badge/license-Unlicense-blue.svg">
  </a>
</p>

A tool for creating maps for the game King Arthur's Gold.

---

## Installation Guide

There are three ways to get the application.

### Method 1: The Easy Way (Recommended)

Download a single executable file that has everything included. **You do not need to install Python.**

1.  Go to the **[Latest Release Page](https://github.com/SonantDread/KAGMapMakerv2/releases/latest)**.
2.  Under the "Assets" section, download the correct file for your operating system:
    *   For **Windows**: Download `KAGMapMaker.exe`
    *   For **Linux**: Download `KAGMapMaker`
3.  Run the downloaded file.
    *   *On Linux, you may need to make the file executable first by opening a terminal and running: `chmod +x KAGMapMaker`*

### Method 2: From Source with Helper Scripts

Use this method if you have **Python 3.8+ installed** on your system. Note that this project was made using 3.12.3.

1.  Download the project source by clicking the green **"< > Code"** button on the GitHub page, then **"Download ZIP"**.
2.  Unzip the folder.
3.  Run the application:
    *   On **Windows**, double-click the `run.bat` file.
    *   On **Linux/macOS**, open a terminal in the project folder and run: `./run.sh`

> **Note for Linux Users:** Before running the script, you must install the `tkinter` package:
> *   On Debian/Ubuntu: `sudo apt-get install python3-tk`
> *   On Fedora/RHEL: `sudo dnf install python3-tkinter`

### Method 3: For Developers (Manual Setup)

This method is for developers who want to modify the code. You will need `git` and Python 3.8+ installed.

1.  Clone the repository: `git clone https://github.com/SonantDread/KAGMapMakerv2.git`
2.  Navigate into the directory: `cd KAGMapMakerv2`
3.  Use your preferred tool to set up the environment:
    *   **Using `uv` (Fastest):** `uv venv && uv sync`
    *   **Using `pip`:** `python -m venv .venv && pip install -r requirements.txt`
4.  Run the application: `python app.py`

---

## Creating Custom Content (Mods)

You can extend KAGMapMaker by adding your own custom content. To do this, you will need the project's source code (see Installation Method 2 or 3).

1.  Create a folder named `Modded` in the project's root directory.
2.  Inside `Modded`, create another folder for your mod (e.g., `MyAwesomeMod`). The name can be anything that does **not** start with an underscore `_`.
3.  Inside your mod's folder, create a `.json` file to define your items.

#### Item Definition (`.json` file)

Below is an example for a custom "Sand" tile. You can add multiple items to a single JSON file by putting them in the main list `[ ... ]`.

```json
[
  {
    "type": "tile",
    "name": "sand",
    "display_name": "Sand",
    "sprite": {
        "image": 183,
        "z": 499
    },
    "pixel_data": {
      "colors": {
        "rotation0_team0": [
            255,
            236,
            213,
            144
          ]
        }
    }
  }
]
```

> **Note:** The table below explains the most common fields. For a complete list of all possible properties and their advanced behaviors, developers can refer to the `base/CItem.py` file in the source code.

**Key Fields Explained:**

| Field | Description |
| :--- | :--- |
| `type` | The internal type of the item (e.g., `tile`, `blob`). This decides which tab to place it in. If left blank, the item will go to the `Other` tab. |
| `name` | A unique, lowercase ID for your item. No spaces or special characters. |
| `display_name` | The name that appears in the editor's UI for users to see. |
| `sprite.image` | The numeric ID of the sprite from `world.png` (interpreted as 8x8 sprites). Can also be a `.png` file. |
| `sprite.z` | The drawing layer (z-index). Higher numbers are drawn on top of lower numbers. |
| `pixel_data` | Contains the raw color data for the map file. The `colors` object holds the RGBA value `[Red, Green, Blue, Alpha]`. |

3. After writing your own file and saving it, run the application and locate the "Modded" tab. The item you created should be placed underneath the `type` you created it as. If not, check the `Other` tab.

Need help? Contact `sonantdread` on Discord. If you don't know how to code, I can also create the files for you.

---
## How to Contribute

Contributions are welcome! If you have found a bug or have a feature request, please open an issue on the [GitHub Issues page](https://github.com/SonantDread/KAGMapMakerv2/issues). Before creating an issue, please refer to [the TODO list](https://github.com/users/SonantDread/projects/3/views/1) for the project.

---

## Acknowledgements

*   **[TerminalHash](https://github.com/TerminalHash)** for locating bugs and testing on Linux.
*   **[Guift](https://github.com/Kuift)** for the original main canvas.py functions.
*   **[NoahTheLegend](https://github.com/NoahTheLegend)** for providing code that lets you sync data between all initialized classes.

---

## License

This project is released into the public domain. See the [LICENSE](LICENSE) file for details.