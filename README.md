# URDF Exporter for Blender

**Author:** Iñigo Moreno i Caireta
**Version:** 1.0.2
**Blender Compatibility:** 3.0.1 and later
**Category:** Import–Export

This Blender add-on exports the current Blender scene to a
[URDF](http://wiki.ros.org/urdf) (Universal Robot Description Format) or
[xacro](http://wiki.ros.org/xacro) file, suitable for use in ROS/ROS 2
robot projects.

It automatically:

* Creates a URDF robot model from all objects in the scene.
* Exports each object’s geometry to Collada (`.dae`) files.
* Generates `Visual` and (optionally) `Collision` elements for each link.
* Converts **all Blender parent-child relationships into fixed joints** in the URDF.
* Searches upward for a `package.xml` to convert paths to `package://` URIs.
* Can wrap the URDF in a Xacro macro for easy reuse.

---

## Installation

1. **Download the add-on ZIP** directly from GitHub: <https://github.com/InigoMoreno/blender-urdf-exporter/archive/refs/heads/main.zip>

2. **Install in Blender**

* In Blender, go to **Edit → Preferences → Add-ons → Install…**
* Select the downloaded ZIP file (do not extract).
* Enable **URDF Exporter** in the add-on list.

---

## Usage

1. Open or create a Blender scene containing the robot model.
2. Go to **File → Export → URDF**.
3. Choose a destination `.xacro` (or `.urdf`) file.
4. Options:
* **Xacro Macro** – wrap output in a Xacro macro.
* **Assume Collision Geometry Will Be Added Later** – use `.stl` placeholders in a `collision` folder.

The exporter will:

* Apply object scale transforms.
* Export each non-empty object to a Collada file (`.dae`) under `meshes/visual`
inside the detected ROS package (or next to the chosen URDF if no package is
found).
* Convert **all parent-child relationships in Blender** into **fixed joints** in the URDF.
* Build a valid URDF or Xacro file referencing those meshes.
