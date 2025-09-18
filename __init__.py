import copy
import os
import pathlib
import re

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

bl_info = {
    "name": "URDF Exporter",
    "category": "Import-Export",
    "author": "Iñigo Moreno i Caireta",
    "version": (1, 0, 3),
    "blender": (3, 0, 1),
    "location": "File > Export > URDF",
    "description": "Exports a URDF file from the current Blender scene",
}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.


class URDFExporter(Operator, ExportHelper):
    """URDF Exporter"""
    bl_idname = "export.urdf"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "URDF Exporter"

    # ExportHelper mixin class uses this
    filename_ext = ".xacro"

    filter_glob: StringProperty(
        default="*.xacro",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    xacro_setting: BoolProperty(
        name="Xacro Macro",
        description="Whether it should be a macro",
        default=True,
    )

    collision_setting: BoolProperty(
        name="Asume Collision Geometry will be added later",
        description="Wether to add assume that the collision geometry will be added later",
        default=True,
    )

    def execute(self, context):
        from . import urdf

        filepath = pathlib.Path(self.filepath)
        blend_file_path = pathlib.Path(bpy.data.filepath)
        package_path = filepath.parent
        while not package_path.joinpath('package.xml').exists():
            package_path = package_path.parent
            if package_path == package_path.parent:
                package_path = None
                break
        # package_path = pathlib.Path("/home/110359@TRI.LAN/ros/jazzy/jarvis_ws/src/jarvis_workcell/jarvis_workcell")
        if package_path is None:
            directory = filepath.parent
            urdf_path = filepath
        else:
            directory = package_path.joinpath('meshes', 'visual')
            urdf_path = filepath
        if self.xacro_setting:
            prefix = "$\\{prefix\\}"
            base_link = "base_link"
        else:
            prefix = ""
            base_link = "world"

        directory.mkdir(exist_ok=True)

        for obj in bpy.data.objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
        #    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        robot = urdf.Robot(blend_file_path.stem)
        robot(urdf.Link(prefix + base_link))
        for obj in bpy.data.objects:
            obj.name = obj.name.lower().replace(' ', '_')
            link_args = [prefix + obj.name]
            file = str(directory.joinpath(f'{obj.name}.dae'))
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            if obj.type != 'EMPTY':
                prev_matrix = copy.deepcopy(obj.matrix_world)
                prev_parent = None
                if obj.parent is not None:
                    prev_parent = obj.parent.name
                obj.matrix_world = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
                obj.parent = None
                bpy.ops.wm.collada_export(filepath=file, selected=True)
                if prev_parent is not None:
                    obj.parent = bpy.data.objects[prev_parent]
                obj.matrix_world = prev_matrix

                if package_path is not None:
                    file = file.replace(str(package_path), f'package://{package_path.stem}')

                link_args.append(urdf.Visual(urdf.Geometry(urdf.Mesh(filename=file))))
                collision_file = file
                if self.collision_setting:
                    collision_file = file.replace('.dae', '.stl').replace('visual', 'collision')
                link_args.append(urdf.Collision(urdf.Geometry(urdf.Mesh(filename=collision_file))))

            robot(urdf.Link(*link_args))
            parent = base_link
            if obj.parent is not None:
                parent = obj.parent.name
            robot(urdf.Joint(
                prefix + obj.name,
                urdf.Parent(prefix + parent),
                urdf.Child(prefix + obj.name),
                urdf.Origin(xyz=list(obj.matrix_local.to_translation()), rpy=list(obj.matrix_local.to_euler())),
                type='fixed',
            ))

        urdf_string = str(robot)

        if self.xacro_setting:
            urdf_string = re.sub(
                r'<robot[ ]+name="([^"]+)"',
                r'<robot xmlns:xacro="http://wiki.ros.org/xacro">\n<xacro:macro name="\1" params="prefix=\1_"',
                urdf_string)
            urdf_string = re.sub(r'<\/robot>', r'</xacro:macro>\n</robot>', urdf_string)
            urdf_string = re.sub(r'\\{', '{', urdf_string)
            urdf_string = re.sub(r'\\}', '}', urdf_string)

        urdf_path.write_text(urdf_string)

        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(URDFExporter.bl_idname, text="Universal Robot Description Format (.urdf)")

# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access)


def register():
    bpy.utils.register_class(URDFExporter)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(URDFExporter)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
