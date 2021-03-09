# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# This code is written based on the offical blender addon import-export STL format 
# written by Guillaume Bouchard.

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import Operator

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper,
    axis_conversion,
)
bl_info = {
    "name": "OpenFOAM stl Exporter",
    "author": "Arman Safdari",
    "version": (1, 0, 0),
    "blender": (2, 82, 0),
    "location": "3D View > 'Export OF' tab",
    "description": "Export stl file for OpenFOAM",
    "category": "Mesh",
}


def write_some_data(context, filepath, use_some_setting):
    print("running write_some_data...")
    f = open(filepath, 'w', encoding='utf-8')
    f.write("Hello World %s" % use_some_setting)
    f.close()

    return {'FINISHED'}
    
    
@orientation_helper(axis_forward='Y', axis_up='Z')
class ExportSomeData(Operator, ExportHelper):
    bl_idname = "export_stl_openfoam.stl"  
    bl_label = "Export STL "
    bl_description = """Export STL file in ASCII file format for OpenFOAM"""

    filename_ext = ".stl"
    filter_glob: StringProperty(
        default="*.stl",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selection objects only",
        default=False,
    )
    use_mesh_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply the modifiers before saving",
        default=True,
    )    
    global_scale: FloatProperty(
        name="Scale",
        min=0.000001, 
        default=1.0,
    )    
    def execute(self, context):
        import os
        import itertools
        from mathutils import Matrix
        from . import export
        keywords = self.as_keywords(
          ignore=(
                  "axis_forward",
                  "axis_up",
                  "check_existing", 
                  "filter_glob",
                  "use_selection",
                  "global_scale",
                  "use_mesh_modifiers",
                  ),
        )   

        scene = context.scene
        if self.use_selection:
                data_seq = context.selected_objects
        else:
                data_seq = scene.objects 
                            
        global_scale = self.global_scale
        global_matrix = axis_conversion(
            to_forward=self.axis_forward,
            to_up=self.axis_up,
        ).to_4x4() @ Matrix.Scale(global_scale, 4)
        
        prefix = os.path.splitext(self.filepath)[0]
        keywords_temp = keywords.copy()
        
        if os.path.exists( prefix + ".stl"):
             os.remove( prefix + ".stl")
           
        for ob in data_seq:
           faces = export.faces_from_mesh(ob, global_matrix, self.use_mesh_modifiers)
           keywords_temp["filepath"] = prefix + ".stl"
           keywords_temp["ObjectName"] = bpy.path.clean_name(ob.name)
           export.write_stl_for_OpenFOAM(faces=faces, **keywords_temp)
        return {'FINISHED'}  



class STL_For_OpenFOAM(bpy.types.Panel):
	
    bl_label = "Export for OpenFOAM"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Export OF"

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.export_stl_openfoam", text="Export STL")

# Export
class MESH_OP_STL_For_OpenFOAM(bpy.types.Operator):
    bl_idname = "mesh.export_stl_openfoam"
    bl_label = "Export STL format for OpenFoam"
    bl_description = "Export objects as stl format for OpenFOAM"

    def execute(self, context):
        bpy.ops.export_stl_openfoam.stl('INVOKE_DEFAULT')
        return {'FINISHED'}


def register():
	bpy.utils.register_class(STL_For_OpenFOAM)
	bpy.utils.register_class(MESH_OP_STL_For_OpenFOAM)
	bpy.utils.register_class(ExportSomeData)


def unregister():
	bpy.utils.unregister_class(STL_For_OpenFOAM)
	bpy.utils.unregister_class(MESH_OP_STL_For_OpenFOAM)
	bpy.utils.unregister_class(ExportSomeData)



if __name__ == "__main__":
    register()
