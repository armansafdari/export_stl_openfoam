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

# <pep8-80 compliant>

# This code is written based on offical blender addon import-export STL format 
# written by Guillaume Bouchard.

import bpy

def _ascii_write_for_OpenFOAM(ObjectName, filepath, faces):
    from mathutils.geometry import normal

    with open(filepath, 'a') as data:
        fw = data.write
        fw('solid %s\n' % ObjectName)

        for face in faces:
            # calculate face normal
            fw('facet normal %f %f %f\nouter loop\n' % normal(*face)[:])
            for vert in face:
                fw('vertex %f %f %f\n' % vert[:])
            fw('endloop\nendfacet\n')

        fw('endsolid %s\n' % ObjectName)


def write_stl_for_OpenFOAM(ObjectName="",filepath="", faces=(), ascii=False):
    _ascii_write_for_OpenFOAM(ObjectName, filepath, faces)





def faces_from_mesh(ob, global_matrix, use_mesh_modifiers=False):

    import bpy

    # get the editmode data
    if ob.mode == "EDIT":
        ob.update_from_editmode()

    # get the modifiers
    if use_mesh_modifiers:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        mesh_owner = ob.evaluated_get(depsgraph)
    else:
        mesh_owner = ob

    # Object.to_mesh() is not guaranteed to return a mesh.
    try:
        mesh = mesh_owner.to_mesh()
    except RuntimeError:
        return

    if mesh is None:
        return

    mat = global_matrix @ ob.matrix_world
    mesh.transform(mat)
    if mat.is_negative:
        mesh.flip_normals()
    mesh.calc_loop_triangles()

    vertices = mesh.vertices

    for tri in mesh.loop_triangles:
        yield [vertices[index].co.copy() for index in tri.vertices]

    mesh_owner.to_mesh_clear()

