import bpy
import bmesh
import math
import mathutils

def area_quad(v1, v2, v3, v4):
    """Calculate the area of a quad by dividing it into two triangles."""
    return mathutils.geometry.area_tri(v1, v2, v3) + mathutils.geometry.area_tri(v1, v3, v4)

def scale_uv_to_match_texture(obj, pixel_per_meter=32, texture_size=128, angle_threshold=5.0):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    if not mesh.uv_layers.active:
        print(f"{obj.name} 没有UV映射。")
        bpy.ops.object.mode_set(mode='OBJECT')
        return
    
    uv_layer = bm.loops.layers.uv.active
    texture_meter_size = texture_size / pixel_per_meter
    angle_rad_threshold = math.radians(angle_threshold)

    def get_adjacent_faces(face):
        for edge in face.edges:
            for linked_face in edge.link_faces:
                if linked_face != face:
                    yield linked_face

    visited_faces = set()
    
    for face in bm.faces:
        if face in visited_faces:
            continue
        
        connected_faces = set([face])
        queue = [face]
        
        while queue:
            current_face = queue.pop()
            visited_faces.add(current_face)
            face_normal = current_face.normal
            for adj_face in get_adjacent_faces(current_face):
                if adj_face in visited_faces:
                    continue
                angle = face_normal.angle(adj_face.normal)
                if angle < angle_rad_threshold:
                    connected_faces.add(adj_face)
                    queue.append(adj_face)
        
        # Process connected faces
        world_verts = [obj.matrix_world @ v.co for f in connected_faces for v in f.verts]
        face_area_world = 0.0
        face_area_uv = 0.0

        uv_coords = []

        for f in connected_faces:
            verts = [obj.matrix_world @ v.co for v in f.verts]
            uvs = [l[uv_layer].uv.copy() for l in f.loops]
            num_verts = len(verts)

            if num_verts == 3:
                face_area_world += mathutils.geometry.area_tri(*verts)
                face_area_uv += mathutils.geometry.area_tri(*uvs)
            elif num_verts == 4:
                face_area_world += area_quad(*verts)
                face_area_uv += area_quad(*uvs)
            else:
                print(f"警告: 对象 {obj.name} 包含非三角形或四边形面，跳过该面。")
                continue

            uv_coords.extend(uvs)

        if face_area_world <= 0:
            print(f"警告: 对象 {obj.name} 的一组相连面具有零或负的世界面积，跳过该组。")
            continue

        if face_area_uv <= 0:
            print(f"警告: 对象 {obj.name} 的一组相连面具有零或负的 UV 面积，跳过该组。")
            continue

        current_pixel_density = face_area_uv / face_area_world
        target_pixel_density = 1.0 / (texture_meter_size ** 2)
        scale_uv_factor = math.sqrt(target_pixel_density / current_pixel_density)

        center_uv = sum(uv_coords, mathutils.Vector((0, 0))) / len(uv_coords)

        for f in connected_faces:
            for loop in f.loops:
                loop_uv = loop[uv_layer].uv
                loop_uv.x = (loop_uv.x - center_uv.x) * scale_uv_factor + center_uv.x
                loop_uv.y = (loop_uv.y - center_uv.y) * scale_uv_factor + center_uv.y

    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode='OBJECT')

def unwrap_and_fit_uv(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    # Check that there is a UV map and ensure it is initialized
    if not mesh.uv_layers:
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    
    # Get the active UV layer
    uv_layer = bm.loops.layers.uv.active

    # Manually unwrap and position the UVs within [0, 1] range
    # Note: Adjust the unwrap algorithm or parameters if needed
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    
    # Find the bounding box of the UVs
    min_uv = [float('inf'), float('inf')]
    max_uv = [float('-inf'), float('-inf')]
    
    for face in bm.faces:
        for loop in face.loops:
            uv = loop[uv_layer].uv
            if uv.x < min_uv[0]:
                min_uv[0] = uv.x
            if uv.y < min_uv[1]:
                min_uv[1] = uv.y
            if uv.x > max_uv[0]:
                max_uv[0] = uv.x
            if uv.y > max_uv[1]:
                max_uv[1] = uv.y

    # Determine the scale and translation needed to fit UVs in the [0, 1] range
    uv_scale = 1.0 / max(max_uv[0] - min_uv[0], max_uv[1] - min_uv[1])
    uv_offset = [-min_uv[0] * uv_scale, -min_uv[1] * uv_scale]

    # Apply scaling and translation to each UV
    for face in bm.faces:
        for loop in face.loops:
            loop_uv = loop[uv_layer].uv
            loop_uv.x = loop_uv.x * uv_scale + uv_offset[0]
            loop_uv.y = loop_uv.y * uv_scale + uv_offset[1]

    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode='OBJECT')

class UVformater(bpy.types.Operator):
    bl_idname = "object.uv_formater"
    bl_label = "uv统一规格尺寸"
    bl_description = "批量调整选中对象中的 UV 映射"
    bl_options = {'REGISTER', 'UNDO'}

    pixel_per_meter: bpy.props.IntProperty(
        name="像素/米",
        default=32,
        min=1,
        description="每米的像素数"
    )

    texture_size: bpy.props.IntProperty(
        name="纹理尺寸",
        default=128,
        min=1,
        description="纹理的像素尺寸"
    )

    angle_threshold: bpy.props.FloatProperty(
        name="角度阈值",
        default=5.0,
        min=0.0,
        max=180.0,
        description="在组内合并处理面时的最大角度差"
    )

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH':
                scale_uv_to_match_texture(obj, self.pixel_per_meter, self.texture_size, self.angle_threshold)
            else:
                self.report({'WARNING'}, f"{obj.name} 不是一个网格对象，跳过。")
        return {'FINISHED'}

class UVUnwrapper(bpy.types.Operator):
    bl_idname = "object.uv_unwrapper"
    bl_label = "UV展开并适配至UV边界"
    bl_description = "对所选对象展开UV并调整UV坐标以覆盖整个UV空间"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH':
                unwrap_and_fit_uv(obj)
            else:
                self.report({'WARNING'}, f"{obj.name} 不是一个网格对象，跳过。")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(UVUnwrapper)
    bpy.utils.register_class(UVformater)

def unregister():
    bpy.utils.unregister_class(UVUnwrapper)
    bpy.utils.unregister_class(UVformater)