import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty, PointerProperty, CollectionProperty
from bpy.types import Panel, PropertyGroup
from .MaterialOperator import SetEmissionStrength, SetMaterialRoughness
from .renderconfig import BATCH_RESOLUTION_OT_ExecuteButton

# 材质属性组
class MaterialPropertyGroup(PropertyGroup):
    material: PointerProperty(
        type=bpy.types.Material,
        name="材质"
    )

class CustomFunctionsPanel(Panel):
    bl_label = "工具箱"
    bl_idname = "VIEW3D_PT_custom_functions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "工具箱"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
# 小工具集合
        col_tools = layout.column()
        col_tools.prop(scene, "tools_expand", text="模型编辑工具集", emboss=False,
                       icon='TRIA_DOWN' if context.scene.tools_expand else 'TRIA_RIGHT')

        if scene.tools_expand:
            # Edit Tools
            layout.label(text="编辑工具:", icon='TOOL_SETTINGS')
            edit_box = layout.box()
            edit_box.operator("object.miao_remove_vertex_group", text="移除顶点组", icon='GROUP_VERTEX')
            edit_box.operator("object.remove_modifiers", text="移除修改器", icon='MODIFIER')
            edit_box.operator("object.make_single_user_operator", text="批量独立化物体", icon='UNLINKED')
            edit_box.operator("object.miao_correct_rotation", text="矫正旋转", icon='CON_ROTLIMIT')
            

            
            # Animation Tools
            layout.label(text="清理工具:", icon='BRUSH_DATA')
            clean_box = layout.box()
            clean_box.operator("object.miao_clean_collection", text="清空空集合", icon='OUTLINER_COLLECTION')
            clean_box.operator("object.clean_empty", text="清除无子集空物体", icon='OUTLINER_OB_EMPTY')
            clean_box.operator("object.clear_animation_data", text="批量清空动画", icon='ANIM_DATA')
            clean_box.operator("object.clean_meshes_without_faces", text="清理无实体物体", icon='MESH_DATA')
            clean_box.operator("object.uv_cleaner", text="清理UV非法数据", icon='UV')
            clean_box.operator("image.remove_broken", text="清理丢失图像", icon='IMAGE_DATA')
            
            # 场景简化工具
            layout.label(text="场景简化工具:", icon='VIEW_CAMERA')
            scene_clean_box = layout.box()
            scene_clean_box.operator("object.auto_hide_clean", text="创建AutoHidden集合并隐藏", icon='HIDE_OFF')
            scene_clean_box.operator("object.auto_hide_delete", text="直接删除不可见物体", icon='TRASH')

            # Generation Tools
            layout.label(text="生成工具:", icon='SHADERFX')
            gen_box = layout.box()
            gen_box.operator("object.miao_boundbox_gen", text="生成包围盒", icon='CUBE')
            gen_box.operator("object.convex_hull_creator", text="生成凸包", icon='META_CUBE')
            gen_box.operator("object.miao_safecombin", text="安全合并", icon='AUTOMERGE_ON')
            gen_box.operator("object.object_instance", text="转换实例化", icon='DUPLICATE')

            # Alignment Tools
            layout.label(text="对齐工具:", icon='ORIENTATION_GLOBAL')
            align_box = layout.box()
            align_box.prop(context.scene, "axis_direction_enum", text="轴向选择")
            op = align_box.operator("object.move_origin", text="移动原点")
            op.axis_direction = context.scene.axis_direction_enum
            align_box.operator("object.reset_z_axis", text="Z轴归零", icon='AXIS_TOP')

            # Selection Tools
            layout.label(text="选择工具:", icon='RESTRICT_SELECT_OFF')
            select_box = layout.box()
            select_box.operator("object.match_uv", text="选取同UV物体", icon='GROUP_UVS')
            select_box.operator("object.select_large_objects", text="选择过大物体", icon='FULLSCREEN_ENTER')
            select_box.operator("object.select_small_objects", text="选择过小物体", icon='FULLSCREEN_EXIT')
            select_box.operator("object.select_objects_without_texture", text="选择没有贴图物体", icon='TEXTURE')
            select_box.operator("object.select_objects_without_vertex_groups", text="选择没有顶点组物体", icon='GROUP_VERTEX')
            
            # 按名称列表筛选工具
            namelist_select_box = layout.box()
            namelist_select_box.label(text="按名称列表筛选:", icon='OUTLINER_OB_GROUP_INSTANCE')
            
            # 添加描述信息
            namelist_select_box.label(text="要保留的物体名称列表:", icon='TEXT')
            
            # 使用简单的输入框显示当前内容
            box_text = namelist_select_box.box()
            if scene.object_names_list:
                lines = scene.object_names_list.split('\n')
                if len(lines) > 5:  # 如果超过5行，只显示前5行和计数
                    for line in lines[:5]:
                        box_text.label(text=line)
                    box_text.label(text=f"... 共{len(lines)}行")
                else:
                    for line in lines:
                        box_text.label(text=line)
            else:
                box_text.label(text="(空)")
            
            # 添加编辑按钮
            edit_row = namelist_select_box.row(align=True)
            edit_row.operator("object.edit_names_list", text="在外部编辑器中编辑列表", icon='TEXT')
            if scene.temp_names_file_path:
                edit_row.operator("object.read_names_from_temp_file", text="加载已编辑的列表", icon='IMPORT')
            
            # 添加提示
            namelist_select_box.label(text="(编辑后保存文件，然后点击'加载已编辑的列表')")
            
            row = namelist_select_box.row()
            row.prop(scene, "delete_lights_option", text="删除所有灯光")
            row.prop(scene, "show_report_option", text="显示报告")
            namelist_select_box.operator("object.select_and_delete_by_name_list", text="按名称列表筛选物体", icon='TRASH')

            # 合并工具
            layout.label(text="合并工具:", icon='SNAP_MIDPOINT')
            convert_box = layout.box()
            convert_box.operator("object.combin_same_origin_object", text="合并同原点物体", icon='PIVOT_BOUNDBOX')
            
# 绑定操作
        col_BindOperation = layout.column()
        col_BindOperation.prop(scene, "BindOperation_expand", text="关联与绑定工具", emboss=False,
                               icon='TRIA_DOWN' if context.scene.BindOperation_expand else 'TRIA_RIGHT')
        if context.scene.BindOperation_expand:
            # 碰撞检测与集合绑定
            bounding_box_operations = col_BindOperation.box()
            bounding_box_operations.label(text="碰撞检测与集合绑定:", icon='MOD_BOOLEAN')
            
            col = bounding_box_operations.column(align=True)
            col.operator("object.miao_collection_byboundingbox", text="检测碰撞归集合", icon='SNAP_VOLUME')
            col.operator("object.miao_parent_byboundingbox", text="检测碰撞归子集", icon='SNAP_FACE')
            col.operator("object.collection_by_attached", text="检测并合并碰撞", icon='FACE_MAPS')
            
            # 集合父级设置
            parent_by_collections_box = col_BindOperation.box()
            parent_by_collections_box.label(text="集合父级设置:", icon='GROUP')
            parent_by_collections_box.label(text="以集合物体绑定子集合父级", icon='INFO')
            
            col = parent_by_collections_box.column()
            col.prop(scene, "collectionA", text="父级集合", icon='COLLECTION_COLOR_01')
            col.prop(scene, "collectionB", text="子级集合", icon='COLLECTION_COLOR_04')
            parent_by_collections_box.operator("object.miao_set_parent_collections", text="设置父级关系", icon='LINKED')

            # 空物体父级绑定
            empty_parent_box = col_BindOperation.box()
            empty_parent_box.label(text="空物体父级绑定:", icon='EMPTY_DATA')
            empty_parent_box.prop(scene, "multiple_object_binding", text="为多个物体创建共同父级")
            empty_parent_box.operator("object.miao_create_empty_at_bottom", text="创建空物体父级", icon='EMPTY_ARROWS')

# 材质操作
        col_meterialoperation = layout.column()
        col_meterialoperation.prop(scene, "meterialoperation_expand", text="材质与纹理工具", emboss=False,
                                   icon='TRIA_DOWN' if context.scene.meterialoperation_expand else 'TRIA_RIGHT')

        if context.scene.meterialoperation_expand:
            # UV操作
            uv_box = col_meterialoperation.box()
            uv_box.label(text="UV操作:", icon='MOD_UVPROJECT')
            row = uv_box.row(align=True)
            row.operator("object.uv_formater", text="UV尺寸校准", icon='UV_DATA')
            row.operator("object.correct_uv_rotation", text="UV旋转矫正", icon='DRIVER_ROTATIONAL_DIFFERENCE')
            uv_box.operator("object.quad_uv_aligner", text="UV铺满展开", icon='FULLSCREEN_ENTER')

            # 材质强度调整
            emission_box = col_meterialoperation.box()
            emission_box.label(text="材质强度调整:", icon='MATERIAL')
            row = emission_box.row()
            row.prop(context.scene, "emission_strength", text="发光强度", slider=True)
            row.operator(SetEmissionStrength.bl_idname, text="应用", icon='CHECKMARK').strength = context.scene.emission_strength
            
            row = emission_box.row()
            row.prop(context.scene, "roughness_strength", text="粗糙强度", slider=True)
            row.operator(SetMaterialRoughness.bl_idname, text="应用", icon='CHECKMARK').roughness = context.scene.roughness_strength

            row = emission_box.row()
            row.prop(context.scene, "metallic_strength", text="金属强度", slider=True)
            row.operator("object.set_metallic", text="应用", icon='CHECKMARK').metallic = context.scene.metallic_strength

            row = emission_box.row()
            row.prop(context.scene, "specular_strength", text="高光强度", slider=True)
            row.operator("object.set_specular", text="应用", icon='CHECKMARK').specular = context.scene.specular_strength

            row = emission_box.row()
            row.prop(context.scene, "specular_tint_strength", text="光泽度", slider=True)
            row.operator("object.set_specular_tint", text="应用", icon='CHECKMARK').specular_tint = context.scene.specular_tint_strength

            # 材质节点操作
            material_operations_box = col_meterialoperation.box()
            material_operations_box.label(text="材质节点操作:", icon='NODETREE')
            
            row1 = material_operations_box.row(align=True)
            row1.operator("object.alpha_node_connector", text="连接Alpha", icon='NODE_COMPOSITING')
            row1.operator("object.alpha_node_disconnector", text="断开Alpha", icon='TRACKING_REFINE_BACKWARDS')
            
            row2 = material_operations_box.row(align=True)
            row2.operator("object.alpha_to_skin", text="Alpha设为肤色", icon='OUTLINER_OB_ARMATURE')
            row2.operator("object.set_texture_interpolation", text="硬边缘采样", icon='SNAP_INCREMENT')
            
            row3 = material_operations_box.row(align=True)
            row3.operator("object.set_material_alpha_clip", text="设置Alpha裁剪模式", icon='CLIPUV_HLT')
            row3.operator("object.set_material_alpha_blend", text="设置Alpha混合模式", icon='SNAP_VOLUME')
            
            row4 = material_operations_box.row(align=True)
            row4.operator("object.set_shadow_invisible", text="设置选中物体阴影不可见", icon='GHOST_ENABLED')
            row4.operator("object.set_shadow_visible", text="设置选中物体阴影可见", icon='GHOST_DISABLED')

            row5 = material_operations_box.row(align=True)
            row5.operator("object.set_texture_alpha_packing", text="设置Alpha通道打包", icon='PACKAGE')

            # 贴图自动链接
            texture_operater_box = col_meterialoperation.box()
            texture_operater_box.label(text="贴图自动链接", icon='TEXTURE')
            
            col = texture_operater_box.column()
            col.prop(context.scene, "texture_dir", text="贴图路径", icon='FILE_FOLDER')
            col.prop(scene, "ignore_fields_input", text="忽略字段列表", icon='FILE_TEXT')
            
            # 匹配方法子框
            matching_methods_box = texture_operater_box.box()
            matching_methods_box.label(text="纹理匹配方法:", icon='IMGDISPLAY')
            
            # 基础匹配方法
            basic_matching_box = matching_methods_box.box()
            basic_matching_box.label(text="基础匹配:", icon='OBJECT_DATA')
            col = basic_matching_box.column(align=True)
            col.operator("object.apply_texture_operator", 
                       text="按物体名称匹配(完整)", 
                       icon='OBJECT_DATA')
            col.operator("object.apply_texture_to_selected_objects", 
                       text="按物体名称匹配(忽略字段)", 
                       icon='TOOL_SETTINGS')
            col.operator("object.apply_texture_to_materials", 
                       text="按材质名称匹配", 
                       icon='MATERIAL')
            col.operator("object.apply_texture_by_parent", 
                       text="按顶级父级名称匹配", 
                       icon='OUTLINER_OB_EMPTY')

            # 智能匹配方法
            smart_matching_box = matching_methods_box.box()
            smart_matching_box.label(text="智能匹配:", icon='AUTOMERGE_ON')
            col = smart_matching_box.column(align=True)
            col.operator("object.apply_texture_by_object_name",
                       text="按物体名称包含匹配",
                       icon='TEXTURE')
            col.operator("object.apply_texture_by_similarity",
                       text="按相似度匹配",
                       icon='SORTALPHA')
           
            # 材质管理
            material_manager_box = col_meterialoperation.box()
            material_manager_box.label(text="材质管理:", icon='MATERIAL_DATA')
            
            row1 = material_manager_box.row(align=True)
            row1.operator("object.miao_material_sort", text="材质球排序", icon='SORTSIZE')
            row1.operator("scene.random_meterial", text="随机材质", icon='NODE_TEXTURE')
            
            row2 = material_manager_box.row(align=True)
            row2.operator("object.miao_merge_material", text="清除材质", icon='TRASH')
            row2.operator("object.remove_unused_material_slots", text="清理空材质槽", icon='PANEL_CLOSE')
            
            row3 = material_manager_box.row(align=True)
            row3.operator("object.material_cleaner", text="合并重复材质(.00x后缀)", icon='DUPLICATE')
            row3.operator("object.merge_duplicate_materials", text="合并同名及相同参数材质", icon='MATERIAL')
            
            row4 = material_manager_box.row(align=True)
            row4.operator("object.clean_unused_materials", text="清理未使用材质及插槽", icon='X')
            
            # 材质替换功能
            material_replace_box = col_meterialoperation.box()
            material_replace_box.label(text="材质替换:", icon='MATERIAL')
            
            # 添加和清空按钮放在顶部
            row = material_replace_box.row(align=True)
            row.operator("object.add_source_material", text="添加源材质", icon='ADD')
            row.operator("object.clear_source_materials", text="清空列表", icon='TRASH')
            
            # 源材质列表
            material_replace_box.label(text="源材质列表:")
            for i, item in enumerate(context.scene.source_materials):
                row = material_replace_box.row(align=True)
                row.prop(item, "material", text="")
                row.operator("object.remove_source_material", text="", icon='X').index = i
            
            # 目标材质选择
            material_replace_box.prop(context.scene, "target_material", text="目标材质")
            
            # 执行替换按钮
            material_replace_box.operator("object.replace_material", text="执行材质替换", icon='MATERIAL')

# 命名操作
        col_renameoperation = layout.column()
        col_renameoperation.prop(scene, "renameoperation_expand", text="重命名与命名管理", emboss=False,
                                 icon='TRIA_DOWN' if context.scene.renameoperation_expand else 'TRIA_RIGHT')

        if context.scene.renameoperation_expand:
            # 车辆部件命名
            box_auto_rename_car = col_renameoperation.box()
            box_auto_rename_car.label(text="车辆部件自动重命名:", icon='AUTO')
            row = box_auto_rename_car.row(align=True)
            row.operator("object.miao_auto_rename_car", text="Unity车辆命名", icon='EVENT_U')
            row.operator("object.miao_auto_rename_car_for_rigcar", text="RigCar命名", icon='EVENT_R')

            # 层级与集合命名
            spatial_rename_box = col_renameoperation.box()
            spatial_rename_box.label(text="层级与集合命名:", icon='OUTLINER')
            row = spatial_rename_box.row(align=True)
            row.operator("object.miao_rename_by_parent", text="子级命名为顶级", icon='OUTLINER_OB_EMPTY')
            row.operator("object.rename_to_collection", text="命名为所处集合", icon='GROUP')

            # 后缀管理
            remove_suffix_box = col_renameoperation.box()
            remove_suffix_box.label(text="名称后缀管理:", icon='SORTALPHA')
            row = remove_suffix_box.row(align=True)
            row.operator("object.miao_remove_name_suffix", text="移除后缀", icon='X')
            row.operator("object.remove_suffix_and_resolve", text="移除后缀并解决重名", icon='DECORATE_KEYFRAME')
            
            # 数据命名同步
            naming_convention_box = col_renameoperation.box()
            naming_convention_box.label(text="数据命名同步:", icon='COMMUNITY')
            row = naming_convention_box.row(align=True)
            row.operator("object.rename_meshes", text="Mesh命名为物体", icon='OUTLINER_DATA_MESH')
            row.operator("object.rename_objects", text="物体命名为Mesh", icon='OBJECT_DATA')

            # 贴图改名
            texture_rename_box = col_renameoperation.box()
            texture_rename_box.label(text="贴图重命名:", icon='IMAGE_DATA')
            texture_rename_box.operator("object.rename_texture_orign", text="贴图改名为原始名称", icon='FILE_REFRESH')

            # 按位置重命名
            position_rename_box = col_renameoperation.box()
            position_rename_box.label(text="按位置重命名:", icon='SNAP_GRID')
            
            # 集合内位置重命名
            box_rename_by_collections = position_rename_box.box()
            box_rename_by_collections.label(text="集合内位置重命名:")
            box_rename_by_collections.prop(context.scene, "collectionA", text="集合 A")
            box_rename_by_collections.prop(context.scene, "collectionB", text="集合 B")
            box_rename_by_collections.operator("object.miao_rename_collections", text="按位置重命名集合", icon='COLLECTION_NEW')
            
            # 空间顺序重命名
            box_rename_by_location = position_rename_box.box()
            box_rename_by_location.label(text="空间顺序重命名:")
            row = box_rename_by_location.row(align=True)
            row.prop(context.scene, "rename_axis", text="轴向")
            row.prop(context.scene, "rename_order", text="排序类型")
            box_rename_by_location.operator("object.miao_rename_location", text="按空间顺序重命名", icon='SORTSIZE')

# 旋转缩放位移操作
        col_rsm = layout.column()
        col_rsm.prop(scene, "rsm_expand", text="变换工具", emboss=False,
                     icon='TRIA_DOWN' if context.scene.rsm_expand else 'TRIA_RIGHT')
        if context.scene.rsm_expand:
            # 下落至表面
            surface_box = col_rsm.box()
            surface_box.label(text="放置与对齐:", icon='SNAP_FACE')
            surface_box.operator("object.move_to_surface", text="下落至表面", icon='ORIENTATION_NORMAL')
            
            # 列队工具
            queue_up_box = col_rsm.box()
            queue_up_box.label(text="列队排列:", icon='OUTLINER_OB_POINTCLOUD')
            
            col = queue_up_box.column()
            row = col.row()
            row.prop(context.scene, "queue_up_distance", text="间距")
            row.prop(context.scene, "queue_up_axis", text="轴向")
            
            col.prop(context.scene, "use_bounding_box", text="使用包围盒")
            col.operator("object.miao_queue_up", text="执行列队排列", icon='MOD_ARRAY')
            
            # 随机放置工具
            random_box = col_rsm.box()
            random_box.label(text="随机变换:", icon='MOD_NOISE')
            
            # 随机位置
            random_placement_box = random_box.box()
            random_placement_box.label(text="随机位置:", icon='DRIVER_TRANSFORM')
            random_placement_box.prop(context.scene, "random_placement_extent", text="随机范围")
            random_placement_box.operator("object.miao_random_placement", text="随机分布位置", icon='STICKY_UVS_DISABLE')
            
            # 随机缩放
            random_scale_box = random_box.box()
            random_scale_box.label(text="随机缩放:", icon='FULLSCREEN_ENTER')
            col = random_scale_box.column(align=True)
            col.prop(context.scene, "random_scale_extent_x", text="X轴范围")
            col.prop(context.scene, "random_scale_extent_y", text="Y轴范围")
            col.prop(context.scene, "random_scale_extent_z", text="Z轴范围")
            random_scale_box.operator("object.miao_random_scale", text="应用随机缩放", icon='ARROW_LEFTRIGHT')
            
            # 对齐集合顶级父级
            align_parent_box = col_rsm.box()
            align_parent_box.label(text="集合对齐:", icon='CON_TRACKTO')
            col = align_parent_box.column()
            col.prop(context.scene, "collectionA", text="参考集合", icon='COLLECTION_COLOR_01')
            col.prop(context.scene, "collectionB", text="目标集合", icon='COLLECTION_COLOR_02')
            align_parent_box.operator("object.align_operator", text="批量对齐顶级父物体", icon='SNAP_ON')

# 灯光工具
        col_light_tools = layout.column()
        col_light_tools.prop(scene, "light_tools_expand", text="灯光工具", emboss=False,
                          icon='TRIA_DOWN' if context.scene.light_tools_expand else 'TRIA_RIGHT')
        
        if scene.light_tools_expand:
            # 灯光关联工具
            light_tools_box = col_light_tools.box()
            light_tools_box.label(text="灯光关联工具:", icon='LIGHT')
            
            # 容差设置
            light_tools_box.prop(context.scene, "light_linking_tolerance", text="相似度容差")
            
            # 关联灯光按钮
            op = light_tools_box.operator("object.link_similar_lights", text="关联相似灯光", icon='LINKED')
            op.tolerance = context.scene.light_linking_tolerance

# 动画处理工具
        col_animation = layout.column()
        col_animation.prop(scene, "animation_tools_expand", text="动画处理工具", emboss=False,
                          icon='TRIA_DOWN' if context.scene.animation_tools_expand else 'TRIA_RIGHT')
        
        if scene.animation_tools_expand:
            # 角色部件替换工具
            role_replace_box = col_animation.box()
            role_replace_box.label(text="角色部件替换:", icon='OUTLINER_OB_ARMATURE')
            role_replace_box.prop(context.scene, "collectionA", text="源集合", icon='COLLECTION_COLOR_01')
            role_replace_box.prop(context.scene, "collectionB", text="目标集合", icon='COLLECTION_COLOR_04')
            
            # 添加四个按钮
            col = role_replace_box.column(align=True)
            col.label(text="替换集合内物体:")
            row = col.row(align=True)
            row.operator("object.miao_role_replacer", text="随机替换", icon='ARMATURE_DATA')
            row.operator("object.miao_role_replacer_parent", text="基于父级关系", icon='CONSTRAINT')
            
            col.label(text="替换所选物体:")
            row = col.row(align=True)
            row.operator("object.miao_role_replacer_selected", text="随机替换", icon='OBJECT_DATA')
            row.operator("object.miao_role_replacer_selected_parent", text="基于父级关系", icon='CONSTRAINT')

            # 动画清理工具
            animation_tools_box = col_animation.box()
            animation_tools_box.label(text="动画清理工具:", icon='ANIM_DATA')
            
            row1 = animation_tools_box.row(align=True)
            row1.operator("animation.clear_scale_animation", text="清除缩放动画", icon='FULLSCREEN_ENTER')
            row1.operator("animation.clear_location_animation", text="清除位移动画", icon='ANCHOR_TOP')
            
            row2 = animation_tools_box.row(align=True)
            row2.operator("animation.clear_rotation_animation", text="清除旋转动画", icon='DRIVER_ROTATIONAL_DIFFERENCE')
            row2.operator("animation.clear_all_animation", text="清除所有动画", icon='CANCEL')
            
            # 动画修改器工具
            animation_modifier_box = col_animation.box()
            animation_modifier_box.label(text="动画修改器工具:", icon='MODIFIER')
            
            row1 = animation_modifier_box.row(align=True)
            row1.operator("animation.paste_modifiers", text="添加循环修改器(带偏移)", icon='PASTEDOWN')
            row1.operator("animation.add_cycle_modifier_no_offset", text="添加循环修改器(无偏移)", icon='PASTEDOWN')
            
            row2 = animation_modifier_box.row(align=True)
            row2.operator("animation.remove_all_modifiers", text="移除所有修改器", icon='X')
            
            # 骨架操作工具
            armature_tools_box = col_animation.box()
            armature_tools_box.label(text="骨架操作工具（测试）:", icon='ARMATURE_DATA')
            
            # 添加骨架位置设置工具
            armature_position_box = armature_tools_box.box()
            armature_position_box.label(text="骨架位置设置:", icon='ARMATURE_DATA')
            row = armature_position_box.row(align=True)
            row.operator("armature.set_to_rest_position", text="设置为静置位置", icon='ARMATURE_DATA')
            row.operator("armature.set_to_pose_position", text="设置为姿态位置", icon='POSE_HLT')
            
            # 添加空物体转骨骼工具
            empty_to_bone_box = armature_tools_box.box()
            empty_to_bone_box.label(text="空物体转骨骼:", icon='EMPTY_DATA')
            empty_to_bone_box.operator("object.convert_empties_to_bones", text="转换空物体为骨骼", icon='ARMATURE_DATA')
            
            # 添加骨骼参数复制面板
            bone_params_box = armature_tools_box.box()
            bone_params_box.label(text="骨骼参数复制:", icon='ARMATURE_DATA')
            
            # 源骨架和目标骨架选择
            bone_params_box.prop(context.scene, "source_armature", text="源骨架")
            bone_params_box.prop(context.scene, "target_armature", text="目标骨架")
            
            # 执行按钮
            bone_params_box.operator("object.copy_bone_parameters", text="复制骨骼参数", icon='ARMATURE_DATA')
            


# 导入导出操作
        col_inout = layout.column()
        col_inout.prop(scene, "inout_expand", text="导入导出工具", emboss=False,
                       icon='TRIA_DOWN' if context.scene.inout_expand else 'TRIA_RIGHT')

        if context.scene.inout_expand:
            # 批量导入
            import_box = col_inout.box()
            import_box.label(text="批量导入:", icon='IMPORT')
            import_box.operator("miao.batch_import_fbx", text="批量导入FBX", icon='FILE_3D')
            import_box.operator("miao.batch_import_obj", text="批量导入OBJ", icon='FILE_3D')
            
            # Better FBX导入
            better_fbx_box = import_box.box()
            better_fbx_box.label(text="Better FBX导入:", icon='ARMATURE_DATA')
            better_fbx_box.prop(context.scene, "better_fbx_import_directory", text="FBX目录", icon='FILE_FOLDER')
            
            row = better_fbx_box.row(align=True)
            row.operator("better_fbx.batch_import", text="批量导入", icon='IMPORT')
            row.operator("better_fbx.batch_import_files", text="选择多个FBX文件", icon='DOCUMENTS')
            
            # 批量导出
            export_box = col_inout.box()
            export_box.label(text="批量导出:", icon='EXPORT')
            export_box.prop(context.scene, "export_directory", text="导出目录", icon='FILE_FOLDER')
            
            # 添加导出配置选项
            export_config_box = export_box.box()
            export_config_box.label(text="导出配置:", icon='SETTINGS')
            export_config_box.prop(context.scene, "export_config", text="")
            export_config_box.prop(context.scene, "clear_parent_on_export", text="清除父级关系", icon='UNLINKED')
            
            col = export_box.column(align=True)
            col.operator("scene.export_fbx_by_parent", text="按顶级父物体导出FBX", icon='OUTLINER_OB_EMPTY')
            col.operator("scene.export_fbx_by_col_mark", text="按.col标记导出FBX", icon='BOOKMARKS')
            col.operator("object.miao_output_fbx_as_collection", text="按集合分文件夹导出FBX", icon='OUTLINER_COLLECTION')
            col.operator("object.export_objs", text="批量导出OBJ", icon='EXPORT')
            
            # 批量关联场景
            link_scenes_batch_box = col_inout.box()
            link_scenes_batch_box.label(text="场景关联与排序:", icon='SCENE_DATA')
            link_scenes_batch_box.prop(context.scene, "export_directory", text=".Blender文件目录", icon='BLENDER')
            
            col = link_scenes_batch_box.column(align=True)
            col.operator("scene.link_scenes_batch", text="从.blend文件关联场景", icon='LINK_BLEND')
            col.operator("scene.sort_scenes", text="按名称排序场景", icon='SORTALPHA')
            col.operator("scene.add_sorted_scenes_to_sequencer", text="批量添加场景至时间轴", icon='SEQ_SEQUENCER')

# 资产操作
        col_assestoperation = layout.column()
        col_assestoperation.prop(scene, "assestoperation_expand", text="资产转换工具", emboss=False,
                                 icon='TRIA_DOWN' if context.scene.assestoperation_expand else 'TRIA_RIGHT')
        if context.scene.assestoperation_expand:
            # VOX处理
            box_vox = col_assestoperation.box()
            box_vox.label(text="VOX模型处理:", icon='MESH_GRID')
            box_vox.operator("object.vox_operation", text="导入VOX一键处理", icon='IMPORT')

            # 批量处理步骤
            box_assestoperation = col_assestoperation.box()
            box_assestoperation.label(text="模型预处理流程:", icon='PRESET_NEW')
            col = box_assestoperation.column(align=True)
            col.operator("object.miao_apply_and_separate", text="1.独立化应用所有变换", icon='OBJECT_DATA')
            col.operator("object.miao_merge_top_level", text="2.按顶级层级合并", icon='OUTLINER_OB_GROUP_INSTANCE')
            col.operator("object.miao_reset_normals", text="3.重置所选矢量", icon='NORMALS_VERTEX')
            col.operator("object.miao_clean_empty", text="4.清理所选空物体", icon='OUTLINER_OB_EMPTY')
            col.operator("object.miao_clean_sense", text="5.递归清理场景", icon='PARTICLEMODE')

            # 批量标记资产
            assembly_asset_box = col_assestoperation.box()
            assembly_asset_box.label(text="批量标记资产:", icon='ASSET_MANAGER')
            assembly_asset_box.prop(context.scene, "asset_collection", text="目标集合", icon='COLLECTION_COLOR_04')
            assembly_asset_box.prop(context.scene, "create_top_level_parent", text="创建顶级父级")
            assembly_asset_box.operator("object.miao_create_assembly_asset", text="创建装配资产", icon='CHECKMARK')

            # Voxelizer设置
            box_voxelizer = col_assestoperation.box()
            box_voxelizer.label(text="Voxelizer工具:", icon='CUBE')
            box_voxelizer.prop(context.scene.voxelizer_tool, "path", text="模型路径", icon='FILE_3D')
            box_voxelizer.prop(context.scene.voxelizer_tool, "voxelizer_path", text="Voxelizer路径", icon='TOOL_SETTINGS')
            
            row = box_voxelizer.row(align=True)
            row.operator("object.convert_voxelizer", text="转换为VOX", icon='MESH_CUBE')
            row.operator("object.convert_voxelizer_color", text="转换为VOX(带颜色)", icon='COLOR')

            # 体素转换
            convert_box = col_assestoperation.box()
            convert_box.label(text="体素化设置:", icon='LIGHTPROBE_GRID')
            convert_box.operator("object.voxel_converter", text="生成体素化指令", icon='CONSOLE')
            convert_box.prop(scene, "resolution_factor", text="分辨率因子")

#批量渲染
        col_autorender = layout.column()
        col_autorender.prop(scene, "autorender_expand", text="渲染工具", emboss=False, 
                            icon='TRIA_DOWN' if scene.autorender_expand else 'TRIA_RIGHT')

        if scene.autorender_expand:
            # 快速处理显示效果
            quick_render_box = col_autorender.box()
            quick_render_box.label(text="快速处理:", icon='SHADING_RENDERED')
            quick_render_box.operator("auto_render.oneclick", 
                                   text="优化模型显示效果", 
                                   icon='SHADERFX')
            
            # 批量渲染设置
            box_autorender = col_autorender.box()
            box_autorender.label(text="批量渲染设置:", icon='RENDER_STILL')
            
            # 输出设置
            output_col = box_autorender.column()
            output_col.label(text="输出设置:", icon='OUTPUT')
            output_row = output_col.row()
            output_row.prop(bpy.context.scene.auto_render_settings, "output_path", text="路径", icon='FILE_FOLDER')
            output_row.prop(bpy.context.scene.auto_render_settings, "output_name", text="名称", icon='FILE_BLANK')
            output_col.prop(bpy.context.scene.auto_render_settings, "output_format", text="格式", icon='FILE_IMAGE')
            
            # 渲染对象
            render_col = box_autorender.column()
            render_col.label(text="渲染对象:", icon='SCENE')
            render_col.prop(bpy.context.scene.auto_render_settings, "collections", text="集合", icon='OUTLINER_COLLECTION')
            render_col.prop(bpy.context.scene.auto_render_settings, "cameras", text="相机", icon='CAMERA_DATA')
            
            # 相机设置
            camera_col = box_autorender.column()
            camera_col.label(text="相机设置:", icon='VIEW_CAMERA')
            camera_col.prop(bpy.context.scene.auto_render_settings, "focus_each_object", text="聚焦到每个物体（正交相机）")
            camera_col.prop(bpy.context.scene.auto_render_settings, "focus_only_faces", text="仅聚焦有面的物体")
            camera_col.prop(bpy.context.scene.auto_render_settings, "margin_distance", text="边框距离")
            
            # 执行按钮
            box_autorender.operator("auto_render.execute", text="执行渲染", icon='RENDER_STILL')

# 批量调整渲染设置
        col_renderadj = layout.column()
        col_renderadj.prop(scene, "renderadj_expand", text="渲染设置批量调整", emboss=False,
                           icon='TRIA_DOWN' if context.scene.renderadj_expand else 'TRIA_RIGHT')

        if context.scene.renderadj_expand:
            box_renderadj = col_renderadj.box()
            box_renderadj.label(text="批量调整渲染设置:", icon='PREFERENCES')
            
            change_resolution_prop = context.scene.change_resolution_prop
            
            # 文件路径设置
            path_col = box_renderadj.column()
            path_col.label(text="文件路径:", icon='FILE_FOLDER')
            path_col.prop(change_resolution_prop, "input_dir", text="输入目录")
            path_col.prop(change_resolution_prop, "output_dir", text="输出目录")
            path_col.prop(change_resolution_prop, "output_file", text="渲染输出路径")
            
            # 渲染设置
            render_settings_col = box_renderadj.column()
            render_settings_col.label(text="渲染设置:", icon='SCENE')
            
            row = render_settings_col.row(align=True)
            row.prop(change_resolution_prop, "render_engine", text="引擎")
            row.prop(change_resolution_prop, "output_format", text="格式")
            
            # 分辨率设置
            res_col = box_renderadj.column()
            res_col.label(text="分辨率设置:", icon='FULLSCREEN_ENTER')
            
            row1 = res_col.row(align=True)
            row1.prop(change_resolution_prop, "output_resolution_x", text="宽度")
            row1.prop(change_resolution_prop, "output_resolution_y", text="高度")
            
            row2 = res_col.row(align=True)
            row2.prop(change_resolution_prop, "resolution_percentage", text="质量百分比")
            row2.prop(change_resolution_prop, "output_frame_rate", text="帧率")
            
            # 执行按钮
            operator_instance = box_renderadj.operator(BATCH_RESOLUTION_OT_ExecuteButton.bl_idname, text="执行批量设置", icon='PLAY')

            # 传递参数
            operator_instance.output_file = change_resolution_prop.output_file
            operator_instance.render_engine = change_resolution_prop.render_engine
            operator_instance.output_format = change_resolution_prop.output_format
            operator_instance.input_dir = change_resolution_prop.input_dir
            operator_instance.output_dir = change_resolution_prop.output_dir
            operator_instance.output_resolution_x = str(change_resolution_prop.output_resolution_x)
            operator_instance.output_resolution_y = str(change_resolution_prop.output_resolution_y)
            operator_instance.resolution_percentage = str(change_resolution_prop.resolution_percentage)
            operator_instance.output_frame_rate = str(change_resolution_prop.output_frame_rate)

            
class AddSourceMaterialOperator(bpy.types.Operator):
    bl_idname = "object.add_source_material"
    bl_label = "添加源材质"
    bl_description = "添加材质到源材质列表"
    
    def execute(self, context):
        # 直接添加一个空的材质槽
        new_item = context.scene.source_materials.add()
        new_item.material = None
        return {'FINISHED'}

class RemoveSourceMaterialOperator(bpy.types.Operator):
    bl_idname = "object.remove_source_material"
    bl_label = "移除源材质"
    bl_description = "从源材质列表移除材质"
    
    index: bpy.props.IntProperty(
        name="索引",
        default=0
    ) # type: ignore
    
    def execute(self, context):
        if 0 <= self.index < len(context.scene.source_materials):
            context.scene.source_materials.remove(self.index)
            return {'FINISHED'}
        return {'CANCELLED'}

class ClearSourceMaterialsOperator(bpy.types.Operator):
    bl_idname = "object.clear_source_materials"
    bl_label = "清空源材质列表"
    bl_description = "清空源材质列表"
    
    def execute(self, context):
        context.scene.source_materials.clear()
        return {'FINISHED'}

class ReplaceMaterialOperator(bpy.types.Operator):
    bl_idname = "object.replace_material"
    bl_label = "执行材质替换"
    bl_description = "将选中的源材质替换为目标材质"
    
    def execute(self, context):
        # 检查是否有目标材质
        if not context.scene.target_material:
            self.report({'ERROR'}, "请选择目标材质")
            return {'CANCELLED'}
            
        # 获取所有非空的源材质
        source_materials = [item.material for item in context.scene.source_materials if item.material is not None]
        if not source_materials:
            self.report({'WARNING'}, "没有有效的源材质")
            return {'CANCELLED'}
            
        # 移除重复的源材质
        source_materials = list(set(source_materials))
        
        # 统计替换结果
        replaced_count = 0
        affected_objects = set()
        
        # 遍历所有选中的物体
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                # 遍历物体的所有材质槽
                for slot in obj.material_slots:
                    if slot.material in source_materials:
                        slot.material = context.scene.target_material
                        replaced_count += 1
                        affected_objects.add(obj.name)
        
        # 显示结果
        if replaced_count > 0:
            self.report({'INFO'}, f"已替换 {replaced_count} 个材质，影响 {len(affected_objects)} 个物体")
        else:
            self.report({'WARNING'}, "没有找到需要替换的材质")
            
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MaterialPropertyGroup)
    bpy.utils.register_class(CustomFunctionsPanel)
    bpy.utils.register_class(AddSourceMaterialOperator)
    bpy.utils.register_class(RemoveSourceMaterialOperator)
    bpy.utils.register_class(ClearSourceMaterialsOperator)
    bpy.utils.register_class(ReplaceMaterialOperator)
    
    # 注册场景属性
    bpy.types.Scene.source_materials = CollectionProperty(type=MaterialPropertyGroup)
    bpy.types.Scene.target_material = PointerProperty(
        type=bpy.types.Material,
        name="目标材质"
    )
    
    bpy.types.Scene.tools_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.BindOperation_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.meterialoperation_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.renameoperation_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.rsm_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.anm_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.inout_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.assestoperation_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.autorender_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.renderadj_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.light_tools_expand = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.animation_tools_expand = bpy.props.BoolProperty(default=False)

    
    # 灯光关联工具参数
    bpy.types.Scene.light_linking_tolerance = bpy.props.FloatProperty(
        name="相似度容差",
        description="判断灯光相似性的容差值",
        default=0.01,
        min=0.001,
        max=0.5,
        soft_min=0.005,
        soft_max=0.1,
        precision=3
    )

    # 源骨架属性
    bpy.types.Scene.source_armature = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="源骨架",
        description="选择带动画的源骨架",
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )

    # 目标骨架属性
    bpy.types.Scene.target_armature = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="目标骨架",
        description="选择要接收动画的目标骨架",
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )

    # 骨骼动画转移参数
    bpy.types.Scene.transfer_bone_animation_keyframe_sample_rate = bpy.props.IntProperty(
        name="关键帧采样率",
        description="每多少帧采样一次关键帧",
        default=1,
        min=1
    )

    bpy.types.Scene.transfer_bone_animation_batch_size = bpy.props.IntProperty(
        name="批处理帧数",
        description="每次处理多少帧",
        default=10,
        min=1
    )

    bpy.types.Scene.transfer_bone_animation_show_detailed_info = bpy.props.BoolProperty(
        name="显示详细信息",
        description="是否显示详细的处理信息",
        default=False
    )

def unregister():
    bpy.utils.unregister_class(CustomFunctionsPanel)
    bpy.utils.unregister_class(MaterialPropertyGroup)
    bpy.utils.unregister_class(AddSourceMaterialOperator)
    bpy.utils.unregister_class(RemoveSourceMaterialOperator)
    bpy.utils.unregister_class(ClearSourceMaterialsOperator)
    bpy.utils.unregister_class(ReplaceMaterialOperator)
    
    # 注销场景属性
    properties_to_remove = [
        # 基础属性
        "tools_expand",
        "BindOperation_expand",
        "meterialoperation_expand",
        "renameoperation_expand",
        "rsm_expand",
        "anm_expand",
        "inout_expand",
        "assestoperation_expand",
        "autorender_expand",
        "renderadj_expand",
        "light_tools_expand",
        "animation_tools_expand",
        
        # 材质相关属性
        "source_materials",
        "target_material",
        
        # 灯光关联工具参数
        "light_linking_tolerance",
        
        # 骨架相关属性
        "source_armature",
        "target_armature",
        
        # 骨骼动画转移参数
        "transfer_bone_animation_keyframe_sample_rate",
        "transfer_bone_animation_batch_size",
        "transfer_bone_animation_show_detailed_info"
    ]
    
    # 安全地删除所有属性
    for prop in properties_to_remove:
        try:
            delattr(bpy.types.Scene, prop)
        except AttributeError:
            pass  # 如果属性不存在，就跳过
