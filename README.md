# LibreWall Wallpaper Library

Welcome to the official wallpaper library for **LibreWall**. This repository hosts a collection of 3D, interactive, and reactive wallpapers designed to run on the LibreWall engine.

## 📂 Repository Structure

Each folder in this repository represents a standalone theme. To use a theme, simply download the specific folder and place it in your LibreWall `wallpapers/` directory.

### Standard Theme Structure
A valid theme folder must contain:
* `config.json`: The core configuration file controlling visuals, lighting, and behavior.
* **Assets**: Your 3D models (`.glb`/`.gltf`), background images/videos (`.mp4`, `.jpg`), and textures.
* *(Optional)* `style.css`: Custom styling for HTML widgets.
* *(Optional)* `widget.html`: Custom HTML overlay elements.
* *(Optional)* `logic.js`: Custom JavaScript for unique interactions.

## 🚀 How to Submit a Wallpaper

We welcome community contributions! If you have created a stunning 3D scene or a useful widget dashboard, submit it to the library.

### Submission Guidelines
1.  Ensure your wallpaper includes all necessary assets (models, textures, etc.).
2.  Optimize your 3D models (use Draco compression if possible) to keep file sizes reasonable.
3.  Include a `thumbnail.png` (1920x1080 preferred) in your folder for the selector UI.
4.  Verify that your `config.json` is valid JSON.

### 📧 Submission Method
Zip your wallpaper folder and email it to:
**librewall@dkydivyansh.com**

Please include:
* Theme Name
* Author Name
* A brief description

## ⚙️ Configuration Documentation

LibreWall is highly customizable. You can control lighting, post-processing (Bloom), shadows, and camera interaction purely through JSON.

Check `example_config.json` in this repository for a complete list of all available variables and what they do.

## 🛠️ Global Widgets

LibreWall supports **Global Widgets** (System Monitor, Network Traffic, etc.).
To enable the system-wide overlay instead of a theme-specific widget, set the following in your config:
```json
"Enable_Global_Widget": true
````

-----

*Maintained by Dkydivyansh*
