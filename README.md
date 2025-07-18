# MiaoTools

**🛠️ 概述**  
MiaoTools 是一个 Blender 插件，集合了多种便捷操作工具，以提升 Blender 的使用效率和工作流程。

## 基础工具集

- **模型编辑工具**

  **✂️ 概述**  
  提供基础的模型数据编辑功能，帮助快速处理模型数据和结构。

  **🔧 功能列表**
  | 功能 | 描述 | 适用场景 |
  |------|------|----------|
  | **移除顶点组** | 批量清除所选物体的顶点组数据 | 模型清理、优化导出模型 |
  | **移除修改器** | 批量移除所选物体上的修改器 | 模型简化、问题排查 |
  | **批量独立化物体** | 断开所选物体与其他物体的链接关系 | 准备导出、避免依赖问题 |
  | **矫正旋转** | 基于选择面重新定向物体的旋转轴 | 校正应用变换后的模型方向 |

  **💡 使用提示**
  - 矫正旋转时，先进入编辑模式选择一个正面作为参考
  - 独立化操作会断开数据链接，但保持变换信息

- **场景清理工具**

  **🧹 概述**  
  一系列专用于清理场景数据的工具，优化文件结构，解决常见数据问题。

  **🧰 核心功能**
  | 功能 | 作用 | 解决问题 |
  |------|------|----------|
  | **清空空集合** | 移除场景中没有内容的集合 | 整理场景层级 |
  | **清除无子集空物体** | 移除没有子对象的空物体 | 清理冗余结构 |
  | **批量清空动画** | 移除选中物体上的动画数据 | 静态导出准备 |
  | **清理无实体工具** | 清除没有顶点的mesh数据块 | 修复文件错误 |
  | **清理UV非法数据** | 移除损坏的UV映射数据 | 解决UV保存问题 |
  | **清理丢失图像** | 清除丢失源文件的图像数据块 | 修复纹理引用错误 |

  **⚠️ 注意事项**  
  无子集空物体清理需多次操作以递归处理深层级结构

- **对齐与原点工具**

  **📐 概述**  
  提供精确控制物体原点位置的工具，便于模型对齐和布局。

  **📍 功能说明**
  - **轴向投射**：将物体原点投射到选定轴方向
  - **边界投射**：将原点移动到物体在选定方向的最大值位置
  | **Z轴归零**：保持XY位置不变，将原点Z坐标设为0

  **🎯 适用场景**  
  模型摆放、物理模拟准备、动画设置

- **高级选择工具**

  **🔍 概述**  
  提供多种基于特定条件的选择工具，超越默认的选择功能。

  **👆 选择方式**
  | 工具 | 选择条件 | 控制参数 |
  |------|---------|----------|
  | **选取同UV物体** | UV重叠度 | UV贴图层、匹配阈值 |
  | **选取过大物体** | 尺寸上限 | 可调最小尺寸值 |
  | **选取过小物体** | 尺寸下限 | 可调最大尺寸值 |
  | **选取无贴图物体** | 材质状态 | 纹理类型筛选 |
  | **按名称列表筛选** | 名称匹配 | 保留列表中的物体，可选是否删除灯光 |

  ![image](https://github.com/user-attachments/assets/f053ad8e-ad96-4658-ba99-a004fbab09dd)

- **快速生成工具**

  **⚡ 概述**  
  一组用于快速生成辅助几何体和实现特殊转换的工具。

  **🔄 功能列表**
  | 功能 | 描述 | 用途 |
  |------|------|------|
  | **生成包围盒** | 创建物体的立方体边界框，添加"_box"后缀 | 碰撞体设置、空间参考 |
  | **生成凸包** | 创建包含物体的凸多边形，添加"_col"后缀 | 简化碰撞体、物理模拟 |
  | **安全合并** | 合并物体但保持集合结构不变 | 保留组织的模型合并 |
  | **转换实例化** | 将多个物体替换为基准物体的实例 | 优化场景、统一编辑 |
  | **合并同原点物体** | 将共享同一原点的物体合并为一个 | 简化模型结构、减少物体数量 |

  **🚀 工作流程**  
  选择目标物体 → 执行生成功能 → 自动创建并命名结果

## 角色绑定与骨骼工具

- **骨骼数据管理**

  **🦴 概述**  
  提供完整的骨骼数据导出、导入和还原功能，支持角色自动绑定工作流。

  **🔧 功能列表**
  - **导出骨骼数据**：将当前骨架的骨骼位置、层级关系和自定义属性保存为JSON
  - **还原骨骼数据**：从JSON文件重建骨架结构
  - **还原点位数据**：恢复场景中空物体的位置信息
  - **重置骨骼端点**：自动连接父子骨骼，优化骨架结构
  - **连接骨骼**：智能连接相邻骨骼，建立正确的层级关系

- **配置驱动的角色绑定**

  **⚙️ 概述**  
  基于JSON配置文件实现角色的自动绑定，支持批量处理和标准化流程。

  **📋 配置文件功能**
  - **骨架模板**：保存标准角色的骨骼结构和位置
  - **命名规则**：定义部件的重命名和分组规则
  - **绑定参数**：记录权重分配和变换设置
  - **刷新配置列表**：动态加载RigJson目录中的配置文件

  **🚀 一键绑定流程**
  1. 选择配置文件
  2. 自动识别和重命名角色部件
  3. 创建标准骨架结构
  4. 绑定网格到骨骼
  5. 应用权重和变换
  6. 设置材质和优化显示

- **角色预处理工具**

  **🔄 概述**  
  专门针对角色模型的预处理流程，为绑定做准备。

  **📝 处理步骤**
  - **独立化与分离**：断开数据链接，分离合并的部件
  - **法线重置**：修复法线方向，优化显示效果
  - **缩放调整**：标准化角色尺寸
  - **变换应用**：应用所有变换到几何体
  - **层级清理**：移除不必要的空物体和父级关系
  - **原点设置**：重新计算几何体中心

- **高级绑定功能**

  **🎯 概述**  
  提供专业级的角色绑定工具，满足复杂制作需求。

  **🛠️ 专业工具**
  - **空物体转骨骼**：将动画空物体转换为骨骼，保持动画数据
  - **骨骼参数复制**：在不同骨架间复制骨骼位置和参数
  - **智能部件合并**：基于命名规则自动合并相关部件
  - **权重自动分配**：根据部件名称自动设置顶点组权重

## 关联与绑定工具

- **碰撞检测与集合绑定**

  **🧩 概述**  
  基于物体碰撞关系自动组织场景结构，适用于快速整理复杂模型。

  **🔧 功能列表**
  - **检测碰撞归集合**：根据物体间的碰撞关系将物体分组至集合
  | **检测碰撞归子集**：将碰撞物体设置为父子关系
  | **检测并合并碰撞**：识别并合并相互接触的物体

- **集合父级设置**

  **📋 概述**  
  管理集合间的父子关系，通过界面指定集合间的层级结构。

  **🔄 功能说明**
  通过指定父级集合和子级集合，快速建立集合间的继承关系，方便场景组织和管理。

- **空物体父级绑定**

  **🔗 概述**  
  自动为物体创建空物体作为父级，能处理多个物体共享一个父级的情况。

  **⚙️ 功能选项**
  - **为多个物体创建共同父级**：所选物体将共享一个新创建的空物体作为父级
  - **创建空物体父级**：为选中物体创建新的空物体父级，并放置在物体底部中心

## 批量转换资产

## 材质工具

- **UV 操作**

  **🔧 概述**  
  提供UV贴图的调整和优化工具，解决常见UV问题。

  **📏 功能列表**
  - **UV尺寸校准**：基于32像素/米的标准比例调整UV
  - **UV旋转矫正**：修正UV旋转方向问题
  - **UV铺满展开**：自动将UV扩展到覆盖整个UV空间
  
  **💡 特点**
  - 基于32像素/米的标准比例调整
  - 自动计算并应用最佳UV缩放值
  - 保持纹理细节与物体实际尺寸的正确对应关系

- **材质强度调整**

  **🎛️ 概述**  
  批量调整所选物体的材质属性参数，快速统一场景中物体的材质表现。

  **⚙️ 可调整参数**
  | 参数 | 调整范围 | 用途 |
  |------|---------|------|
  | **发光度** | 0-10 | 控制材质的自发光强度 |
  | **粗糙度** | 0-10 | 调整材质的表面光滑/粗糙程度 |

  **🔄 操作方式**  
  选择物体 → 调整滑块参数 → 点击应用按钮

- **材质球节点操作**

  **🔌 概述**  
  提供多种常用的材质节点连接和设置操作，简化材质节点编辑流程。

  **🛠️ 功能列表**
  - **Alpha节点连接**：自动将图像的Alpha通道连接到着色器的Alpha输入
  - **断开Alpha连接**：快速移除Alpha通道连接
  - **Alpha设为肤色**：将指定材质的Alpha部分设置为自定义肤色
  - **设置临近采样**：将纹理设置为临近采样模式，实现硬边缘效果
  - **设置Alpha裁剪模式**：将材质设置为Alpha裁剪模式
  - **设置Alpha混合模式**：将材质设置为Alpha混合模式
  - **设置阴影不可见(渲染)**：将所选物体的阴影在视图和最终渲染中均设置为不可见，适用于透明物体或不需要产生阴影的装饰元素
  - **设置阴影可见(渲染)**：将所选物体的阴影在视图和最终渲染中均设置为可见，恢复默认的阴影投射行为
  - **设置Alpha通道打包**：将所选物体的所有贴图设置为Alpha通道打包模式，适用于需要优化透明贴图性能的场景

- **贴图自动链接**

  **🖼️ 概述**  
  根据物体或材质名称自动匹配并应用纹理，简化贴图工作流程。

  **📂 匹配方法**
  - **按物体名称匹配(完整)**：精确匹配物体名称与贴图名称
  - **按物体名称匹配(忽略字段)**：匹配时忽略指定字段
  - **按材质名称匹配**：根据材质名称查找匹配贴图
  - **按顶级父级名称匹配**：使用顶级父级物体名称查找贴图

- **材质管理**

  **🎨 概述**  
  处理和整理场景中的材质，优化材质结构，减少重复数据。

  **🧰 功能列表**
  - **材质球排序**：对材质按名称或其他属性进行排序
  - **随机材质**：为物体随机分配材质，增加场景变化
  - **清理材质**：移除未使用的材质数据
  - **清理空材质槽**：删除物体上没有实际材质的材质槽
  - **合并重复材质(.00x后缀)**：合并具有数字后缀的重复材质
  - **合并后缀同名材质球**：合并名称相似但带有不同后缀的材质

## 重命名工具

- **车辆部件命名工具**

  **🚗 概述**  
  针对车辆模型的专用命名工具，自动识别并命名车轮等关键部件，适用于不同引擎和插件。

  **🛠️ 功能选项**
  - **Unity车辆命名**：识别并按Unity规范命名车轮（需将车辆-Y轴朝前放置）
  - **RigCar命名**：识别并按Rigcar插件规范命名车轮（需将车辆-Y轴朝前放置）

  **🎯 使用场景**  
  车辆模型准备、物理骨骼设置、动画绑定前期准备

- **层级与集合命名**

  **📂 概述**  
  基于物体在场景中的父子关系或集合归属进行批量命名，保持场景组织结构的一致性。

  **🔄 功能选项**
  | 功能 | 描述 | 应用场景 |
  |------|------|----------|
  | **子级命名为顶级** | 将物体命名为其顶级父级名称并添加序号 | 角色部件、组装模型 |
  | **命名为所处集合** | 将物体命名为其所在集合的名称 | 场景整理、批量资产管理 |
  | **集合内位置重命名** | 根据物体在集合中的相对位置命名 | 有序物体组、流程化资产 |

  **⚡ 工作方式**  
  自动分析层级关系 → 应用命名规则 → 处理重名冲突

- **名称后缀管理**

  **🏷️ 概述**  
  处理物体名称中的后缀标识，解决重名问题并保持命名整洁。

  **✂️ 功能列表**
  - **移除后缀**：清除物体名称中的序号后缀（如.001、.002等）
  - **移除顶级后缀并解决重名**：清除顶级父级名称后缀并自动解决子物体重名

  **💼 适用场景**  
  多次导入后的模型整理、导出前的名称标准化

- **Mesh数据命名**

  **🔍 概述**  
  同步物体与其网格数据的命名，确保内部数据结构与外部物体命名一致。

  **🔄 双向命名**
  - **Mesh命名为物体**：将网格数据块重命名为其所属物体的名称
  - **物体命名为Mesh**：将物体重命名为其包含的网格数据名称

  **📊 位置命名**
  - **空间顺序重命名**：根据物体在3D空间中的排列顺序进行命名并添加序号

- **贴图重命名**

  **🖼️ 概述**  
  将贴图数据块重命名为其原始文件名，保持命名一致性。

  **🔄 功能说明**
  自动识别贴图的原始文件名并应用为贴图数据块名称，提高文件组织的清晰度。

- **按位置重命名**

  **📏 概述**  
  根据物体在3D空间中的排列顺序或相对位置进行有序命名。

  **🧮 命名选项**
  - **集合内位置重命名**：根据物体在指定集合内的相对位置重命名
  - **空间顺序重命名**：按照物体在选定轴向上的排序位置命名并编号

## 变换工具

- **放置与对齐**

  **📌 概述**  
  提供物体精确放置和对齐功能，便于场景排布和模型组装。

  **🛠️ 功能列表**
  - **下落至表面**：将所选物体沿Y轴下降直至与目标表面接触
  - **批量对齐顶级父物体**：将一个集合中的物体对齐到另一个集合中同名物体上

- **列队排列工具**

  **📐 概述**  
  提供物体的有序排列功能，可自定义间距和方向。

  **⚙️ 参数设置**
  - **间距**：物体之间的距离
  - **轴向**：排列的方向轴
  | **使用包围盒**：是否使用物体的边界盒计算间距

- **随机变换工具**

  **🎲 概述**  
  为物体添加随机位置和缩放变化，创建自然多样的场景效果。

  **🔄 功能列表**
  - **随机分布位置**：在指定范围内随机分布所选物体
  - **随机缩放**：对所选物体应用随机缩放值，可分别设置X/Y/Z轴的范围

## 灯光工具

- **灯光关联工具**

  **💡 概述**  
  用于处理场景中多个灯光的关联和组织。

  **🔧 功能说明**
  基于灯光属性的相似度，将相似灯光相互关联，减少重复设置和编辑工作。
  可通过相似度容差参数调整匹配精度。

## 渲染工具

- **快速处理显示效果**

  **🖌️ 概述**  
  一键优化模型的显示效果，适用于快速预览和展示。

  **🎯 使用场景**  
  模型展示、截图预览、演示准备

- **批量对象渲染**

  **🖼️ 概述**  
  自动渲染场景中多个物体，生成独立图像文件，适用于产品展示、资产预览生成等场景。

  **⚙️ 主要参数**
  | 参数 | 描述 | 用途 |
  |------|------|------|
  | **输出路径** | 渲染图像的保存目录 | 指定渲染结果存储位置 |
  | **输出名称** | 图像文件名前缀 | 区分不同批次渲染结果 |
  | **输出格式** | 图像文件格式 | 根据需要选择适合的格式 |
  | **渲染集合** | 要渲染的物体集合 | 限定渲染范围 |
  | **相机选择** | 使用的摄像机 | 控制渲染视角 |

  **🔍 智能聚焦功能**
  - **自动聚焦**：渲染时自动调整视图，使物体填满画面（正交模式下有效）
  - **边框距离**：控制物体与视口边缘的距离，避免裁切
  
  **🚀 工作流程**  
  选择参数 → 执行渲染 → 按顶级父级分组处理 → 自动保存结果

- **批量文件渲染**

  **📊 概述**  
  批量渲染多个.blend文件，支持静态图像和动画序列输出。

  **🔄 功能选项**
  - **渲染为动画**：将文件渲染为动画序列而非单帧图像
  - **批量处理**：自动依次处理指定目录中的所有Blender文件

- **批量文件渲染设置**

  **🔧 概述**  
  批量修改多个Blender文件的渲染设置，确保渲染参数的一致性，提高工作流效率。

  **⚙️ 可调整参数**
  ```
  ┌─────────────┬────────────────────────────────┐
  │ 基本设置    │ 渲染设置                       │
  ├─────────────┼────────────────────────────────┤
  │ 源文件路径  │ 渲染引擎 (Cycles/Eevee)        │
  │ 输出文件路径│ 输出格式                       │
  │             │ 渲染目标路径                   │
  │             │ 分辨率和百分比                 │
  │             │ 帧率                           │
  └─────────────┴────────────────────────────────┘
  ```

  **📋 操作流程**
  1. 选择包含.blend文件的目录
  2. 设置输出目录保存修改后的文件
  3. 配置所需的渲染参数
  4. 执行批量处理
  5. 系统自动处理所有文件并保存

  **💼 适用场景**  
  多文件渲染项目、团队协作标准化、批量渲染设置更新

## 资产转换工具

- **VOX模型处理**

  **🧊 概述**  
  针对体素模型(VOX格式)的导入和处理工具，简化体素模型的编辑流程。

  **🛠️ 功能说明**
  一键处理导入的VOX模型，自动优化结构和设置，使其易于在Blender中编辑。

- **模型预处理流程**

  **📋 概述**  
  提供完整的模型预处理工作流，为导出和使用做准备。

  **🔄 流程步骤**
  1. **独立化应用所有变换**：应用物体的所有变换并断开数据链接
  2. **按顶级层级合并**：将物体根据顶级父物体结构合并
  3. **重置所选矢量**：重新计算法线方向，修复出现的问题
  4. **清理所选空物体**：移除不需要的空物体，简化场景结构
  5. **递归清理场景**：深度清理场景中的问题数据

- **批量标记资产**

  **🏷️ 概述**  
  将物体批量标记为Blender资产，方便在资产浏览器中管理和使用。

  **⚙️ 选项**
  - **目标集合**：指定要处理的集合
  - **创建顶级父级**：为标记的资产创建顶级父物体，便于组织管理

- **Voxelizer工具**

  **📦 概述**  
  使用外部Voxelizer工具将3D模型转换为体素模型(VOX格式)。

  **🔄 转换选项**
  - **转换为VOX**：将模型转换为基本体素模型
  - **转换为VOX(带颜色)**：保留原始模型颜色信息的体素转换

- **体素化设置**

  **⚙️ 概述**  
  控制体素化转换的参数和设置，影响最终体素模型的精度和外观。

  **🔧 参数说明**
  - **分辨率因子**：控制体素化的精细程度，数值越高体素越精细

## 导入导出工具

- **批量导入**

  **📥 概述**  
  快速导入多个3D文件，支持常见的3D格式。

  **🔧 功能列表**
  - **批量导入FBX**：一次性导入目录中的所有FBX文件
  - **批量导入OBJ**：一次性导入目录中的所有OBJ文件

- **智能导出系统**

  **📤 概述**  
  提供多种导出模式和配置预设，针对不同目标软件优化FBX导出参数。

  **⚙️ 导出配置预设**
  | 配置 | 目标软件 | 轴向设置 | 单位 | 旋转处理 | 特点 |
  |------|---------|---------|------|----------|------|
  | **Unity默认(CM)** | Unity引擎 | Forward: -Z, Up: Y | 厘米 | 自动应用90°旋转 | 标准游戏引擎配置 |
  | **3ds Max默认配置(M)** | 3ds Max | Forward: Y, Up: Z | 米 | 保持原始旋转 | CAD/建模软件兼容 |

  **🎛️ 导出选项**
  - **导出配置选择**：在界面中选择预设配置
  - **清除父级关系**：导出时移除顶级空物体，保持子物体变换
  - **智能缩放**：根据配置自动应用单位转换和缩放

- **多模式导出**

  **🔄 概述**  
  提供多种导出模式，满足不同的工作流需求。

  **📋 导出模式**
  | 模式 | 描述 | 适用场景 | 特点 |
  |------|------|----------|------|
  | **按顶级父物体导出** | 以顶级父物体为单位，每个导出一个FBX | 角色、道具资产导出 | 保持完整层级结构 |
  | **按部件导出** | 每个Mesh单独导出，包含骨架 | 角色换装系统、模块化资产 | 精细化部件管理 |
  | **导出角色(完整)** | 导出完整角色（3ds Max配置） | 外部软件渲染、动画制作 | 保持所有细节 |
  | **导出角色(无父级)** | 清除空父级后导出 | 简化结构、减少层级 | 一键简化导出 |
  | **按.col标记导出** | 导出包含碰撞标记的物体及其父级链 | 游戏碰撞体导出 | 自动识别碰撞物体 |
  | **按集合分文件夹导出** | 每个集合导出到独立文件夹 | 场景资产分类导出 | 自动组织文件结构 |

  **⚡ 一键导出功能**
  - **导出角色(无父级)**：直接使用3ds Max配置，清除父级关系后导出
  - **智能旋转处理**：多物体时围绕父级整体旋转，而非单独旋转
  - **批量处理**：自动处理所有顶级父物体，显示进度信息

- **导出优化特性**

  **🚀 概述**  
  内置多项优化功能，提升导出效率和质量。

  **🔧 优化功能**
  - **批量处理**：大量物体时分批处理，避免内存溢出
  - **性能监控**：显示处理进度和耗时统计
  - **智能缩放**：根据目标软件自动应用正确的单位缩放
  - **变换保持**：导出后自动恢复物体原始变换状态
  - **错误处理**：自动检查路径有效性，提供错误提示

- **批量导出OBJ**

  **📦 概述**  
  将选中的物体批量导出为OBJ格式文件。

  **🛠️ 功能说明**
  每个选中物体导出为独立的OBJ文件，适用于静态模型和3D打印准备。



## 附加信息

- **插件更新**

  **🔄 在线更新功能**  
  插件提供自动更新功能，在Blender偏好设置中可以找到更新按钮。
  
  ⚠️ **重要提示**：更新过程会覆盖所有文件，包括角色配置的JSON文件，请在更新前单独备份这些文件！

- **依赖包管理**

  **📦 依赖项**  
  插件依赖Pillow包处理图像（主要用于渲染后处理、边距调整等）。
  
  **⚙️ 安装方式**
  - **自动安装**：插件激活时会自动安装根目录package文件夹中的依赖包
  - **手动安装**：可使用Blender内置Python执行安装命令
    ```
    cd [Blender安装目录]/python
    python -m pip install pillow
    ```
  
  **🖥️ 跨平台支持**  
  在非Windows平台使用时，需要下载对应平台的.tar.gz或.whl文件放入package文件夹

  当前依赖库文件仅支持Windows（PIL）

- **游戏资产准备**

  **💼 适用场景**  
  游戏资产准备、跨软件工作流、批量资产导出

- **场景关联与排序**

  **🔄 概述**  
  用于处理多个Blender文件中场景的关联、排序和编辑。

  **🛠️ 功能列表**
  - **从.blend文件关联场景**：批量从其他Blender文件中链接场景到当前文件
  - **按名称排序场景**：对文件中的场景按名称进行排序
  - **批量添加场景至时间轴**：将排序后的场景批量添加到视频序列编辑器中

  **💼 适用场景**  
  场景重构、多版本物体对齐、地面物体摆放



