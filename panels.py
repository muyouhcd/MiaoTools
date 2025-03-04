import bpy
from .MaterialOperator import SetEmissionStrength, SetMaterialRoughness
from .renderconfig import BATCH_RESOLUTION_OT_ExecuteButton

class CustomFunctionsPanel(bpy.types.Panel):
    bl_label = "工具盒"
    bl_idname = "VIEW3D_PT_custom_functions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "工具盒"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
# 小工具集合
        col_tools = layout.column()
        col_tools.prop(scene, "tools_expand", text="工具集", emboss=False,
                       icon='TRIA_DOWN' if context.scene.tools_expand else 'TRIA_RIGHT')

        if scene.tools_expand:
            # Edit Tools
            layout.label(text="编辑:")
            edit_box = layout.box()
            edit_box.operator("object.miao_remove_vertex_group", text="移除顶点组", icon='GROUP_VERTEX')
            edit_box.operator("object.remove_modifiers", text="移除修改器", icon='MODIFIER')
            edit_box.operator("object.miao_clean_collection", text="清空空集合", icon='OUTLINER_COLLECTION')
            edit_box.operator("object.clean_empty", text="清除无子集空物体", icon='OUTLINER_OB_EMPTY')
            edit_box.operator("object.make_single_user_operator", text="批量独立化物体", icon='OBJECT_DATA')
            edit_box.operator("object.miao_correct_rotation", text="矫正旋转", icon='CON_ROTLIMIT')
            # Animation Tools
            layout.label(text="动画:")
            anim_box = layout.box()
            anim_box.operator("object.clear_animation_data", text="批量清空动画", icon='ANIM_DATA')
            # Generation Tools
            layout.label(text="生成:")
            gen_box = layout.box()
            gen_box.operator("object.miao_boundbox_gen", text="生成包围盒", icon='MESH_CUBE')
            gen_box.operator("object.convex_hull_creator", text="生成凸包", icon='META_ELLIPSOID')
            gen_box.operator("object.miao_safecombin", text="安全合并", icon='AUTOMERGE_ON')
            gen_box.operator("object.object_instance", text="转换实例化", icon='OUTLINER_OB_GROUP_INSTANCE')

            # Alignment Tools
            layout.label(text="对齐:")
            align_box = layout.box()
            align_box.prop(context.scene, "axis_direction_enum", text="Axis Direction")
            op = align_box.operator("object.move_origin", text="Move Origin")
            op.axis_direction = context.scene.axis_direction_enum
            align_box.operator("object.reset_z_axis", text="z轴归零")

            # Selection Tools
            layout.label(text="选择:")
            select_box = layout.box()
            select_box.operator("object.match_uv", text="选取同UV物体", icon='GROUP_UVS')
            select_box.operator("object.select_large_objects", text="选择过大物体", icon='FULLSCREEN_ENTER')
            select_box.operator("object.select_small_objects", text="选择过小物体", icon='FULLSCREEN_EXIT')
            select_box.operator("object.select_objects_without_texture", text="选择没有贴图物体", icon='FILE_BLANK')

            #清理工具
            layout.label(text="清理:")
            clean_box = layout.box()
            clean_box.operator("object.clean_meshes_without_faces", text="清理无实体物体", icon='BRUSH_DATA')
            clean_box.operator("object.uv_cleaner", text="清理uv非法数据", icon='BRUSH_DATA')
            clean_box.operator("image.remove_broken", text="清理丢失图像", icon='BRUSH_DATA')

            layout.label(text="合并:")
            convert_box = layout.box()
            convert_box.operator("object.combin_same_origin_object", text="合并同原点物体", icon='MOD_REMESH')

            
            
# 绑定操作
        col_BindOperation = layout.column()
        col_BindOperation.prop(scene, "BindOperation_expand", text="绑定集合", emboss=False,
                               icon='TRIA_DOWN' if context.scene.BindOperation_expand else 'TRIA_RIGHT')
        if context.scene.BindOperation_expand:

            layout.label(text="碰撞检测与集合绑定:")
            bounding_box_operations = layout.box()
            bounding_box_operations.operator("object.miao_collection_byboundingbox", text="检测碰撞归集合", icon='MESH_CIRCLE')
            bounding_box_operations.operator("object.miao_parent_byboundingbox", text="检测碰撞归子集", icon='FILE_PARENT')
            bounding_box_operations.operator("object.collection_by_attached", text="检测并合并碰撞", icon='MESH_CIRCLE')
            
            # Parent By Collections
            layout.label(text="集合父级设置:")
            parent_by_collections_box = layout.box()
            parent_by_collections_box.label(text="以集合物体绑定子集合父级")
            parent_by_collections_box.prop(scene, "collectionA", text="集合 A")
            parent_by_collections_box.prop(scene, "collectionB", text="集合 B")
            parent_by_collections_box.operator("object.miao_set_parent_collections", text="设置父级", icon='FILE_PARENT')

            # Empty Parent Binding
            layout.label(text="绑定空物体父级:")
            create_empty_at_origin_box = layout.box()
            create_empty_at_origin_box.prop(scene, "multiple_object_binding", text="为多个物体绑定")
            create_empty_at_origin_box.operator("object.miao_create_empty_at_bottom", text="创建空物体父级", icon='MESH_CIRCLE')

# 材质操作
        col_meterialoperation = layout.column()
        col_meterialoperation.prop(scene, "meterialoperation_expand", text="材质", emboss=False,
                                   icon='TRIA_DOWN' if context.scene.meterialoperation_expand else 'TRIA_RIGHT')

        if context.scene.meterialoperation_expand:
            uv_box = layout.box()
            uv_box.label(text="UV操作:")
            uv_box.operator("object.uv_formater", text="UV尺寸校准", icon='UV_DATA')
            uv_box.operator("object.quad_uv_aligner", text="UV铺满展开", icon='UV')
            uv_box.operator("object.correct_uv_rotation", text="UV旋转矫正", icon='MOD_UVPROJECT')

            emission_box = layout.box()
            emission_box.label(text="材质强度调整:")
            emission_box.prop(context.scene, "emission_strength", text="发光强度", slider=True)
            emission_box.operator(SetEmissionStrength.bl_idname).strength = context.scene.emission_strength
            emission_box.prop(context.scene, "roughness_strength", text="粗糙强度", slider=True)
            emission_box.operator(SetMaterialRoughness.bl_idname).roughness = context.scene.roughness_strength

            material_operations_box = layout.box()
            material_operations_box.label(text="材质球操作:")
            material_operations_box.operator("object.alpha_node_connector", text="图像Alpha节点连接", icon='NODETREE')
            material_operations_box.operator("object.alpha_node_disconnector", text="断开Alpha连接", icon='NODETREE')
            material_operations_box.operator("object.alpha_to_skin", text="Alpha通道设置为肤色", icon='NODETREE')
            material_operations_box.operator("object.set_texture_interpolation", text="设置临近采样（硬边缘）", icon='TEXTURE_DATA')

            texture_operater_box = layout.box()
            texture_operater_box.label(text="贴图自动链接")
            texture_operater_box.prop(context.scene, "texture_dir", text="贴图路径", icon='FILE_FOLDER')
            texture_operater_box.operator("object.apply_texture_operator", text="批量链接贴图(完整匹配)", icon='NODE_TEXTURE')

            texture_operater_box.prop(scene, "ignore_fields_input", text="忽略字段列表", icon='FILE_TEXT')
            texture_operater_box.operator("object.apply_texture_to_selected_objects", text="批量链接贴图(忽略匹配)", icon='NODE_TEXTURE')
            texture_operater_box.operator("object.apply_texture_to_materials", text="批量链接贴图(材质球名称匹配)", icon='NODE_TEXTURE')
            # 材质球排序
            material_manager_box = layout.box()
            material_manager_box.label(text="材质管理:")
            material_manager_box.operator("object.miao_material_sort", text="材质球排序", icon='SORTSIZE')
            material_manager_box.operator("scene.random_meterial", text="随机材质", icon='OUTLINER_OB_POINTCLOUD')
            material_manager_box.operator("object.miao_merge_material", text="清理材质", icon='BRUSH_DATA')
            material_manager_box.operator("object.remove_unused_material_slots", text="清理空材质槽", icon='BRUSH_DATA')
            material_manager_box.operator("object.material_cleaner", text="重复材质（.00x后缀）合并", icon='BRUSH_DATA')

# 命名操作
        col_renameoperation = layout.column()
        col_renameoperation.prop(scene, "renameoperation_expand", text="重命名", emboss=False,
                                 icon='TRIA_DOWN' if context.scene.renameoperation_expand else 'TRIA_RIGHT')

        if context.scene.renameoperation_expand:

            box_auto_rename_car = col_renameoperation.box()
            box_auto_rename_car.label(text="车辆部件自动重命名")
            box_auto_rename_car.operator("object.miao_auto_rename_car", text="UnityCar自动重命名", icon='SYNTAX_ON')
            box_auto_rename_car.operator("object.miao_auto_rename_car_for_rigcar", text="RigCar自动重命名", icon='SYNTAX_ON')

            spatial_rename_box = col_renameoperation.box()
            spatial_rename_box.operator("object.miao_rename_by_parent", text="子级命名为顶级", icon='OUTLINER_OB_EMPTY')

            # Rename Objects to Collection Name
            spatial_rename_box.operator("object.rename_to_collection", text="命名为所处集合名称", icon='GROUP')

            # Remove Name Suffix
            remove_suffix_box = col_renameoperation.box()
            remove_suffix_box.label(text="移除名称后缀:")

            remove_suffix_box.operator("object.miao_remove_name_suffix", text="移除后缀", icon='X')
            remove_suffix_box.operator("object.remove_suffix_and_resolve", text="移除顶级后缀并解决重名", icon='X')
            
            # Naming Conventions
            naming_convention_box = col_renameoperation.box()
            naming_convention_box.label(text="Mesh-物体:")
            naming_convention_box.operator("object.rename_meshes", text="Mesh命名为物体", icon='OUTLINER_DATA_MESH')
            naming_convention_box.operator("object.rename_objects", text="物体命名为Mesh", icon='OBJECT_DATA')

            #贴图改名工具
            layout.label(text="贴图改名:")
            convert_box = layout.box()
            convert_box.operator("object.rename_texture_orign", text="贴图改名为原始名称", icon='MOD_REMESH')

            # Rename by Location Within Collections
            box_rename_by_collections = col_renameoperation.box()
            box_rename_by_collections.label(text="集合内位置重命名:")
            box_rename_by_collections.prop(context.scene, "collectionA", text="集合 A")
            box_rename_by_collections.prop(context.scene, "collectionB", text="集合 B")
            box_rename_by_collections.operator("object.miao_rename_collections", text="按位置重命名集合", icon='SORTSIZE')
            # Rename by Location
            box_rename_by_location = col_renameoperation.box()
            box_rename_by_location.label(text="根据位置重命名:")
            box_rename_by_location.prop(context.scene, "rename_axis", text="轴向")
            box_rename_by_location.prop(context.scene, "rename_order", text="排序类型")
            box_rename_by_location.operator("object.miao_rename_location", text="按空间顺序重命名", icon='SORTSIZE')

# 旋转缩放位移操作
        col_rsm = layout.column()
        col_rsm.prop(scene, "rsm_expand", text="旋转位移缩放", emboss=False,
                     icon='TRIA_DOWN' if context.scene.rsm_expand else 'TRIA_RIGHT')
        if context.scene.rsm_expand:
            # 下落至表面
            layout.operator("object.move_to_surface")
            # 创建一个box来包含列队相关功能
            queue_up_box = layout.box()
            # queue_up_box.label(text="列队")
            queue_up_box.prop(context.scene, "queue_up_distance")
            queue_up_box.prop(context.scene, "queue_up_axis", text="轴向")
            queue_up_box.prop(context.scene, "use_bounding_box", text="使用包围盒")
            queue_up_box.operator("object.miao_queue_up",icon='SNAP_VERTEX')
            # 创建一个box来包含置乱位置相关功能
            random_placement_box = layout.box()
            # random_placement_box.label(text="置乱位置")
            random_placement_box.prop(context.scene, "random_placement_extent")
            random_placement_box.operator("object.miao_random_placement",icon='STICKY_UVS_DISABLE')
            # 创建一个box来包含置乱缩放相关功能
            random_scale_box = layout.box()
            # random_scale_box.label(text="置乱缩放")
            random_scale_box.prop(context.scene, "random_scale_extent_x")
            random_scale_box.prop(context.scene, "random_scale_extent_y")
            random_scale_box.prop(context.scene, "random_scale_extent_z")
            random_scale_box.operator("object.miao_random_scale")
            #对齐集合顶级父级
            align_parent_box = layout.box()
            align_parent_box.label(text="批量对齐顶级父物体")
            align_parent_box.prop(context.scene, "collectionA", text="集合A (参考)")
            align_parent_box.prop(context.scene, "collectionB", text="集合B (对齐目标)")
            align_parent_box.operator("object.align_operator")
# 动画操作
        # col_anm = layout.column()
        # col_anm.prop(scene, "anm_expand", text="动画操作", emboss=False,
        #             icon='TRIA_DOWN' if context.scene.anm_expand else 'TRIA_RIGHT')

        # if context.scene.anm_expand:
        #     anim_box = layout.box()
        #     anim_box.prop(context.scene, "rv_start_frame")
        #     anim_box.prop(context.scene, "rv_end_frame")
        #     anim_box.prop(context.scene, "rv_initial_visibility")
        #     anim_box.operator("object.set_render_visibility")

# 导入导出操作
        col_inout = layout.column()
        col_inout.prop(scene, "inout_expand", text="导入导出", emboss=False,
                       icon='TRIA_DOWN' if context.scene.inout_expand else 'TRIA_RIGHT')

        if context.scene.inout_expand:
            # Export Operations
            export_box = layout.box()
            export_box.label(text="批量导出")
            export_box.prop(context.scene, "export_directory", text="导出目录", icon='FILE_FOLDER')  # 添加目录选择器
            # Export FBX by Parent
            export_box.operator("scene.export_fbx_by_parent", text="按顶级父物体导出FBX", icon='EXPORT')
            # export_box.operator("scene.export_fbx_by_parent_without_apply", text="按顶级父物体导出FBX（保持变换）", icon='EXPORT')
            # Export FBX by ".col" Mark
            export_box.operator("scene.export_fbx_by_col_mark", text="按.col标记导出FBX", icon='EXPORT')
            # Export FBX by Collection
            export_box.operator("object.miao_output_fbx_as_collection", text="按集合分文件夹导出FBX", icon='EXPORT')
            # Batch Export OBJ
            export_box.operator("object.export_objs", text="批量导出OBJ", icon='EXPORT')
            # Batch Link Scenes from Directory
            link_scenes_batch_box = layout.box()
            link_scenes_batch_box.label(text="批量从目录关联场景")
            link_scenes_batch_box.prop(context.scene, "export_directory", text=".Blender文件目录", icon='LINK_BLEND')
            link_scenes_batch_box.operator("scene.link_scenes_batch", text="从.blend文件关联场景", icon='LINK_BLEND')
            # Sort Scenes List
            link_scenes_batch_box.operator("scene.sort_scenes", text="按名称排序时间轴场景", icon='SORTALPHA')
            # Add Sorted Scenes to Sequencer
            link_scenes_batch_box.operator("scene.add_sorted_scenes_to_sequencer", text="批量添加场景至时间轴", icon='SEQUENCE')



# 资产操作
        col_assestoperation = layout.column()
        col_assestoperation.prop(scene, "assestoperation_expand", text="批量转换资产", emboss=False,
                                 icon='TRIA_DOWN' if context.scene.assestoperation_expand else 'TRIA_RIGHT')
        if context.scene.assestoperation_expand:
            box_vox = col_assestoperation.box()
            box_vox.operator("object.vox_operation", text="导入VOX一键处理",icon='ALIASED')
            # box_character.operator("object.point_data_generator", text="角色点位数据生成", icon='AUTOMERGE_ON')
            # box_character.operator("object.bone_data_generator", text="角色骨骼数据生成", icon='AUTOMERGE_ON')

            # box_character.prop(scene,"assign_contact_weights", text="是否赋予权重")
            # box_character.prop(scene, "threshold_distance", text="接触阈值")

            box_assestoperation = col_assestoperation.box()
            box_assestoperation.operator("object.miao_apply_and_separate", text="1.独立化应用所有变换")
            box_assestoperation.operator("object.miao_merge_top_level", text="2.按顶级层级合并")
            box_assestoperation.operator("object.miao_reset_normals", text="3.重置所选矢量")
            box_assestoperation.operator("object.miao_clean_empty", text="4.清理所选空物体")
            box_assestoperation.operator("object.miao_clean_sense", text="5.递归清理场景")

            assembly_asset_box = col_assestoperation.box()
            assembly_asset_box.label(text="批量标记资产设置")
            assembly_asset_box.prop(context.scene, "asset_collection")
            assembly_asset_box.prop(context.scene, "create_top_level_parent")
            assembly_asset_box.operator("object.miao_create_assembly_asset")

            box_voxelizer = layout.box()
            box_voxelizer.prop(context.scene.voxelizer_tool, "path")
            box_voxelizer.prop(context.scene.voxelizer_tool, "voxelizer_path")
            # box_voxelizer.prop(scene, "generate_solid")
            box_voxelizer.operator("object.convert_voxelizer", text="一键转换vox",icon='ALIASED')
            box_voxelizer.operator("object.convert_voxelizer_color", text="一键转换vox(带颜色)",icon='ALIASED')
# 烘焙
            # box_bake = layout.box()
            # box_bake.operator("object.retopologize_and_bake", text="烘焙选中物体(Remesh)")
            # box_bake.operator("object.retopologize_and_bake_without_remesh", text="烘焙选中物体")

            layout.label(text="转换:")
            convert_box = layout.box()
            convert_box.operator("object.voxel_converter", text="生成体素化指令",icon='MESH_GRID')
            convert_box.prop(scene, "resolution_factor")

#批量渲染
        # 确保自动展开部分包括新的滑动条选项
        # 确保自动展开部分包括新的滑动条选项
        layout = self.layout
        scene = bpy.context.scene

        col_autorender = layout.column()
        col_autorender.prop(scene, "autorender_expand", text="批量渲染", emboss=False, 
                            icon='TRIA_DOWN' if scene.autorender_expand else 'TRIA_RIGHT')

        if scene.autorender_expand:
            box_autorender = col_autorender.box()

            box_autorender.operator("auto_render.oneclick",text="一键处理模型显示效果（硬边缘、自发光为0）",icon='RENDER_STILL')

            box_autorender.prop(bpy.context.scene.auto_render_settings, "output_path", text="输出路径",icon='FILE_FOLDER')
            box_autorender.prop(bpy.context.scene.auto_render_settings, "output_name", text="输出名称",icon='FILE_FOLDER')
            box_autorender.prop(bpy.context.scene.auto_render_settings, "output_format", text="输出格式",icon='FILE_IMAGE')
            box_autorender.prop(bpy.context.scene.auto_render_settings, "collections", text="渲染集合",icon='GROUP')
            box_autorender.prop(bpy.context.scene.auto_render_settings, "cameras", text="相机",icon='CAMERA_DATA')
            box_autorender.prop(bpy.context.scene.auto_render_settings, "focus_each_object", text="聚焦到每个物体（正交相机）")
            box_autorender.prop(bpy.context.scene.auto_render_settings, "margin_distance", text="边框距离（正交相机）")
            box_autorender.operator("auto_render.execute",text="渲染",icon='RENDER_STILL')
            
            box_autorender_blendefile = col_autorender.box()
            box_autorender_blendefile.label(text="批量渲染.blend文件")
            render_operator = box_autorender_blendefile.operator('auto_render.batch_render',text="渲染",icon='RENDER_STILL')
            box_autorender_blendefile.prop(render_operator, 'render_as_animation', text="渲染动画")

# 批量调整渲染设置
        col_renderadj = layout.column()
        col_renderadj.prop(scene, "renderadj_expand", text="批量调整渲染设置", emboss=False,
                           icon='TRIA_DOWN' if context.scene.renderadj_expand else 'TRIA_RIGHT')

        if context.scene.renderadj_expand:

            box_renderadj = col_renderadj.box()
            change_resolution_prop = context.scene.change_resolution_prop
            box_renderadj.prop(change_resolution_prop, "input_dir",text="blend文件目录")
            box_renderadj.prop(change_resolution_prop, "output_dir",text="输出路径")
            box_renderadj.prop(change_resolution_prop, "render_engine", text="渲染引擎")
            box_renderadj.prop(change_resolution_prop, "output_format", text="输出格式")
            box_renderadj.prop(change_resolution_prop, "output_file", text="渲染输出路径")
            box_renderadj.prop(change_resolution_prop, "output_resolution_x", text="宽度分辨率")
            box_renderadj.prop(change_resolution_prop, "output_resolution_y", text="高度分辨率")
            box_renderadj.prop(change_resolution_prop, "resolution_percentage", text="质量百分比")
            box_renderadj.prop(change_resolution_prop, "output_frame_rate", text="帧率")
            
            operator_instance = box_renderadj.operator(BATCH_RESOLUTION_OT_ExecuteButton.bl_idname,text="执行",icon='RENDER_STILL')

            # 添加操作按钮并传递输入参数
            operator_instance.output_file = change_resolution_prop.output_file
            operator_instance.render_engine = change_resolution_prop.render_engine
            operator_instance.output_format = change_resolution_prop.output_format
            operator_instance.input_dir = change_resolution_prop.input_dir
            operator_instance.output_dir = change_resolution_prop.output_dir
            operator_instance.output_resolution_x = str(change_resolution_prop.output_resolution_x)
            operator_instance.output_resolution_y = str(change_resolution_prop.output_resolution_y)
            operator_instance.resolution_percentage = str(change_resolution_prop.resolution_percentage)
            operator_instance.output_frame_rate = str(change_resolution_prop.output_frame_rate)

            
def register():
    bpy.utils.register_class(CustomFunctionsPanel)
    

def unregister():
    bpy.utils.unregister_class(CustomFunctionsPanel)
