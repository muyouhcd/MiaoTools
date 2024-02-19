import bpy
import random
import bmesh
import mathutils
import collections
import os
import math
import time
from bpy.types import Menu
from mathutils import Matrix
from mathutils import Vector
from collections import defaultdict
import re
from mathutils.bvhtree import BVHTree
import numpy as np
from bpy.props import PointerProperty
from bpy.types import Operator, Panel, Collection
from bpy.props import EnumProperty
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
from mathutils import kdtree



# class ParentBoneMatcher(bpy.types.Operator):
#     """Match bones' parent-child relations to a template armature"""
#     bl_idname = "object.parent_bone_matcher"
#     bl_label = "Parent Bone Matcher"
#     bl_options = {'REGISTER', 'UNDO'}

#     template_armature_name: bpy.props.StringProperty(
#         name="Template Armature Name",
#         default="Bip001"
#     )

#     def execute(self, context):
#         # 获取模板骨架
#         template_armature = bpy.data.objects.get(self.template_armature_name)
        
#         # 判断模板骨架是否存在
#         if not template_armature or template_armature.type != 'ARMATURE':
#             self.report({'ERROR'}, "Template armature not found or not an armature.")
#             return {'CANCELLED'}

#         # 当前活动骨架的编辑骨骼和它们的父骨骼名字映射
#         bone_parent_map = {}
#         context.view_layer.objects.active = template_armature
#         bpy.ops.object.mode_set(mode='EDIT')
#         for bone in template_armature.data.edit_bones:
#             bone_parent_map[bone.name] = bone.parent.name if bone.parent else None
#         bpy.ops.object.mode_set(mode='OBJECT')

#         # 遍历所有的骨架，调整对应骨骼的父子关系
#         for obj in bpy.data.objects:
#             if obj.type == 'ARMATURE' and obj.name != self.template_armature_name:
#                 context.view_layer.objects.active = obj
#                 bpy.ops.object.mode_set(mode='EDIT')
#                 for bone_name, parent_name in bone_parent_map.items():
#                     if bone_name in obj.data.edit_bones:
#                         bone = obj.data.edit_bones[bone_name]
#                         bone.parent = obj.data.edit_bones.get(parent_name) if parent_name else None
#                 bpy.ops.object.mode_set(mode='OBJECT')
#         return {'FINISHED'}
    

# # 这是您现有插件中的一个操作类
# class MyAddonExistingOperator(bpy.types.Operator):
#     """My Existing Operator Tooltip"""
#     bl_idname = "object.my_addon_existing_operator"
#     bl_label = "My Existing Operator"
    
#     # 现有操作的属性可以在这里定义
#     # 示例属性：一个字符串属性
#     my_string_prop: bpy.props.StringProperty(name="Some String")

#     # 示例属性：一个整数属性
#     my_int_prop: bpy.props.IntProperty(name="Some Integer")

#     # 操作类的方法和逻辑
#     def execute(self, context):
#         # 这里是现有操作的执行代码
#         # 假设我们只是打印属性值到控制台
#         print("String Property:", self.my_string_prop)
#         print("Integer Property:", self.my_int_prop)

#         # 您可以在这里添加更多自定义逻辑，比如操作数据或者调用其他函数

#         # 最后，返回执行状态
#         return {'FINISHED'}
    
#     # 可选：操作的相关UI（如果操作类有自己专属的面板或者需要交互的属性）
#     def invoke(self, context, event):
#         # 调用默认属性填写界面
#         return context.window_manager.invoke_props_dialog(self)

#     # 可选：操作前/后的准备和清理工作
#     @classmethod
#     def poll(cls, context):
#         # 这里可以设置操作是否可用的条件，例如判断选中了某个特定类型的对象
#         return context.active_object is not None



#原点批量移动至-y中心
class OBJECT_OT_move_object_origin_to_bottom(Operator):
    bl_idname = "object.move_origin_to_bottom"
    bl_label = "移动原点到-y中心"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 储存当前选中状态和活动物体
        active_object = context.view_layer.objects.active
        selected_objects = context.selected_objects

        for obj in selected_objects:
            # 只对当前物体操作
            context.view_layer.objects.active = obj
            # 取消选择其他所有物体
            bpy.ops.object.select_all(action='DESELECT')
            # 选中当前物体
            obj.select_set(True)
            # 计算物体在世界空间的包围盒角点
            world_bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            # 获得Y方向的最小点作为底部中心的Y位置
            bottom_y = min(world_bbox_corners, key=lambda corner: corner.y).y
            # 还要计算X和Z方向的中心点，以创建一个底部中心的3D点
            center_x = sum([corner.x for corner in world_bbox_corners]) / 8
            center_z = sum([corner.z for corner in world_bbox_corners]) / 8
            bottom_center = Vector((center_x, bottom_y, center_z))
            # 设置游标到底部中心点
            bpy.context.scene.cursor.location = bottom_center
            # 将原点设置到游标位置
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            # 取消选择当前物体，以便下一个循环
            obj.select_set(False)

        # 恢复原始选中状态和活动物体
        for obj in selected_objects:
            obj.select_set(True)
        context.view_layer.objects.active = active_object

        return {'FINISHED'}

#移除顶级物体名称后缀，重名则交换
class OBJECT_OT_remove_suffix_and_resolve_conflicts(Operator):
    bl_idname = "object.remove_suffix_and_resolve"
    bl_label = "移除后缀数字，保持顶级无后缀"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 正则表达式，“.数字”的格式
        suffix_pattern = re.compile(r"\.\d+$")

        for obj in bpy.data.objects:
            # 只处理顶级父物体
            if obj.parent == None:
                # 找到并删除后缀
                new_name = re.sub(suffix_pattern, "", obj.name)

                # 检查是否存在名称冲突的子对象
                conflict_child = None
                for child in obj.children:
                    if child.name == new_name:
                        conflict_child = child
                        break

                if conflict_child:  # 如果找到冲突的子对象
                    # 交换名称
                    conflict_child.name = obj.name
                    obj.name = new_name
                else:  # 无冲突的情况下正常改名
                    obj.name = new_name
        return {'FINISHED'}

#批量独立化
class OBJECT_OT_make_single_user(bpy.types.Operator):
    bl_idname = "object.make_single_user_operator"
    bl_label = "批量独立化"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 获取当前的选择物体列表
        selected_objects = context.selected_objects

        # 遍历所选物体并执行make_single_user命令
        for obj in selected_objects:
            context.view_layer.objects.active = obj  # 将当前物体设置为活动对象
            bpy.ops.object.make_single_user(
                object=True,    # 单独化对象
                obdata=True,   # 不单独化数据
                material=False, # 不单独化材质
                animation=False, # 不单独化动画
                obdata_animation=False # 不单独化数据动画
            )

        # 更新场景以反映更改
        context.view_layer.update()

        return {'FINISHED'}

#生成凸包
class OBJECT_OT_convex_hull_creator(bpy.types.Operator):
    bl_idname = "object.convex_hull_creator"
    bl_label = "生成凸包"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects

        # 使用集合来收集父物体名称以自动移除重复项
        parent_names = set()

        duplicates = []

        for obj in selected:
            top_parent = obj
            while top_parent.parent is not None:
                top_parent = top_parent.parent

            # 将父物体名称添加到集合中
            parent_names.add(top_parent.name)

            dup_obj = obj.copy()
            dup_obj.data = obj.data.copy()
            dup_obj.modifiers.clear()
            context.collection.objects.link(dup_obj)
            duplicates.append(dup_obj)

        bpy.ops.object.select_all(action='DESELECT')

        for dup_obj in duplicates:
            dup_obj.select_set(True)

        bpy.context.view_layer.objects.active = duplicates[0]
        bpy.ops.object.join()

        obj_in_edit = context.object
        context.view_layer.objects.active = obj_in_edit
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.convex_hull()
        bpy.ops.object.mode_set(mode='OBJECT')

        if len(obj_in_edit.data.materials) > 0:
            for _ in range(len(obj_in_edit.data.materials)):
                obj_in_edit.data.materials.pop(index=0)

        # 用已排除重复的父物体名字来命名新物体
        final_name = '_'.join(parent_names) + "_col"
        obj_in_edit.name = final_name
        obj_in_edit.data.name = final_name + "_mesh"

        return {'FINISHED'}
#生成体素化指令
class VoxelConverter(bpy.types.Operator):
    """生成obj2vox指令"""
    bl_idname = "object.voxel_converter"
    bl_label = "生成体素化指令"

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            dimensions = obj.dimensions
            max_dim = max(dimensions.x, dimensions.y, dimensions.z)
            result = round(max_dim * 32)
            print(f"obj2voxel {obj.name}.obj {obj.name}.vox -r {result} -p xZy ")
        return {'FINISHED'}

#移除所选物体修改器
class RemoveModifiers(bpy.types.Operator):
    """移除所选物体的修改器"""
    bl_idname = "object.remove_modifiers"
    bl_label = "移除选中物体的修改器"

    def execute(self, context):
        # 获取当前的选中物体
        selected_objects = context.selected_objects

        # 遍历每个选中的物体
        for obj in selected_objects:

            # 判断这个物体是否有修改器
            if obj.type == 'MESH' and obj.modifiers:

                #如果有，那么我们就移除所有的修改器
                while(obj.modifiers):
                    obj.modifiers.remove(obj.modifiers[0])

        return {'FINISHED'}

#选择尺寸超过指定值的物体
def is_object_size_above_threshold(obj, threshold):
    # 获取物体的尺寸
    dimensions = obj.dimensions
    max_size = max(dimensions)

    # 如果最大尺寸超过指定阈值，则返回True，否则返回False
    return max_size > threshold
class SelectLargeObjectsOperator(bpy.types.Operator):
    bl_idname = "object.select_large_objects"
    bl_label = "选择过大物体"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 将阈值设置为8米
        threshold_meters = 8

        # 清空之前的选择
        bpy.ops.object.select_all(action='DESELECT')

        # 根据条件选择物体
        for obj in bpy.context.scene.objects:
            # 忽略摄像机、灯光等辅助物体
            if obj.type not in ['MESH']:
                continue

            # 判断物体尺寸是否超过指定阈值
            if is_object_size_above_threshold(obj, threshold_meters):
                obj.select_set(True)

        return {'FINISHED'}
    
# 判断物体尺寸是否小于指定阈值
def is_object_size_below_threshold(obj, threshold):
    # 获取物体的尺寸
    dimensions = obj.dimensions
    max_size = max(dimensions)

    # 如果最大尺寸小于指定阈值，则返回True，否则返回False
    return max_size < threshold

class SelectSmallObjectsOperator(bpy.types.Operator):
    bl_idname = "object.select_small_objects"
    bl_label = "选择过小物体"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 将阈值设置为1米
        threshold_meters = 0.2

        # 清空之前的选择
        bpy.ops.object.select_all(action='DESELECT')

        # 根据条件选择物体
        for obj in bpy.context.scene.objects:
            # 忽略摄像机、灯光等非网格物体
            if obj.type not in ['MESH']:
                continue

            # 判断物体尺寸是否小于指定阈值
            if is_object_size_below_threshold(obj, threshold_meters):
                obj.select_set(True)

        return {'FINISHED'}

# 批量导出obj
class ExporteObjOperator(bpy.types.Operator):
  bl_label = "批量导出Obj"
  bl_idname = "object.export_objs"

  def execute(self, context):
    
    output_dir = context.scene.export_directory
    
    selected_objects = context.selected_objects
    
    if not selected_objects:
      self.report({'INFO'}, "No objects selected")
      return {'FINISHED'}

    for obj in selected_objects:
        
      obj_name = obj.name
      export_path = os.path.join(output_dir, obj_name + ".obj")
    
      bpy.ops.object.select_all(action='DESELECT')
      obj.select_set(True)
      bpy.context.view_layer.objects.active = obj
      bpy.ops.export_scene.obj(
        filepath = export_path,
        check_existing=True, 
        axis_forward='-Z', 
        axis_up='Y', 
        use_selection=True, 
        use_animation=False, 
        use_mesh_modifiers=True, 
        use_edges=True, 
        use_smooth_groups=False, 
        use_smooth_groups_bitflags=False, 
        use_normals=True, 
        use_uvs=True, 
        use_materials=True, 
        use_triangles=False, 
        use_nurbs=False, 
        use_vertex_groups=False, 
        use_blen_objects=True, 
        group_by_object=False, 
        group_by_material=False, 
        keep_vertex_order=True, 
        global_scale=1, 
        path_mode='COPY',
      )

      self.report({'INFO'}, f"Exported {obj_name} to {export_path}")
      
    return {'FINISHED'}

#设置所选物体材质为临近采样（硬边缘）
class SetTextureInterpolation(bpy.types.Operator):
    bl_label = "设置所选物体材质为硬边缘采样"
    bl_idname = "object.set_texture_interpolation"
    
    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        
        for obj in selected_objects:
            mat_slots = obj.material_slots
            
            for ms in mat_slots:
                mat = ms.material
                
                if mat and mat.node_tree:
                    node_tree = mat.node_tree
                    
                    for node in node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            node.interpolation = 'Closest'
                            
        return {'FINISHED'}

#更改mesh名称为物体名称
class RenameMeshesOperator(bpy.types.Operator):
    """Rename Meshes to their object names"""      
    bl_idname = "object.rename_meshes"  
    bl_label = "重命名Meshes为物体名称"         
    bl_options = {'REGISTER', 'UNDO'}  
    
    def execute(self, context):       

        # 访问场景中的所有对象
        for obj in bpy.context.scene.objects:
            # 检查对象是否为mesh
            if obj.type == 'MESH':
                # 更改 mesh 数据块的名称为该对象的名称
                obj.data.name = obj.name

        return {'FINISHED'}

class RenameObjectsOperator(bpy.types.Operator):
    """Rename Objects to their mesh names"""
    bl_idname = "object.rename_objects"
    bl_label = "重命名物体为Mesh名称"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                obj.name = obj.data.name

        return {'FINISHED'}

# 合并材质
class MergeMaterial(bpy.types.Operator):
    bl_idname = "object.miao_merge_material"
    bl_label = "合并材质"

    def execute(self, context):
        # 单击按钮时要执行的代码
        mesh_objs = [
            obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        for obj in mesh_objs:
            print(obj.name)
            # Delete all materials in the mesh
            for i in range(len(obj.material_slots)):
                bpy.ops.object.material_slot_remove({'object': obj})
            mat = bpy.data.materials.new(obj.name)
            obj.data.materials.append(mat)
        return {'FINISHED'}

#批量设置发光亮度

bpy.types.Scene.emission_strength = bpy.props.FloatProperty(
    name="强度",
    description="设置发光强度",
    default=0.2,
    min=0.0,
    max=10.0
)
class SetEmissionStrength(bpy.types.Operator):
    bl_idname = "material.set_emission_strength"
    bl_label = "设置发光强度"

    strength : bpy.props.FloatProperty(
        name="强度",
        description="设置发光强度",
        default=0.2,
        min=0.0
    )

    def set_emission_strength(self, material, strength):
        if not material.use_nodes:
            return

        for node in material.node_tree.nodes:
            if node.type == 'EMISSION':
                node.inputs['Strength'].default_value = strength
            if node.type == 'BSDF_PRINCIPLED':
                node.inputs['Emission Strength'].default_value = strength

    def process_selected_objects(self, strength):
        for obj in bpy.context.selected_objects:
            if obj.data.materials:
                for mat in obj.data.materials:
                    if mat.node_tree is not None:
                        self.set_emission_strength(mat, strength)

    def execute(self, context):
        strength = context.scene.emission_strength
        self.process_selected_objects(strength)
        return {'FINISHED'}

#批量清空动画数据
class ClearAnimationData(bpy.types.Operator):
    bl_idname = "object.clear_animation_data"
    bl_label = "清除动画数据"

    def clear_animation_data_for_selected(self):
        selected_objects = bpy.context.selected_objects
        
        for obj in selected_objects:
            if obj.animation_data:
                obj.animation_data_clear()
                print(f"已清除 {obj.name} 的动画数据")
            else:
                print(f"{obj.name} 没有动画数据")

    def execute(self, context):
        self.clear_animation_data_for_selected()
        return {'FINISHED'}

# 置乱位置
class RandomPlacement(bpy.types.Operator):
    bl_idname = "object.miao_random_placement"
    bl_label = "随机放置"

    def execute(self, context):

        bpy.types.Scene.random_placement_extent = bpy.props.FloatVectorProperty(
            name="范围大小(x,y,z)",
            description="设置随机放置的范围大小",
            default=(10, 10, 0),
            size=3
        )
        # 获取自定义属性的值
        extent = bpy.context.scene.random_placement_extent

        objects = sorted(list(bpy.context.selected_objects),
                         key=lambda obj: obj.name)

        # Scatter the objects randomly in the defined area
        for obj in objects:
            obj.location = (random.uniform(-extent[0], extent[0]),
                            random.uniform(-extent[1], extent[1]),
                            random.uniform(-extent[2], extent[2]))

        return {'FINISHED'}

# 置乱缩放
bpy.types.Scene.random_scale_extent_x = bpy.props.FloatVectorProperty(
    name="X轴缩放范围(min, max)",
    description="设置X轴随机缩放的范围",
    default=(1, 1),
    size=2
)
bpy.types.Scene.random_scale_extent_y = bpy.props.FloatVectorProperty(
    name="Y轴缩放范围(min, max)",
    description="设置Y轴随机缩放的范围",
    default=(1, 1),
    size=2
)
bpy.types.Scene.random_scale_extent_z = bpy.props.FloatVectorProperty(
    name="Z轴缩放范围(min, max)",
    description="设置Z轴随机缩放的范围",
    default=(1, 1),
    size=2
)

class RandomScale(bpy.types.Operator):
    bl_idname = "object.miao_random_scale"
    bl_label = "随机缩放"

    def execute(self, context):
        # 获取自定义属性的值
        scale_extent_x = bpy.context.scene.random_scale_extent_x
        scale_extent_y = bpy.context.scene.random_scale_extent_y
        scale_extent_z = bpy.context.scene.random_scale_extent_z

        objects = sorted(list(bpy.context.selected_objects),
                         key=lambda obj: obj.name)

        # Scale the objects randomly within the defined range for each axis
        for obj in objects:
            scale_factor_x = random.uniform(
                scale_extent_x[0], scale_extent_x[1])
            scale_factor_y = random.uniform(
                scale_extent_y[0], scale_extent_y[1])
            scale_factor_z = random.uniform(
                scale_extent_z[0], scale_extent_z[1])
            obj.scale = (scale_factor_x, scale_factor_y, scale_factor_z)

        return {'FINISHED'}

# 名称顺序y轴列队
bpy.types.Scene.queue_up_distance = bpy.props.FloatProperty(
    name="距离",
    description="列队移动的距离",
    default=5
)
bpy.types.Scene.queue_up_axis = bpy.props.EnumProperty(
    name="轴向",
    items=[("X", "X轴", "在X轴上排队"),
           ("Y", "Y轴", "在Y轴上排队"),
           ("Z", "Z轴", "在Z轴上排队")],
    default="Y"
)

class QueueUp(bpy.types.Operator):
    bl_idname = "object.miao_queue_up"
    bl_label = "列队"

    def execute(self, context):

        # 获取自定义属性的值
        distance = bpy.context.scene.queue_up_distance
        axis = bpy.context.scene.queue_up_axis

        objects = sorted(list(bpy.context.selected_objects),
                         key=lambda obj: obj.name)

        if len(objects) == 0:
            print("Collection is empty, cannot move objects")
        else:
            for i, obj in enumerate(objects):
                if axis == "X":
                    obj.location = (i * distance, 0, 0)
                elif axis == "Y":
                    obj.location = (0, i * distance, 0)
                elif axis == "Z":
                    obj.location = (0, 0, i * distance)

        return {"FINISHED"}

# 对齐所选物体原点到底部并归于原点
class AlignmentGround(bpy.types.Operator):
    bl_idname = "object.miao_alignment_ground"
    bl_label = "对齐原点到底部中心-M3"

    def execute(self, context):
        # 储存当前选中状态和活动物体
        active_object = context.view_layer.objects.active
        selected_objects = context.selected_objects

        for obj in selected_objects:
            # 只对当前物体操作
            context.view_layer.objects.active = obj
            
            # 取消选择其他所有物体
            bpy.ops.object.select_all(action='DESELECT')
            
            # 选中当前物体
            obj.select_set(True)

            # 计算物体在世界空间的包围盒角点
            world_bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

            # 获得Y方向的最小点作为底部中心的Y位置
            bottom_y = min(world_bbox_corners, key=lambda corner: corner.y).y
            # 还要计算X和Z方向的中心点，以创建一个底部中心的3D点
            center_x = sum([corner.x for corner in world_bbox_corners]) / 8
            center_z = sum([corner.z for corner in world_bbox_corners]) / 8
            bottom_center = Vector((center_x, bottom_y, center_z))

            # 设置游标到底部中心点
            bpy.context.scene.cursor.location = bottom_center

            # 将原点设置到游标位置
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

            # 取消选择当前物体，以便下一个循环
            obj.select_set(False)

        # 恢复原始选中状态和活动物体
        for obj in selected_objects:
            obj.select_set(True)
        context.view_layer.objects.active = active_object

        return {'FINISHED'}

# 按照空间前后顺序对所选物体重命名
class RenameByLocation(bpy.types.Operator):
    bl_idname = "object.miao_rename_location"
    bl_label = "按轴空间顺序重命名"

    def execute(self, context):

        rename_axis = bpy.context.scene.rename_axis
        rename_order = bpy.context.scene.rename_order

        # 获取所选轴的整数索引
        axis_index = "XYZ".index(rename_axis)

        selected_objs = bpy.context.selected_objects
        locations = [(obj.name, obj.location) for obj in selected_objs]

        # 按轴空间顺序排序
        locations_sorted = sorted(locations, key=lambda x: x[1][axis_index])
        if rename_order == "DESC":
            locations_sorted.reverse()

        # 遍历排序后的物体列表，对每个物体进行重命名
        for i, loc in enumerate(locations_sorted):
            obj_name = 'Object{}'.format(i+1)
            bpy.data.objects[loc[0]].name = obj_name

        return {"FINISHED"}

# 创建父级空物体
def get_top_parent(obj):
    if obj.parent is None:
        return obj
    else:
        return get_top_parent(obj.parent)

# 向目标集合添加空物体
def calculate_bounding_box(objects):
    bbox_corners = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box] 
    min_corner = Vector((min(corner[i] for corner in bbox_corners) for i in range(3))) 
    max_corner = Vector((max(corner[i] for corner in bbox_corners) for i in range(3))) 
    return min_corner, max_corner 

def calculate_bottom_center(min_corner, max_corner):
    bottom_center = min_corner
    bottom_center.x = (max_corner.x + min_corner.x)/2
    bottom_center.y = (max_corner.y + min_corner.y)/2
    return bottom_center

def link_empty(obj_collection, empty_name, location):
    empty = bpy.data.objects.new(empty_name, None)
    obj_collection.objects.link(empty)
    empty.location = location
    return empty

class CreateEmptyAtObjectBottom(bpy.types.Operator):
    bl_idname = "object.miao_create_empty_at_bottom"
    bl_label = "在选中物体底部创建父级空物体"

    def execute(self, context):
        def create_empty_at_bottom(collection, name, location):
            empty = link_empty(collection, name, location)
            return empty

        def create_single_empty_for_multiple_objects(location):
            empty_name = 'multiple_objects_empty'
            empty = link_empty(context.collection, empty_name, location)
            return empty

        multiple_object_binding = context.scene.multiple_object_binding
        selected_objects = bpy.context.selected_objects

        if not multiple_object_binding:
            for obj in selected_objects:
                top_parent = get_top_parent(obj)
                obj_collection = top_parent.users_collection[0]
                empty_name = top_parent.name + '_empty'

                # Calculate the bounding box of the top parent
                min_corner, max_corner = calculate_bounding_box([top_parent])
                # Calculate the bottom center of the top parent
                location = calculate_bottom_center(min_corner, max_corner)

                # Create a new empty at the location
                empty = create_empty_at_bottom(obj_collection, empty_name, location)

                # Store the initial world matrix
                initial_matrix_world = top_parent.matrix_world.copy()

                # Reparent with the new empty object without inverse
                bpy.ops.object.select_all(action='DESELECT')
                empty.select_set(True)
                top_parent.select_set(True)
                context.view_layer.objects.active = empty
                bpy.ops.object.parent_set(type="OBJECT", keep_transform=True)

                # Restore the initial world matrix
                top_parent.matrix_world = initial_matrix_world
        else:
            # Get all top parents
            top_parents = [get_top_parent(obj) for obj in selected_objects]

            # Calculate the bounding box of all top parents
            min_corner, max_corner = calculate_bounding_box(top_parents)
            # Calculate the bottom center of all top parents
            location = calculate_bottom_center(min_corner, max_corner)

            # Create a new empty at the location
            multiple_empty = create_single_empty_for_multiple_objects(location)

            for top_parent in top_parents:

                # Store the initial world matrix
                initial_matrix_world = top_parent.matrix_world.copy()

                # Reparent with the new empty object without inverse
                bpy.ops.object.select_all(action='DESELECT')
                multiple_empty.select_set(True)
                top_parent.select_set(True)
                context.view_layer.objects.active = multiple_empty
                bpy.ops.object.parent_set(type="OBJECT", keep_transform=True)

                # Restore the initial world matrix
                top_parent.matrix_world = initial_matrix_world

        return {'FINISHED'}

# 按距离划分编组并绑定最高的物体为父级
class CollectionByDistance(bpy.types.Operator):
    bl_idname = "object.miao_collection_bydistance"
    bl_label = "按距离划分编组并绑定最高的物体为父级"

    def execute(self, context):

        # 获取选定的物体并将其存储在变量中
        selected_objects = bpy.context.selected_objects

        # 将物体分组
        collections = []
        for obj in selected_objects:
            assigned = False
            for collection in collections:
                if all((obj.matrix_world.translation - member.matrix_world.translation).length < 40 for member in collection.objects):
                    collection.objects.link(obj)
                    assigned = True
                    break
            if not assigned:
                new_collection = bpy.data.collections.new("Collection")
                bpy.context.scene.collection.children.link(new_collection)
                new_collection.objects.link(obj)
                collections.append(new_collection)

        # 为每个集合选择父级
        for collection in collections:
            parent = max(collection.objects, key=lambda x: x.location.z)
            for obj in collection.objects:
                if obj != parent:
                    obj.parent = parent
                    obj.matrix_local = parent.matrix_world.inverted() @ obj.matrix_world

        # 输出父级信息
        for obj in selected_objects:
            if obj.parent is not None:
                print(obj.name, "is a child of", obj.parent.name)

#检测碰撞并且合并：
class CollectionByAttached(bpy.types.Operator):
    bl_idname = "object.collection_by_attached"
    bl_label = "接触合并"

    def execute(self, context):
        def create_bounding_box_vectors(obj):
            bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            return bbox_corners

        def check_bounding_box_collision(obj1, obj2):
            if obj1 == obj2:
                return False

            bbox1 = create_bounding_box_vectors(obj1)
            bbox2 = create_bounding_box_vectors(obj2)

            obj1_min_x, obj1_max_x = min(bbox1, key=lambda coord: coord.x)[0], max(bbox1, key=lambda coord: coord.x)[0]
            obj1_min_y, obj1_max_y = min(bbox1, key=lambda coord: coord.y)[1], max(bbox1, key=lambda coord: coord.y)[1]
            obj1_min_z, obj1_max_z = min(bbox1, key=lambda coord: coord.z)[2], max(bbox1, key=lambda coord: coord.z)[2]

            obj2_min_x, obj2_max_x = min(bbox2, key=lambda coord: coord.x)[0], max(bbox2, key=lambda coord: coord.x)[0]
            obj2_min_y, obj2_max_y = min(bbox2, key=lambda coord: coord.y)[1], max(bbox2, key=lambda coord: coord.y)[1]
            obj2_min_z, obj2_max_z = min(bbox2, key=lambda coord: coord.z)[2], max(bbox2, key=lambda coord: coord.z)[2]

            return (
                obj1_min_x <= obj2_max_x and obj1_max_x >= obj2_min_x
                and obj1_min_y <= obj2_max_y and obj1_max_y >= obj2_min_y
                and obj1_min_z <= obj2_max_z and obj1_max_z >= obj2_min_z
            )

        def merge_objects(objects):
            bpy.ops.object.select_all(action='DESELECT')

            for obj in objects:
                obj.select_set(True)
            
            bpy.context.view_layer.objects.active = objects[0]
            bpy.ops.object.join()

        def group_colliding_objects(selected_objects):
            object_groups = []

            def find_existing_group(obj, groups):
                for group in groups:
                    if obj in group:
                        return group
                return None

            def merge_groups(obj1, obj2, groups):
                group1 = find_existing_group(obj1, groups)
                group2 = find_existing_group(obj2, groups)

                if group1 and group2:
                    if group1 != group2:
                        group1.update(group2)
                        groups.remove(group2)
                elif group1:
                    group1.add(obj2)
                elif group2:
                    group2.add(obj1)
                else:
                    new_group = {obj1, obj2}
                    groups.append(new_group)

            for obj1 in selected_objects:
                for obj2 in selected_objects:
                    if obj1 == obj2:
                        continue
                    if check_bounding_box_collision(obj1, obj2):
                        merge_groups(obj1, obj2, object_groups)

            return object_groups

        selected_objects = bpy.context.selected_objects
        colliding_object_groups = group_colliding_objects(selected_objects)

        for group in colliding_object_groups:
            merge_objects(list(group))

        if colliding_object_groups:
            self.report({'INFO'}, "Objects have been merged.")
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "No colliding objects found.")
            return {'CANCELLED'}

# 碰撞检测（Boundbox）并打组
class CollectionByBoundingbox(bpy.types.Operator):
    bl_idname = "object.miao_collection_byboundingbox"
    bl_label = "检测碰撞归为一个集合（无法撤回请及时保存）"

    def execute(self, context):

        def create_bounding_box_vectors(obj):
            bbox_corners = [obj.matrix_world @
                            Vector(corner) for corner in obj.bound_box]
            return bbox_corners

        def check_bounding_box_collision(obj1, obj2):
            if obj1 == obj2:
                return False

            bbox1 = create_bounding_box_vectors(obj1)
            bbox2 = create_bounding_box_vectors(obj2)

            obj1_min_x, obj1_max_x = min(bbox1, key=lambda coord: coord.x)[
                0], max(bbox1, key=lambda coord: coord.x)[0]
            obj1_min_y, obj1_max_y = min(bbox1, key=lambda coord: coord.y)[
                1], max(bbox1, key=lambda coord: coord.y)[1]
            obj1_min_z, obj1_max_z = min(bbox1, key=lambda coord: coord.z)[
                2], max(bbox1, key=lambda coord: coord.z)[2]

            obj2_min_x, obj2_max_x = min(bbox2, key=lambda coord: coord.x)[
                0], max(bbox2, key=lambda coord: coord.x)[0]
            obj2_min_y, obj2_max_y = min(bbox2, key=lambda coord: coord.y)[
                1], max(bbox2, key=lambda coord: coord.y)[1]
            obj2_min_z, obj2_max_z = min(bbox2, key=lambda coord: coord.z)[
                2], max(bbox2, key=lambda coord: coord.z)[2]

            return (
                obj1_min_x <= obj2_max_x and obj1_max_x >= obj2_min_x
                and obj1_min_y <= obj2_max_y and obj1_max_y >= obj2_min_y
                and obj1_min_z <= obj2_max_z and obj1_max_z >= obj2_min_z
            )

        def create_collection(coll_name, objects):
            coll = bpy.data.collections.get(coll_name)
            if not coll:
                coll = bpy.data.collections.new(coll_name)
                bpy.context.scene.collection.children.link(coll)
            for obj in objects:
                current_collections = obj.users_collection
                coll.objects.link(obj)
                for current_coll in current_collections:
                    current_coll.objects.unlink(obj)

        def group_colliding_objects(selected_objects):
            object_groups = []

            def find_existing_group(obj, groups):
                for group in groups:
                    if obj in group:
                        return group
                return None

            def merge_groups(obj1, obj2, groups):
                group1 = find_existing_group(obj1, groups)
                group2 = find_existing_group(obj2, groups)

                if group1 and group2:
                    if group1 != group2:
                        group1.update(group2)
                        groups.remove(group2)
                elif group1:
                    group1.add(obj2)
                elif group2:
                    group2.add(obj1)
                else:
                    new_group = {obj1, obj2}
                    groups.append(new_group)

            for obj1 in selected_objects:
                for obj2 in selected_objects:
                    if obj1 == obj2:
                        continue
                    if check_bounding_box_collision(obj1, obj2):
                        merge_groups(obj1, obj2, object_groups)

            return object_groups

        selected_objects = bpy.context.selected_objects
        colliding_object_groups = group_colliding_objects(selected_objects)

        for i, group in enumerate(colliding_object_groups, 1):
            collection_name = f"Collision_Group_{i}"
            create_collection(collection_name, group)

        if colliding_object_groups:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

#vox导入处理
class VoxOperation(bpy.types.Operator):
    bl_idname = "object.vox_operation"
    bl_label = "vox角色处理"

    def execute(self, context):

        # bpy.ops.object.miao_apply_and_sparate()
        bpy.ops.object.reset_normals_flat_shading()
        # bpy.ops.object.merge_vertices_operator()

        return {'FINISHED'}



# 碰撞检测（Boundbox）并创建父级
class ParentByBoundingbox(bpy.types.Operator):
    bl_idname = "object.miao_parent_byboundingbox"
    bl_label = "检测碰撞归为一个子集"

    def execute(self, context):
        def create_bounding_box_vectors(obj):
            bbox_corners = [obj.matrix_world @
                            Vector(corner) for corner in obj.bound_box]
            return bbox_corners

        def check_bounding_box_collision(obj1, obj2):
            if obj1 == obj2:
                return False

            bbox1 = create_bounding_box_vectors(obj1)
            bbox2 = create_bounding_box_vectors(obj2)

            obj1_min_x, obj1_max_x = min(bbox1, key=lambda coord: coord.x)[
                0], max(bbox1, key=lambda coord: coord.x)[0]
            obj1_min_y, obj1_max_y = min(bbox1, key=lambda coord: coord.y)[
                1], max(bbox1, key=lambda coord: coord.y)[1]
            obj1_min_z, obj1_max_z = min(bbox1, key=lambda coord: coord.z)[
                2], max(bbox1, key=lambda coord: coord.z)[2]

            obj2_min_x, obj2_max_x = min(bbox2, key=lambda coord: coord.x)[
                0], max(bbox2, key=lambda coord: coord.x)[0]
            obj2_min_y, obj2_max_y = min(bbox2, key=lambda coord: coord.y)[
                1], max(bbox2, key=lambda coord: coord.y)[1]
            obj2_min_z, obj2_max_z = min(bbox2, key=lambda coord: coord.z)[
                2], max(bbox2, key=lambda coord: coord.z)[2]

            return (
                obj1_min_x <= obj2_max_x and obj1_max_x >= obj2_min_x
                and obj1_min_y <= obj2_max_y and obj1_max_y >= obj2_min_y
                and obj1_min_z <= obj2_max_z and obj1_max_z >= obj2_min_z
            )

        def calculate_group_center(group):
            if not group:
                return Vector((0, 0, 0))

            # 初始化最小和最大向量
            min_coord = Vector((float('inf'), float('inf'), float('inf')))
            max_coord = Vector((-float('inf'), -float('inf'), -float('inf')))

            # 对每个物体的边界框的每个角进行迭代，更新最小和最大坐标
            for obj in group:
                bbox_corners = create_bounding_box_vectors(obj)
                for corner in bbox_corners:
                    min_coord.x = min(min_coord.x, corner.x)
                    min_coord.y = min(min_coord.y, corner.y)
                    min_coord.z = min(min_coord.z, corner.z)

                    max_coord.x = max(max_coord.x, corner.x)
                    max_coord.y = max(max_coord.y, corner.y)
                    max_coord.z = max(max_coord.z, corner.z)

            # 计算并返回最小和最大坐标的平均值
            center = (min_coord + max_coord) * 0.5
            return center
        
        # 获取所有mesh对象
        all_mesh_objects = [obj for obj in context.scene.objects if obj.type == 'MESH']
        bounding_boxes = {obj: create_bounding_box_vectors(obj) for obj in all_mesh_objects}

        def find_colliding_objects(obj, objects):
            """找到与指定对象碰撞的所有对象"""
            colliding_objects = []
            for other in objects:
                if obj != other and check_bounding_box_collision(obj, other):
                    colliding_objects.append(other)
            return colliding_objects

        def group_colliding(obj, grouped_objects, remaining_objects):
            """递归地寻找碰撞对象，并将它们放入同一组"""
            colliding = find_colliding_objects(obj, remaining_objects)
            for coll_obj in colliding:
                if coll_obj not in grouped_objects:
                    grouped_objects.add(coll_obj)
                    remaining_objects.remove(coll_obj)
                    # 继续传递 bounding_boxes 参数
                    group_colliding(coll_obj, grouped_objects, remaining_objects)
        
        # 根据新的起点对象递归寻找碰撞组
        colliding_groups = []
        while all_mesh_objects:
            starting_object = all_mesh_objects.pop()
            current_group = {starting_object}
            group_colliding(starting_object, current_group, all_mesh_objects)
            colliding_groups.append(current_group)
            
        # 创建父对象
        for group in colliding_groups:
            # 取消选择所有物体
            bpy.ops.object.select_all(action='DESELECT')
            
            # 选择当前组中的所有物体
            for obj in group:
                obj.select_set(True)
            
            # 需要设置活跃对象以确保操作运行无误
            if group:  # 如果组非空
                context.view_layer.objects.active = next(iter(group))
            
            # 调用自定义操作，这里假设 `miao_create_empty_at_bottom` 正常工作
            bpy.ops.object.miao_create_empty_at_bottom()

        return {'FINISHED' if colliding_groups else 'CANCELLED'}

#角色一键处理（绑骨骼）
bpy.types.Scene.assign_contact_weights = bpy.props.BoolProperty(
        name="是否赋予权重",
        default=False,
        )
bpy.types.Scene.threshold_distance = bpy.props.FloatProperty(
    name="接触判定阈值",
    description="Set the threshold distance for contact weight calculation",
    default=0.1,
    min=0.0,
    step=0.1,
    precision=2
)

# class CharOperaterBoneWeight(bpy.types.Operator):
#     bl_idname = "object.char_operater_bone_weight"
#     bl_label = "执行自定义操作"

#     def execute(self, context):

#         def rename_all_children_based_on_collection(empty_coll_name):
#             # 获取包含空物体的集合
#             empty_collection = bpy.data.collections[empty_coll_name]

#             # 初始化一个字典来保存BVH树
#             objects_bvh = {}

#             def create_bvh_tree(obj):
#                 bm = bmesh.new()
#                 bm.from_object(obj, bpy.context.evaluated_depsgraph_get())
#                 bmesh.ops.transform(bm, verts=bm.verts, matrix=obj.matrix_world)
        
#                 bvh = BVHTree.FromBMesh(bm)
#                 bm.free()
#                 return bvh

#             # 遍历场景中的所有物体，为所有的模型物体创建BVH树
#             for obj in bpy.context.scene.objects:
#                 if obj.type == 'MESH':
#                     objects_bvh[obj] = create_bvh_tree(obj)
        
#             # 初始化一个字典来过滤已经被重新命名的物体
#             renamed_objects = {}

#             # 遍历空物体集合中的所有物体
#             for obj in empty_collection.objects:
#                 if "_example" in obj.name and obj.type == 'EMPTY':
#                     # 获取不包含"example"的名称
#                     new_name = obj.name.replace("_example", "")
                    
#                     # 检查每个模型物体是否包含这个空物体
#                     for other_obj, _ in objects_bvh.items():
#                         # 如果物体被修改了，我们需要重新生成bvh tree
#                         if other_obj.is_modified(bpy.context.scene, 'PREVIEW'):
#                             objects_bvh[other_obj] = create_bvh_tree(other_obj)

#                         # 获取空物体的全局位置
#                         global_location = obj.matrix_world.translation

#                         intersection_count = 0
#                         ray_origin = global_location
#                         ray_direction = Vector((0, 0, -1))
#                         bvh = objects_bvh[other_obj]

#                         while True:
#                             hit, _, _, _ = bvh.ray_cast(ray_origin, ray_direction)
#                             if hit is None:
#                                 break
#                             intersection_count += 1
#                             ray_origin = hit + ray_direction * 0.00001  

#                         # 如果交叉次数为奇数，则该点在物体内部
#                         if intersection_count % 2 == 1:
#                             if other_obj not in renamed_objects:
#                                 other_obj.name = new_name
#                                 renamed_objects[other_obj] = True
                                
#         # 检查一个物体及其所有的子物体是否为Empty类型
#         def all_children_empty(object):
#             if object.type != 'EMPTY':
#                 return False
#             for child in object.children:
#                 if not all_children_empty(child):
#                     return False
#             return True

#         def duplicate_bones_to_objects():
#             scene_objects = bpy.data.objects

#             bip001_bone = bpy.data.objects.get('Bip001_example')  # 获取名为Bip001的骨架

#             if not bip001_bone or bip001_bone.type != 'ARMATURE':  # 确保Bip001存在且是骨架类型
#                 print('Bip001 armature not found or not of ARMATURE type.')
#                 return

#             for object in scene_objects:
#                 if object.parent is None:  # 找到顶级父物体
#                     # 如果物体以及所有的子物体都为Empty类型，那么跳过
#                     if all_children_empty(object):
#                         continue
#                     dup_bone = bip001_bone.copy()  # 复制骨架，会包含所有骨骼
#                     dup_bone.name = 'Bip001'
#                     dup_bone.data = bip001_bone.data.copy()  # 复制骨架的Armature数据
#                     dup_bone.data.name = "Bip001" 

#                     # 把复制的骨架移动到父物体的集合中
#                     object.users_collection[0].objects.link(dup_bone)

#                     dup_bone.matrix_world = bip001_bone.matrix_world  # 设置复制骨架的位置为原骨架位置

#                     dup_bone.parent = object  # 设置原父物体为复制骨架的父物体

#                     # 绑定过程
#                     for child_obj in object.children:
#                         if child_obj.type == 'MESH':
#                             #对象与骨骼名字的比较规则改为物体名称前加 "Bip001 "
#                             bone_name = "Bip001 " + child_obj.name.split('.')[0]

#                             # 创建骨骼修改器
#                             modifier = child_obj.modifiers.new(name='ArmatureMod', type='ARMATURE')
#                             modifier.object = dup_bone
#                             modifier.use_vertex_groups = True

#                             # 添加顶点组并设置权重为 1
#                             group = child_obj.vertex_groups.new(name=bone_name)
#                             for v in child_obj.data.vertices:
#                                 group.add([v.index], 1.0, 'ADD')

#         def get_top_parent(obj):
#             """此函数用于获取物体的顶级父物体"""
#             while obj.parent is not None:
#                 obj = obj.parent
#             return obj if obj else None

#         def create_parent_dict(name_list):
#             # 使用字典保存顶级父物体的mesh子物体
#             top_parents = {}  
#             for obj in bpy.context.scene.objects:  # 遍历场景中的所有物体
#                 # 如果物体是mesh并且名字中包含给定的关键字
#                 if obj.type == 'MESH' and any(name in obj.name for name in name_list):
#                     top_parent = get_top_parent(obj)
#                     if top_parent is None:
#                         top_parent = obj  # 如果没有父对象，则顶级父对象是对象本身
#                     if top_parent not in top_parents:
#                         top_parents[top_parent] = []
#                     top_parents[top_parent].append(obj)
#             return top_parents

#         def join_objects(parent_dict, new_name):
#             for top_parent, objects in parent_dict.items():
#                 bpy.ops.object.select_all(action='DESELECT')  # 全部取消选中
#                 for obj in objects:
#                     obj.select_set(True)  # 设置物体为选中

#                 if bpy.context.selected_objects:  # 如果有选中的物体
#                     ctx = bpy.context.copy()
#                     ctx['active_object'] = bpy.context.selected_objects[0]
#                     ctx['selected_editable_objects'] = bpy.context.selected_objects
#                     bpy.ops.object.join(ctx)  # 合并选中的物体

#         def create_contact_vertex_groups(input_objects, threshold_distance):
#             # 设定已存在的物体名
#             objects = {obj.name: obj for obj in input_objects}

#             # 提前设定好每个物体的KD树和BMesh实例
#             kdtrees = {}
#             bm_objects = {}
#             for obj_name, obj in objects.items():
#                 bm_objects[obj_name] = bmesh.new()
#                 bm_objects[obj_name].from_mesh(obj.data)
#                 kdtrees[obj_name] = kdtree.KDTree(len(bm_objects[obj_name].verts))
#                 for i, v in enumerate(bm_objects[obj_name].verts):
#                     kdtrees[obj_name].insert(obj.matrix_world @ v.co, i)
#                 kdtrees[obj_name].balance()

#             # 准备顶点组字典
#             vertex_groups = defaultdict(dict)

#             for obj_a in input_objects:
#                 obj_a_name = obj_a.name
#                 # 准备与其他物体的联系顶点组
#                 for obj_b in input_objects:
#                     if obj_a != obj_b:
#                         group_name = f'Bip001 {obj_b.name}'
#                         vertex_groups[obj_a][obj_b] = (obj_a.vertex_groups.new(name=group_name)
#                                                     if group_name not in obj_a.vertex_groups else
#                                                     obj_a.vertex_groups[group_name])

#             for obj_a in input_objects:
#                 obj_a_name = obj_a.name
#                 bm_a = bm_objects[obj_a_name]
#                 kd_tree_a = kdtrees[obj_a_name]
#                 for obj_b in input_objects:
#                     if obj_a != obj_b:
#                         kd_tree_b = kdtrees[obj_b.name]
#                         vertex_group = vertex_groups[obj_a][obj_b]
#                         # 遍历对象A的每个顶点，识别接触面顶点并分配权重给顶点组
#                         for i, v in enumerate(bm_a.verts):
#                             global_v_co = obj_a.matrix_world @ v.co
#                             closest_co, closest_index, dist = kd_tree_b.find(global_v_co)
#                             if dist < threshold_distance:
#                                 weight = 1.0 - dist / threshold_distance
#                                 vertex_group.add([v.index], weight, 'REPLACE')

#             # 释放BMesh资源
#             for bm in bm_objects.values():
#                 bm.free()

#             # 更新网格数据以反映改变
#             for obj in input_objects:
#                 obj.data.update()

#             print("Contact weights assigned for all object combinations, and self vertex groups created with full weight.")
          
#         def filter_objects_by_name_patterns(objects, name_patterns):
#             filtered_objects = []
#             for obj in objects:
#                 if obj.type == 'MESH' and any(name_pattern in obj.name for name_pattern in name_patterns):
#                     filtered_objects.append(obj)
#             return filtered_objects

#         name_groups = [
#             (["Head", "Neck"], "Face"),
#         #    (["Head", ], "Face"),
#             (["Spine", "UpperArm", "Forearm", "Hand", "Finger"], "UpperBody"),
#             (["Pelvis",], "Pelvis"),
#             (["Thigh", "Calf",], "LowerBody"),
#             (["Foot", "Toe0",], "Feet")
#         ]

#         named_group = [
#             {'L Finger11', 'L Finger1'},
#             {'L Finger01', 'L Finger0'},
#             {'L Finger21', 'L Finger2'},
#             {'R Finger11', 'R Finger1'},
#             {'R Finger01', 'R Finger0'},
#             {'R Finger21', 'R Finger2'},
#             {'Pelvis', 'Spine2', 'Spine1', 'Spine'}
#         ]
        
#         #清理场景
#         bpy.ops.object.miao_clean_sense()
#         #按照空物体标记重命名物体
#         rename_all_children_based_on_collection("name_example")

#         def process_contact_weights():
#             threshold_distance = bpy.context.scene.threshold_distance
#             if bpy.context.scene.assign_contact_weights:
#                 print("Processing contact weights...")
#                 # 对每个顶级父物体和每对分组应用接触检测和权重赋值操作
#                 all_objects = bpy.context.scene.objects
#                 # 针对每个名称组过滤物体并计算接触权重
#                 for name_patterns in named_group:
#                     # 过滤物体
#                     group_objects = filter_objects_by_name_patterns(all_objects, name_patterns)
#                     # 计算接触权重，只有当组内至少有两个物体时才进行操作
#                     create_contact_vertex_groups(group_objects, threshold_distance)
#                 pass
#             else:
#                 print("Skipping contact weight assignment...")

#         #判定是否需要赋予权重
#         process_contact_weights()
#         #绑定骨骼
#         duplicate_bones_to_objects()
#         #合并身体部件
#         parent_dict_list = [(create_parent_dict(name_list), new_name) for name_list, new_name in name_groups]
#         for parent_dict, new_name in parent_dict_list:
#             join_objects(parent_dict, new_name)
#         rename_all_children_based_on_collection("name_example_comb")

#         return {'FINISHED'}

class CharOperater(bpy.types.Operator):
    bl_idname = "object.miao_char_operater"
    bl_label = "角色一键处理"
    
    def apply_transforms_recursive(self, obj):
        # Make sure you select the object
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        # Apply the transformation
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(False)

        # If obj has children, call this function for each of them
        if obj.children:
            for child in obj.children:
                self.apply_transforms_recursive(child)


    def execute(self, context):

        print("开始处理顶点")
        bpy.ops.object.vox_operation()
        print("开始处理碰撞")
        bpy.ops.object.miao_parent_byboundingbox()
        # bpy.ops.object.object.rig_objects()

        def apply_change_to_scene():
            def set_material_to_objects(objects, material):
                for obj in objects:
                    if len(obj.data.materials):
                        obj.data.materials[0] = material
                    else:
                        obj.data.materials.append(material)

            top_level_parents = [obj for obj in bpy.data.objects if obj.parent is None and 'example' not in obj.name.lower()]

            for parent_obj in top_level_parents:
                parent_obj.scale *= 0.5
                parent_obj.location = (0, 0, 0)

                if parent_obj.children:
                    children_with_materials = [child for child in parent_obj.children if len(child.data.materials) > 0]
                    if children_with_materials:
                        child_with_random_material = random.choice(children_with_materials)
                        random_material = child_with_random_material.data.materials[0]
                        set_material_to_objects(parent_obj.children, random_material)
    
        apply_change_to_scene()

        # Apply transformations to all children of all top level objects recursively
        for parent_obj in bpy.context.scene.objects:
            if parent_obj.parent is None:
                self.apply_transforms_recursive(parent_obj)
        
        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}

# 清空空集合
def clean_collection(collection):

  for child in collection.children:  
    clean_collection(child)

  if collection.children:
    return
  
  if not collection.objects:
    bpy.data.collections.remove(collection)

class CleanCollection(bpy.types.Operator):
    bl_idname = "object.miao_clean_collection"
    bl_label = "清空空集合"

    def execute(self, context):
        scene = bpy.context.scene
        
        clean_collection(scene.collection)

        return {'FINISHED'}

# 按体积筛选物体
class SelectByVolume(bpy.types.Operator):
    bl_idname = "object.miao_select_by_volume"
    bl_label = "按体积筛选物体"

    filter_mode: bpy.props.EnumProperty(
        name="Filter Mode",
        description="筛选大于或小于给定体积的物体",
        items=[
            ("GREATER_THAN", "大于", "选择体积大于给定阈值的物体"),
            ("LESS_THAN", "小于", "选择体积小于给定阈值的物体")
        ],
        default="GREATER_THAN",
    )

    volume_threshold: bpy.props.FloatProperty(
        name="体积阈值",
        description="根据筛选模式选择大于或小于此值的物体",
        default=0.0,
        min=0.0,
        max=float('inf'),
        soft_min=0,
        soft_max=1000.0,
        step=1,
        precision=2,
    )

    select: bpy.props.BoolProperty(
        name="选择物体",
        description="若选中，满足条件的物体将被选择；若不选中，满足条件的物体将被取消选择",
        default=True,
    )

    def execute(self, context):
        scene = bpy.context.scene

        for obj in scene.objects:
            if obj.type == "MESH":
                volume = obj.dimensions.x * obj.dimensions.y * obj.dimensions.z

                if self.filter_mode == "GREATER_THAN":
                    condition = volume > self.volume_threshold
                else:
                    condition = volume < self.volume_threshold

                if condition:
                    obj.select_set(self.select)
                else:
                    obj.select_set(not self.select)
        return {"FINISHED"}

# 材质球排序
class MaterialSort(bpy.types.Operator):
    bl_idname = "object.miao_material_sort"
    bl_label = "材质球排序"

    def execute(self, context):
        def sort_materials(obj):
            if obj is not None and obj.type == 'MESH' and len(obj.data.materials) > 1:
                materials = [slot.material for slot in obj.material_slots]
                sorted_materials = sorted(materials, key=lambda x: x.name)

                # 记录顶点组的材质分配关系
                polygon_material_indices = [
                    polygon.material_index for polygon in obj.data.polygons]

                # 创建一个映射，将旧的材质索引映射到新的排序后的材质索引
                index_mapping = {i: sorted_materials.index(
                    material) for i, material in enumerate(materials)}

                # 更新顶点组的材质分配关系
                for polygon in obj.data.polygons:
                    polygon.material_index = index_mapping[polygon_material_indices[polygon.index]]

                # 将排序后的材质球分配回物体的材质插槽
                for i, material in enumerate(sorted_materials):
                    obj.material_slots[i].material = material

        # 获取当前所选物体
        selected_objects = bpy.context.selected_objects
        # 遍历所选物体并排序它们的材质球
        for obj in selected_objects:
            sort_materials(obj)
        return {"FINISHED"}

# 按照包围盒生成box
class BoundboxGen(bpy.types.Operator):
    bl_idname = "object.miao_boundbox_gen"
    bl_label = "生成包围盒"

    def execute(self, context):

        def create_box_from_bounding_box(obj_name, bounding_box):
            mesh = bpy.data.meshes.new(obj_name + "_box")
            bm = bmesh.new()

            bmesh.ops.create_cube(bm, size=1)
            bm.to_mesh(mesh)

            box = bpy.data.objects.new(obj_name + "_box", mesh)

            global_coordinate_bounding_box = [
                obj.matrix_world @ mathutils.Vector(coord) for coord in bounding_box
            ]

            box.dimensions = [
                abs(global_coordinate_bounding_box[6][0] -
                    global_coordinate_bounding_box[0][0]),
                abs(global_coordinate_bounding_box[6][1] -
                    global_coordinate_bounding_box[0][1]),
                abs(global_coordinate_bounding_box[6][2] -
                    global_coordinate_bounding_box[0][2]),
            ]

            box.location = [
                (global_coordinate_bounding_box[6][0] +
                 global_coordinate_bounding_box[0][0]) / 2,
                (global_coordinate_bounding_box[6][1] +
                 global_coordinate_bounding_box[0][1]) / 2,
                (global_coordinate_bounding_box[6][2] +
                 global_coordinate_bounding_box[0][2]) / 2,
            ]

            # 将包围盒的父级设置为参考物体的父级
            box.parent = obj.parent

            # box.rotation_euler = obj.rotation_euler

            bpy.context.collection.objects.link(box)

            return box

        objects = bpy.context.selected_objects

        if objects:
            for obj in objects:
                bounding_box = obj.bound_box
                create_box_from_bounding_box(obj.name, bounding_box)
        else:
            print("请先选择物体")

        return {'FINISHED'}

# 选择合并，不破坏集合关系
class CombinObject(bpy.types.Operator):
    bl_idname = "object.miao_safecombin"
    bl_label = "安全合并（不破坏集合）"

    def execute(self, context):

        # 定义一个函数用于合并物体
        def merge_objects(objs, target_collection, new_name):
            # 取消所有选中物体
            bpy.ops.object.select_all(action='DESELECT')

            # 选择 objs 中的物体并设置活动物体
            for obj in objs:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = objs[0]

            # 合并物体
            bpy.ops.object.join()

            # 获取合并后的物体
            merged_object = bpy.context.active_object

            # 对合并后的物体重命名，并移到目标集合
            merged_object.name = new_name
            merged_object.users_collection[0].objects.unlink(merged_object)
            target_collection.objects.link(merged_object)

            return merged_object

        # 获取选中的物体
        selected_objects = bpy.context.selected_objects

        # 按自身所在的集合分组物体
        grouped_objects = collections.defaultdict(list)
        for obj in selected_objects:
            grouped_objects[obj.users_collection[0]].append(obj)

        # 遍历按集合分组的物体
        merged_objects = []
        for collection, objects in grouped_objects.items():

            # 合并物体，并保持在原本的集合中
            new_obj_name = f"Merged_{collection.name}_object"
            merged_object = merge_objects(objects, collection, new_obj_name)
            merged_objects.append(merged_object)

        # 取消原来的选中，选择合并后的物体
        for obj in selected_objects:
            obj.select_set(False)
        for obj in merged_objects:
            obj.select_set(True)

# 移除选中物体的顶点组
class RemoveVertexGroup(bpy.types.Operator):
    bl_idname = "object.miao_remove_vertex_group"
    bl_label = "移除选中物体的顶点组"

    def execute(self, context):

        # 获取当前选择的物体
        selected_objects = bpy.context.selected_objects
        # 批量移除所选物体的顶点组
        for obj in selected_objects:
            # 确保所选物体类型为 MESH
            if obj.type == 'MESH':
                # 直接从 obj.vertex_groups 中删除顶点组
                while obj.vertex_groups:
                    obj.vertex_groups.remove(obj.vertex_groups[0])

        print("顶点组已成功移除！")
        return {'FINISHED'}
# 对齐原点
class AlignOrign(bpy.types.Operator):
    bl_idname = "object.miao_align_orign"
    bl_label = "对齐原点（需要勾选仅影响原点）"

    def execute(self, context):

        def align_origin(axis='X', objects=None):

            axis_map = {'X': 0, 'Y': 1, 'Z': 2}
            axis_index = axis_map[axis]

            if objects is None:
                objects = bpy.context.selected_objects

            min_origin_coord = None

            # 搜索所选物体中原点坐标值最小的对象
            for obj in objects:
                if obj.type == 'MESH':
                    origin_coordinate = obj.matrix_world.translation
                    if min_origin_coord is None or origin_coordinate[axis_index] < min_origin_coord:
                        min_origin_coord = origin_coordinate[axis_index]

            for obj in objects:
                if obj.type == 'MESH':
                    difference = min_origin_coord - \
                        obj.matrix_world.translation[axis_index]

                    previous_affect_pivot_point = bpy.context.tool_settings.use_transform_pivot_point_align
                    bpy.context.tool_settings.use_transform_pivot_point_align = True

                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)

                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.transform.translate(value=(
                        difference if axis == 'X' else 0, difference if axis == 'Y' else 0, difference if axis == 'Z' else 0))

                    bpy.context.tool_settings.use_transform_pivot_point_align = previous_affect_pivot_point

        # 调用函数 - 对齐所选物体的X轴原点
        align_origin('X')

# 测试用旋转脚本
class RotationOperator(bpy.types.Operator):
    bl_idname = "object.rotation_operator"
    bl_label = "Rotation Operator"

    rotation_angle: bpy.props.FloatProperty(
        name="Rotation Angle",
        description="Angle to rotate the selected objects in radians",
        default=0.0)

    def execute(self, context):
        rotation_axis = context.scene.my_rotation_axis_enum
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                setattr(obj.rotation_euler, rotation_axis, getattr(
                    obj.rotation_euler, rotation_axis) + self.rotation_angle)

        return {"FINISHED"}

#一键提升精度
class MoveOutsideOperator(bpy.types.Operator):
    bl_idname = "object.move_outside_operator"
    bl_label = "校正旋转"
    
    def execute(self, context):
        obj=context.active_object
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        radians=math.radians(90)
        obj.rotation_euler.x-=radians
        obj.rotation_euler.y-=radians
        obj.rotation_euler.y-=radians 
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        obj.rotation_euler.x+=radians
        bpy.ops.object.select_all(action='DESELECT')
        return {"FINISHED"}

class FixSizeOperator(bpy.types.Operator):
    bl_idname = "object.fix_size_operator"
    bl_label = "提升精度"
    
    def execute(self, context):
        outermost_obj = context.active_object
        if outermost_obj is not None:
            outermost_obj.scale *= 0.0001 
            for child_obj in outermost_obj.children:
                child_obj.scale *= 10000
                child_obj.location *= 10000
        return {"FINISHED"}

# 标记资产
class CreateAssemblyAsset(bpy.types.Operator):
    bl_idname = "object.miao_create_assembly_asset"
    bl_label = "批量标记资产（需要m3插件）"

    def execute(self, context):

        bpy.types.Scene.create_top_level_parent = bpy.props.BoolProperty(
            name="创建顶级父物体",
            description="设置是否为每个资产创建一个顶级父物体",
            default=True
        )

        bpy.types.Scene.asset_collection = bpy.props.PointerProperty(
            name="集合",
            description="选择将要标记资产的集合",
            type=bpy.types.Collection
        )

        def get_3d_view_region():
            for area in bpy.context.window.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            return area, region
            return None, None

        def isolate_parent_and_children(obj):
            for ob in bpy.context.visible_objects:
                ob.hide_viewport = True

            obj.hide_viewport = False
            obj.select_set(True)

            # 添加一个新方法，显示所有子物体，包括它们的子集
            def recurse_children(obj):
                for child in obj.children:
                    child.hide_viewport = False
                    child.select_set(True)
                    recurse_children(child)

            recurse_children(obj)  # 调用递归方法

        def select_obj_and_children(obj):
            obj.select_set(True)
            for child in obj.children:
                select_obj_and_children(child)

        def get_viewport_area():
            for area in bpy.context.window.screen.areas:
                if area.type == 'VIEW_3D':
                    return area
            return None

        def create_empty_parent(obj):
            empty = bpy.data.objects.new(f"Empty_{obj.name}", None)
            scene = bpy.context.scene
            scene.collection.objects.link(empty)

            obj_old_parent = obj.parent
            obj.parent = empty
            empty.parent = obj_old_parent

            return empty

        create_top_level_parent = bpy.context.scene.create_top_level_parent

        collection_name = bpy.context.scene.asset_collection.name
        collection = bpy.data.collections.get(collection_name)

        if collection:

            viewport_area, viewport_region = get_3d_view_region()

            if viewport_area is None:
                print("没有找到 3D 视口")
            else:
                i = 0
                for obj in collection.objects:

                    if obj.parent is not None:
                        continue

                    time.sleep(1)
                    i += 1
                    print(f"成功添加资产{i}个")

                    isolate_parent_and_children(obj)

                    override = bpy.context.copy()
                    override['area'], override['region'] = viewport_area, viewport_region
                    bpy.ops.view3d.view_selected(override)

                    original_parent = None
                    if obj.parent is not None:
                        original_parent = obj.parent

                    bpy.ops.object.select_all(action='DESELECT')
                    select_obj_and_children(obj)

                    if create_top_level_parent:
                        create_empty_parent(obj)

                    # 执行 Machin3tools 的标记资产操作并获取 viewport_area
                    override_context = bpy.context.copy()
                    override_context['area'] = viewport_area
                    bpy.ops.machin3.create_assembly_asset(override_context)

                    # 如果存在原始父级，将其恢复
                    if original_parent is not None:
                        obj.parent = original_parent

                    bpy.context.view_layer.update()
                    bpy.ops.wm.redraw_timer(type='DRAW', iterations=30)
        else:
            print("没有选择任何集合")
        return {"FINISHED"}

#去除名称后缀
class RemoveNameSuffix(bpy.types.Operator):
    bl_idname = "object.miao_remove_name_suffix"
    bl_label = "移除名称后缀"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        name_dict = {}

        # 移除后缀，并储存重名的物体
        for obj in selected_objects:
            obj.name = re.sub("(_.*|-.*|\.\d{3}$)", "", obj.name)
            if obj.name in name_dict:
                name_dict[obj.name].append(obj)
            else:
                name_dict[obj.name] = []

        # 根据需要添加后缀
        for obj_name, duplicate_objs in name_dict.items():
            for i, obj in enumerate(duplicate_objs):
                obj.name = obj_name + '.' + str(i + 1).zfill(3)

        return {"FINISHED"}

#批量更改子级名称为顶级父级，忽略隐藏物体
class RenameByParent(bpy.types.Operator):
    bl_idname = "object.miao_rename_by_parent"
    bl_label = "更改所选物体为其顶级名称"

    def execute(self, context):

        def rename_selected_objects_with_sequential_suffixes():
            def get_sequential_suffix(name_base, current_number):
                return f"{name_base}.{current_number:03d}"

            # 获取所有已选择的物体
            all_objects = bpy.data.objects
            selected_objects = bpy.context.selected_objects

            # 遍历所有已选择的物体
            for obj in selected_objects:
                # 检查物体是否有父级，并获得物体的顶级父级
                if obj.parent is None:
                    continue
                top_parent = obj.parent
                while top_parent.parent is not None:
                    top_parent = top_parent.parent

                # 检查物体是否在视口中隐藏，如果是，则跳过
                if obj.hide_viewport:
                    continue

                # 移除顶级父级物体名称的数字后缀
                top_parent_name_no_suffix = top_parent.name.split('.')[0]
                top_parent.name = top_parent_name_no_suffix

                # 获取顶级父级物体的直接子物体
                direct_children = [
                    child for child in selected_objects if child.parent == top_parent]

                # 为顶级父级物体的直接子物体分配连贯的数字后缀
                for index, child in enumerate(direct_children, start=1):
                    new_name = get_sequential_suffix(
                        top_parent_name_no_suffix, index)
                    child.name = new_name

        # 在 Blender 中执行该函数
        rename_selected_objects_with_sequential_suffixes()
        return {"FINISHED"}

#重命名为所处集合名称
class RenameSelectedObjects(bpy.types.Operator):
    bl_idname = "object.rename_to_collection"
    bl_label = "所选物体命名为其所在集合名称"

    def execute(self, context):
        # 获取当前选中的物体
        selected_objects = context.selected_objects
        
        for obj in selected_objects:
            # 创建一个列表用来存储obj的所有父集合
            parents = []
            
            # 遍历所有集合以找到obj的父辈
            for coll in bpy.data.collections:
                if obj.name in coll.objects:
                    parents.append(coll)
            
            # 只有当obj有父集合时，才给obj重命名
            if parents:
                # 根据索引，obj的新名字将等于第一个父集合的名字
                obj.name = parents[0].name

        return {"FINISHED"}

#按照集合中物体位置对应修改名称
def distance(vecA, vecB):
    delta = np.array(vecB) - np.array(vecA)
    return np.linalg.norm(delta)

def center(collection):
    centers = []
    for obj in collection.objects:
        if obj.type == 'MESH':
            world_vertex_coordinates = [obj.matrix_world @ v.co for v in obj.data.vertices]
            center = np.mean(world_vertex_coordinates, axis=0)
            centers.append(center)
    return np.mean(centers, axis=0)

def rename_collections(self, context):
    collectionA = context.scene.collectionA
    collectionB = context.scene.collectionB
    collections_in_B = [coll for coll in collectionB.children]
    top_level_objs_in_A = [obj for obj in collectionA.objects if obj.parent is None]

    for collB in collections_in_B:
        closest_top_objA = min(top_level_objs_in_A, key=lambda objA: distance(center(collB), objA.location))
        collB.name = closest_top_objA.name

class OBJECT_OT_RenameButton(bpy.types.Operator):
    bl_idname = "object.miao_rename_collections"
    bl_label = "Rename Collections"
    bl_description = "Rename collections based on closest object in target collection"

    def execute(self, context):
        rename_collections(self, context)
        return {'FINISHED'}

#按照集合位置划分绑定父级
def set_nearest_parent_for_collection(self, context):
    collectionA = context.scene.collectionA
    collectionB = context.scene.collectionB
    collections_in_B = [coll for coll in collectionB.children]
    top_level_objs_in_A = [obj for obj in collectionA.objects if obj.parent is None]

    for collB in collections_in_B:
        collB_center = center(collB)
        closest_top_objA = min(top_level_objs_in_A, key=lambda objA: distance(collB_center, objA.location))
        for objB in collB.objects:
            closest_top_objA.select_set(True) 
            context.view_layer.objects.active = closest_top_objA
            objB.select_set(True)
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            closest_top_objA.select_set(False) 
            objB.select_set(False)
            collB.name = closest_top_objA.name
class OBJECT_OT_SetParentButton(bpy.types.Operator):
    bl_idname = "object.miao_set_parent_collections"
    bl_label = "Set Parent Collections"
    bl_description = "Set parent of collections based on closest object in target collection"

    def execute(self, context):
        set_nearest_parent_for_collection(self, context)
        return {'FINISHED'}
    
#按照集合对齐顶级父级
class OBJECT_OT_AlignOperator(bpy.types.Operator):
    bl_idname = "object.align_operator"
    bl_label = "集合父级批量对齐"
    
    def execute(self, context):
        def get_all_top_level_objects(collection):
            top_objects = [obj for obj in collection.objects if obj.parent is None]
            return top_objects

        def strip_suffix(name):
            return name.split(".")[0]
        collection_a = context.scene.collectionA
        collection_b = context.scene.collectionB

        # To get all top-level objects in collection A and B
        top_objects_a = get_all_top_level_objects(collection_a)
        top_objects_b = get_all_top_level_objects(collection_b)

        # Move each top-level object in Collection B to match position of top-level object in Collection A with same name
        for parent_a in top_objects_a:
            for obj_b in top_objects_b:
                obj_name = strip_suffix(obj_b.name)
                if strip_suffix(parent_a.name) == obj_name:

                    # Store child object's world matrix
                    old_world_matrices = {child: child.matrix_world.copy() for child in obj_b.children}

                    # Set object's location to match with parent_a
                    obj_b.matrix_world = parent_a.matrix_world

                    # Restore the world matrix of the child objects
                    for child in obj_b.children:
                        child.matrix_world = old_world_matrices[child]

        self.report({'INFO'}, "对集合进行了位置对齐")
        return {'FINISHED'}

#根据uv进行选择物体

#根据uv进行选择面
def get_selected_uv_set(ob):
    uv_set = set()   # 创建一个空集合来存储UV数据

    bm = bmesh.new()
    bm.from_mesh(ob.data)

    if bm.loops.layers.uv:  # Check if the object has UV data
        uv_layer = bm.loops.layers.uv.active  # 获取物体的UV层 
        for face in bm.faces:
            for loop in face.loops:    # 获取每个面的环
                uv_set.add(loop[uv_layer].uv.to_tuple())

    return uv_set

# 检查两个UV集合是否相等
def uv_sets_equal(set_a, set_b):
    return set_a == set_b
  
# 相比单独的脚本，插件的不同之处在于需要定义一个操作并注册这个操作
class UVObjectMatcherOperator(bpy.types.Operator):
    bl_idname = "object.match_uv"
    bl_label = "选取同uv物体"

    def execute(self, context):
        selected_object = context.active_object
        if selected_object is None or selected_object.type != 'MESH':
            return {"CANCELLED"}

        selected_object_uv_set = get_selected_uv_set(selected_object)
  
        for obj in context.view_layer.objects:
            if obj.type == 'MESH' and obj != selected_object:  # 忽略非网格物体及活动物体
                obj_uv_set = get_selected_uv_set(obj)

                if uv_sets_equal(selected_object_uv_set, obj_uv_set):
                    obj.select_set(True)
                else:
                    obj.select_set(False)

        return {"FINISHED"}

# 重置所选矢量
class ResetNormals(bpy.types.Operator):
    bl_idname = "object.miao_reset_normals"
    bl_label = "重置所选矢量"

    def execute(self, context):
        # 获取当前激活的物体
        active_object = bpy.context.active_object
        # 如果当前没有激活物体，从对象列表中选中第一个物体并将其设为活跃物体
        if active_object is None:
            first_object = bpy.context.selectable_objects[0] if bpy.context.selectable_objects else None

            if first_object is not None:
                first_object.select_set(True)
                bpy.context.view_layer.objects.active = first_object
                active_object = first_object

        # 检查当前激活的物体是否为 Mesh 类型
        if active_object is not None and active_object.type == 'MESH':

            # 使当前物体处于编辑模式
            bpy.ops.object.editmode_toggle()
            # 确保所有顶点被选中
            bpy.ops.mesh.select_all(action='SELECT')
            # 重置法线矢量
            bpy.ops.mesh.normals_tools(mode='RESET')
            # 返回物体模式
            bpy.ops.object.editmode_toggle()

        else:
            print("当前没有活跃 Mesh 类型物体，请确保您有可选择的 Mesh 物体。")

        return {"FINISHED"}

class ResetNormalsAndFlatShadingOperator(bpy.types.Operator):
    bl_idname = "object.reset_normals_flat_shading"
    bl_label = "Reset Normals and Flat Shading"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        for obj in selected_objects:
            # 如果当前物体的类型不是 'MESH'，那么就跳过后续处理
            if obj.type != 'MESH':
                continue
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.0001)
            bpy.ops.object.mode_set(mode='OBJECT')
            print(f"合并顶点成功：{obj}")

            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.normals_tools(mode='RESET')
            bpy.ops.object.mode_set(mode='OBJECT')
            print(f"重置矢量成功：{obj}")

            obj_data = obj.data
            if obj_data.materials:
                for mat in obj_data.materials:
                    for poly in obj_data.polygons:
                        poly.use_smooth = False

        return {'FINISHED'}

# 合并顶级层级
class MergeTopLevel(bpy.types.Operator):
  bl_idname = "object.miao_merge_top_level"
  bl_label = "合并顶级层级"

  def execute(self, context):

    selected_objs = context.selected_objects

    def merge_objects(objects, parent):
        bpy.ops.object.select_all(action='DESELECT')

        for obj in objects:
            # Creates a unique copy of object data
            bpy.data.objects[obj.name].data = obj.data.copy()
            obj.select_set(True)
            context.view_layer.objects.active = obj

        # Apply transforms before merging
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Merge selected objects using built-in command
        bpy.ops.object.join()

        merged_obj = context.object
        merged_obj.name = f"{parent.name}_merged"
        merged_obj.parent = parent

        bpy.ops.object.select_all(action='DESELECT')
        merged_obj.select_set(True)

    for obj in selected_objs:
        parent = obj.parent 
        matrix_world = obj.matrix_world.copy()

        while parent and parent.parent:
            obj.parent = parent.parent
            parent = parent.parent

        if parent:
            obj.parent = parent

        obj.matrix_world = matrix_world

    top_parents = set()
    for obj in selected_objs:
        if obj.parent:
            top_parents.add(obj.parent)

    for parent in top_parents:
        children = [child for child in parent.children 
                if child in selected_objs and child.type=='MESH']

        if len(children) > 1:
            merge_objects(children, parent)

    return {'FINISHED'}

# 对选择的物体进行独立化，应用变换

class ApplyAndSeparate(bpy.types.Operator):
    bl_idname = "object.miao_apply_and_separate"
    bl_label = "独立化、应用所有变换"

    def execute(self, context):
        # 获取当前所选物体
        selected_objects = context.selected_objects
        print(f"开始执行操作，选中了 {len(selected_objects)} 个物体。")

        for obj in selected_objects:
            print(f"正在处理物体: {obj.name}")
            self.separate_objects(obj)
            self.apply_transformations(obj)
        print("操作完成。")
        return {'FINISHED'}

    def apply_transformations(self, obj):
        # 设置为活动物体
        context = bpy.context
        context.view_layer.objects.active = obj
        obj.select_set(True)
        print(f"应用变换: {obj.name}")

        # 确保我们在对象模式
        bpy.ops.object.mode_set(mode='OBJECT')

        # 应用所有变换
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        print(f"已应用变换: {obj.name}")

    def separate_objects(self, obj):
        # 设置为活动物体
        context = bpy.context
        context.view_layer.objects.active = obj
        obj.select_set(True)
        print(f"独立物体: {obj.name}")

        # 隔离对象为独立副本
        bpy.ops.object.make_single_user(
            object=True, obdata=True, material=False, animation=False, obdata_animation=False)
        print(f"物体已独立: {obj.name}")

# 清理空物体
class CleanEmpty(bpy.types.Operator):
    bl_idname = "object.miao_clean_empty"
    bl_label = "清理所选空物体"

    def execute(self, context):
        # 遍历所选的物体
        for obj in bpy.context.selected_objects:
            # 检查物体是否为空
            if obj.type == 'EMPTY':
                # 从场景中删除空物体
                bpy.data.objects.remove(obj)

        # 更新场景
        bpy.context.view_layer.update()
        return {"FINISHED"}
        ####

# 递归清理场景
class CleanSense(bpy.types.Operator):
    bl_idname = "object.miao_clean_sense"
    bl_label = "清理场景"

    def execute(self, context):
        def remove_unused_data_blocks():
            # 删除未使用的万花筒
            bpy.ops.outliner.orphans_purge()

            # 删除未使用的材质
            for material in bpy.data.materials:
                if not material.users:
                    bpy.data.materials.remove(material)

            # 删除未使用的纹理
            for texture in bpy.data.textures:
                if not texture.users:
                    bpy.data.textures.remove(texture)

            # 删除未使用的节点分组（Node groups）
            for node_group in bpy.data.node_groups:
                if not node_group.users:
                    bpy.data.node_groups.remove(node_group)

            # 删除未使用的颜色距（Color Ramps）
            for color_ramp in bpy.data.node_groups:
                if not color_ramp.users:
                    bpy.data.node_groups.remove(color_ramp)

            # 删除未使用的画笔
            for brush in bpy.data.brushes:
                if not brush.users:
                    bpy.data.brushes.remove(brush)

            # 删除未使用的贴图
            for image in bpy.data.images:
                if not image.users:
                    bpy.data.images.remove(image)

        def recursive_cleanup(num_iterations=5):
            for _ in range(num_iterations):
                data_sizes = [
                    len(bpy.data.materials),
                    len(bpy.data.textures),
                    len(bpy.data.node_groups),
                    len(bpy.data.brushes),
                    len(bpy.data.images),
                ]

                remove_unused_data_blocks()

                new_data_sizes = [
                    len(bpy.data.materials),
                    len(bpy.data.textures),
                    len(bpy.data.node_groups),
                    len(bpy.data.brushes),
                    len(bpy.data.images),
                ]

                if data_sizes == new_data_sizes:
                    break

        recursive_cleanup()

        return {"FINISHED"}

# 批量关联目录内所有blender文件场景
class SCENE_OT_link_scenes_from_blend_files(bpy.types.Operator):
    bl_idname = "scene.link_scenes_batch"
    bl_label = "从选定目录中的.blend文件批量关联场景"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.types.Scene.export_directory = bpy.props.StringProperty(
            name="Export Directory",
            description="Directory where the exported files will be written"
        )

        directory = context.scene.export_directory

        # 检查路径是否有效，同时兼容使用相对路径
        if directory.startswith('//'):
            directory = bpy.path.abspath(directory)

        if not os.path.exists(directory):
            self.report({'ERROR'}, f"目录 '{directory}' 不存在。")
            return {'CANCELLED'}

        for filename in os.listdir(directory):
            if filename.endswith(".blend"):
                blend_filepath = os.path.join(directory, filename)
                with bpy.data.libraries.load(blend_filepath, link=True) as (data_from, data_to):
                    data_to.scenes = data_from.scenes

                for scene in data_to.scenes:
                    if scene is not None:
                        bpy.context.window.scene = scene
                        bpy.context.view_layer.update()
                        message = f"已关联场景 '{scene.name}' 来自 '{blend_filepath}'."
                        print(message)
                        self.report({'INFO'}, message)
                    else:
                        message = f"'{blend_filepath}' 中没有场景可以关联."
                        print(message)
                        self.report({'INFO'}, message)

        return {'FINISHED'}

# 排序场景列表
class SCENE_OT_sort_scenes(bpy.types.Operator):
    bl_idname = "scene.sort_scenes"
    bl_label = "按名称排序场景"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene_list = list(bpy.data.scenes)

        def natural_sort_key(s):
            return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', s)]

        # 使用自然排序对场景列表进行排序
        sorted_names = sorted(
            [scene.name for scene in scene_list], key=natural_sort_key)

        for scene, new_name in zip(scene_list, sorted_names):
            scene.name = new_name

        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'OUTLINER':
                    area.tag_redraw()

        return {'FINISHED'}

# 场景批量添加至时间轴
class SCENE_OT_add_sorted_scenes_to_sequencer(bpy.types.Operator):
    bl_idname = "scene.add_sorted_scenes_to_sequencer"
    bl_label = "将已排序的场景添加到序列编辑器"
    bl_options = {'REGISTER', 'UNDO'}

    def atoi(self, text):
        return int(text) if text.isdigit() else text

    def natural_keys(self, text):
        return [self.atoi(c) for c in re.split(r'(\d+)', text)]

    def execute(self, context):
        bpy.context.window.workspace = bpy.data.workspaces['Video Editing']
        bpy.ops.sequencer.select_all(action='DESELECT')
        bpy.ops.sequencer.delete()

        scene = bpy.context.scene
        sequencer = scene.sequence_editor

        if sequencer is None:
            sequencer = scene.sequence_editor_create()

        start_frame = 1
        for scene_to_add in sorted(bpy.data.scenes, key=lambda s: self.natural_keys(s.name)):
            if scene_to_add == scene:
                continue

            scene_strip = sequencer.sequences.new_scene(
                name=scene_to_add.name, scene=scene_to_add, channel=1, frame_start=start_frame)
            start_frame += scene_strip.frame_final_duration

        return {'FINISHED'}

# 随机材质球颜色
class OBJ_OT_random_meterial(bpy.types.Operator):
    bl_idname = "scene.random_meterial"
    bl_label = "随机材质球颜色"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        def random_color(colors_set):
            while True:
                color = (random.random(), random.random(), random.random(), 1)
                if color not in colors_set:
                    colors_set.add(color)
                    return color

        def create_diffuse_material(name, color):
            material = bpy.data.materials.new(name=name)
            material.use_nodes = True
            node_tree = material.node_tree

            # 获取 Principled BSDF 节点
            principled_bsdf_node = node_tree.nodes.get("Principled BSDF")

            # 更改颜色
            principled_bsdf_node.inputs["Base Color"].default_value = color
            return material

        def main():
            selected_objects = bpy.context.selected_objects
            used_colors = set()

            for obj in selected_objects:
                if obj.type == 'MESH':
                    material_slots = obj.material_slots
                    for index, material_slot in enumerate(material_slots):
                        unique_color = random_color(used_colors)

                        # 创建新的漫反射材质
                        new_material = create_diffuse_material(
                            obj.name + '_diffuse_' + str(index), unique_color)

                        # 替换现有材质
                        material_slot.material = new_material

        main()

        return {'FINISHED'}

# 下落至表面
class OBJECT_OT_move_to_surface(bpy.types.Operator):
    bl_idname = "object.move_to_surface"
    bl_label = "下落至表面"
    bl_options = {'REGISTER', 'UNDO'}

    def create_tree_from_object(self, obj):
        bm = bmesh.new()
        bm.from_object(obj, bpy.context.evaluated_depsgraph_get())
        bm.transform(obj.matrix_world)
        bvh = BVHTree.FromBMesh(bm)
        bm.free()
        return bvh

    def get_bbox_bottom_center(self, obj):
        local_bbox = obj.bound_box
        dimensions = obj.dimensions
        bbox_bottom_center = sum((Vector(v) for v in local_bbox), Vector()) / 8
        bbox_bottom_center.z = min(v[2] for v in local_bbox)
        return bbox_bottom_center

    def get_contact_point(self, target_tree, sel_obj):
        bbox_bottom_center = self.get_bbox_bottom_center(sel_obj)
        world_bbox_bottom_center = sel_obj.matrix_world @ bbox_bottom_center
        direction = Vector((0, 0, -1))

        co, normal, _, _ = target_tree.ray_cast(
            world_bbox_bottom_center + direction * 0.001, direction, 1000)

        if co is not None:
            displacement = co.z - world_bbox_bottom_center.z
            return displacement

        return 0

    def move_to_surface(self, target_tree, scene, sel_obj):
        displacement = self.get_contact_point(target_tree, sel_obj)
        if displacement != 0:
            sel_obj.location.z += displacement

    def execute(self, context):
        selected_objects = context.selected_objects
        scene = context.scene

        if len(selected_objects) < 2:
            self.report({"ERROR"}, "选择至少两个物体，一个作为参考物体，其余为要移动的物体。")
            return {"CANCELLED"}

        target_obj = context.active_object
        moving_objects = [o for o in selected_objects if o is not target_obj]

        target_tree = self.create_tree_from_object(target_obj)

        for obj in moving_objects:
            self.move_to_surface(target_tree, scene, obj)

        return {"FINISHED"}

#清理无子集空物体
class OBJECT_OT_clean_empty(bpy.types.Operator):
    """My Object Empty Deleting Script"""
    bl_idname = "object.clean_empty"
    bl_label = "清除无子集空物体"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # 获取当前场景的所有对象
        scene_objects = context.scene.objects
        # 收集所有没有子对象的空物体
        empties_to_delete = [obj for obj in scene_objects if obj.type == 'EMPTY' and not obj.children]
        # 删除这些空物体
        for empty in empties_to_delete:
            bpy.data.objects.remove(empty)
        
        self.report({'INFO'}, f"Deleted {len(empties_to_delete)} empty objects without children.")

        return {'FINISHED'}

classes = [
    OBJECT_OT_clean_empty,
    # CharOperaterBoneWeight,
    CharOperater,
    ParentByBoundingbox,
    OBJECT_OT_move_object_origin_to_bottom,
    OBJECT_OT_remove_suffix_and_resolve_conflicts,
    OBJECT_OT_make_single_user,
    OBJECT_OT_convex_hull_creator,
    VoxelConverter,
    CollectionByAttached,
    RemoveModifiers,
    SelectSmallObjectsOperator,
    RenameObjectsOperator,
    VoxOperation,
    ResetNormalsAndFlatShadingOperator,
    SelectLargeObjectsOperator,
    ExporteObjOperator,
    SetTextureInterpolation,
    OBJECT_OT_AlignOperator,
    MoveOutsideOperator,
    FixSizeOperator,
    RemoveNameSuffix,
    OBJECT_OT_SetParentButton,
    OBJECT_OT_RenameButton,
    RenameSelectedObjects,
    ClearAnimationData,
    SetEmissionStrength,
    OBJECT_OT_move_to_surface,
    OBJ_OT_random_meterial,
    SCENE_OT_add_sorted_scenes_to_sequencer,
    SCENE_OT_sort_scenes,
    SCENE_OT_link_scenes_from_blend_files,
    CleanSense,
    CleanEmpty,
    MergeTopLevel,
    ApplyAndSeparate,
    ResetNormals,
    CollectionByDistance,
    CleanCollection,
    SelectByVolume,
    MaterialSort,
    BoundboxGen,
    CombinObject,
    RemoveVertexGroup,
    RotationOperator,
    RenameByLocation,
    QueueUp,
    AlignmentGround,
    RandomPlacement,
    MergeMaterial,
    CollectionByBoundingbox,
    AlignOrign,
    CreateEmptyAtObjectBottom,
    CreateAssemblyAsset,
    RenameByParent,
    RandomScale,
    RenameMeshesOperator,
    UVObjectMatcherOperator,
]

def register():

    bpy.types.Scene.rename_axis = EnumProperty(
        name="轴向",
        items=[
            ("X", "X轴", "按X轴顺序重命名"),
            ("Y", "Y轴", "按Y轴顺序重命名"),
            ("Z", "Z轴", "按Z轴顺序重命名")
        ],
        default="Y"
    )
    bpy.types.Scene.rename_order = bpy.props.EnumProperty(
        name="排序类型",
        items=[
            ("ASC", "正序", "按正序重新命名"),
            ("DESC", "倒序", "按倒序重新命名")
        ],
        default="ASC"
    )
    bpy.types.Scene.random_placement_extent = bpy.props.FloatVectorProperty(
        name="范围大小",
        description="设置随机放置的范围大小",
        default=(10, 10, 10),
        size=3
    )
    bpy.types.Scene.create_top_level_parent = bpy.props.BoolProperty(
        name="创建顶级父物体",
        description="设置是否为每个资产创建一个顶级父物体",
        default=True
    )
    bpy.types.Scene.asset_collection = bpy.props.PointerProperty(
        name="集合",
        description="选择将要标记资产的集合",
        type=bpy.types.Collection
    )
    bpy.types.Scene.multiple_object_binding = bpy.props.BoolProperty(
        name="Multiple Object Binding",
        description="为多个物体创建单个空物体父级",
        default=True)
    bpy.types.Scene.link_scenes_batch_directory = bpy.props.StringProperty(
        name="目录",
        description="包含 .blend 文件的目录",
        subtype='DIR_PATH',
        maxlen=1024
    )
    bpy.types.Scene.tools_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.GTAtranslate_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.BindOperation_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.meterialoperation_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.assestoperation_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.renameoperation_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.rsm_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.inout_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.renderadj_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.collectionA = PointerProperty(name="Collection A", type=bpy.types.Collection)
    bpy.types.Scene.collectionB = PointerProperty(name="Collection B", type=bpy.types.Collection)
    bpy.types.Scene.export_directory = bpy.props.StringProperty(
        name="导出路径",
        description="设置导出FBX文件的路径",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')
    bpy.types.Scene.autorender_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.collectionA = PointerProperty(type=Collection)
    bpy.types.Scene.collectionB = PointerProperty(type=Collection)

    for cls in classes:
        bpy.utils.register_class(cls)

def is_class_registered(cls):
    return hasattr(cls, "bl_rna")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.collectionB
    del bpy.types.Scene.collectionA
    del bpy.types.Scene.random_placement_extent
    del bpy.types.Scene.rename_order
    del bpy.types.Scene.export_directory
    del bpy.types.Scene.asset_collection
    del bpy.types.Scene.create_top_level_parent
    del bpy.types.Scene.multiple_object_binding
    del bpy.types.Scene.link_scenes_batch_directory
    del bpy.types.Scene.rename_axis
    bpy.types.Scene.tools_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.GTAtranslate_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.BindOperation_expand = bpy.props.BoolProperty(
        default=False)
    bpy.types.Scene.meterialoperation_expand = bpy.props.BoolProperty(
        default=False)
    bpy.types.Scene.assestoperation_expand = bpy.props.BoolProperty(
        default=False)
    bpy.types.Scene.renameoperation_expand = bpy.props.BoolProperty(
        default=False)
    bpy.types.Scene.rsm_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.inout_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.renderadj_expand = bpy.props.BoolProperty(default=False)
