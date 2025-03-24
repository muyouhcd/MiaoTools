# MiaoTools

MiaoTools 是一个 Blender 插件，集合了多种便捷操作工具，以提升 Blender 的操作效率。

## 工具集
![image](https://github.com/user-attachments/assets/d788bd3b-4d44-41b4-bf25-90861a112efb)

### 编辑工具

- **移除顶点组**: 移除所选物体的顶点组（可批量）。
- **移除修改器**: 移除所选物体的修改器（可批量）。
- **批量独立化物体**: 将所选物体与其他物体断开关系，实现独立化操作（可批量）。
- **矫正旋转**: 
  - 在编辑模式下选择物体的一个较正的面作为参考面，对整个物体的旋转轴向进行矫正。
  - 特别适用于已应用过变换的物体，如建筑模型。

### 清理工具

- **清空空集合**: 清理场景中空的集合。
- **清除无子集空物体**: 清理场景中没有子集的空物体，需要递归则需手动多次操作。
- **批量清空动画**: 对所选物体进行动画清除操作。
- **清理无实体工具**: 清理场景中没有顶点的 mesh 块。
- **清理 UV 非法数据**: 清除 UV 非法数据，解决 UV 无法保存的问题。
- **清理丢失图像**: 清理场景中丢失的图像纹理数据块，解决保存时纹理找不到的错误。

### 动画工具

- **暂无功能**: 仅预留面板。

### 生成工具

- **生成包围盒**: 对所选物体生成包围盒（立方体形状），名称与源物体相同并加上 "_box" 后缀。
- **生成凸包**: 对所选物体生成凸包，名称与原物体相同并加上 "_col" 后缀。
- **安全合并**
- **转换实例化**: 以最后选择的物体作为实例化基准，将其他物体替换为该物体（保持变换），实现实例化。

## 导入导出

- **导出操作**: 设定导出路径后，点击按顶级父级导出按钮，将场景中所有物体进行旋转缩放调整后导出，以适应 Unity 中的变换。以所有物体的顶级父级为一个 FBX 文件进行导出。
## 材质工具
- **UV**
实现uv尺寸校准（根据模型尺寸以及纹理尺寸进行调整uv缩放，该纹理应遵循32像素为一米的逻辑）
- **材质强度**
可以批量设置所选物体的材质强度，比如发光度和粗糙度，范围为0-10
- **材质球**
alpha通道自动链接到着色器的alpha
断开alpha的连接
alpha设置为肤色，将指定材质的alpha部分设置为指定颜色
- **贴图自动连接**
指定路径下进行查找贴图，自动连接到同名称物体上
可以对指定字段进行忽略，逗号分割
根据物体名称进行匹配贴图
根据材质球名称进行匹配贴图


- **材质管理**
对材质球插槽进行名称排序
所选物体设置随机颜色材质
清理未使用材质
清理空的材质槽
移除重复名称材质（自动添加.001这种）并将原始材质重新指定到材质插槽，该功能适用于多次导入的材质合并


## 重命名工具

- **UnityCar 自动重命名**: 自动识别并重命名四轮载具的底部四个轮子（适用于 Unity 项目）。
- **Rigcar 自动重命名**: 自动识别并重命名四轮载具的底部四个轮子（适用于 Rigcar 插件）。
- **子集命名为顶级**: 将物体名称修改为其顶级父级名称，自动加序号后缀。
- **命名为所处集合名称**: 将物体命名为集合名称。
- **移除后缀**
- **移除顶级后缀并解决重名**
- **mesh 命名为物体**: mesh 名称改为物体名称。
- **物体命名为 mesh**: 物体名称改为包含的 mesh 名称。
- **集合内位置重命名**: 按照集合中的位置关系进行重命名。
- **空间顺序重命名**: 按照空间的位置关系进行重命名（自动加后缀序号）。

## 其他功能

- **旋转位移缩放**
- **列队**: 在指定轴向上按设定距离排列所选物体。
- **随机放置**: 在指定范围内随机放置所选物体。
- **随机缩放**: 在指定缩放范围内对所选物体进行随机缩放。
- **批量对齐顶级父级物体**: 指定两个集合，批量对齐集合 A 中的物体到集合 B 中同名物体上。
- **下落至表面**: 以最后选择的物体表面为基准，将所选物体下落。

## 批量渲染

- **输出路径**: 渲染出的图片存储目标路径。
- **输出名称**: 输出图片名称的前缀。
- **输出格式**: 图片格式。
- **渲染集合**: 选择要进行渲染的集合。
- **相机**: 选择渲染时要使用的相机。
- **聚焦到每个物体**: 渲染时聚焦到每个物体，使物体紧贴相机视口边框（仅在正交模式有效）。
- **边框距离**: 设置正交模式下渲染图片与边框的间距。
- **渲染**: 遍历目标集合下所有物体，以顶级父级分组进行渲染。若需隐藏其他集合内容，需手动在大纲中屏蔽渲染。



## 批量调整渲染设置

- 对指定路径下的 Blender 文件进行批量调整，详见面板。

## 自动绑定工具（角色工具）
该工具主要目的在于处理一些需要重复绑定的物体/角色进行快速绑定（硬关节效果，部件与骨骼的权重非零即一）
![image](https://github.com/user-attachments/assets/2417383b-a1a7-4df3-90cc-2375f790a7a8)

- 绑定的逻辑如下：
- 制定模板。制作一个骨骼作为模板，并创建对应骨骼同名称空物体用于对物体进行重命名的标记
- 导出模板信息。导出骨骼作为模板json
- 导入待处理模型。清空场景，导入一个需要绑定的新的相同结构的物体/角色
- 执行绑定。绑定原理如下：
- 首先会检测目标模型部件与空物体标记的关系，如果一个部件刚好与某个空物体的空间位置成包含在内的关系则将该部件名称改为空物体名称，由于空物体名称与骨骼名称呈对应关系，则该部件名称也会与骨骼呈对应关系，当名称全部修改完毕后执行同名称骨骼关系的绑定，最终根据模板中记录的部件合并逻辑（该逻辑需要手工指定修改json）对部件进行合并重命名
![image](https://github.com/user-attachments/assets/0f843138-6d72-44b8-87a6-ef3d0b42e4db)



- **骨骼操作**:
导出骨骼（对当前主选骨骼以及副选空物体作为模板进行导出配置）
还原骨骼（还原所选配置中的骨骼以及空物体）
还原点位（还原所选配置中的空物体）
重置端点（重置骨骼的端点位置，使骨骼首尾相连，但对于多子集骨骼层级不进行处理）
链接骨骼（将首尾重合的骨骼进行连接，以实现blender中的自动IK功能）
- **配置列表**: 该列表展示已存储的骨骼配置模板json文件，**json文件存储位置在插件根目录中的RigJson文件夹中**。
- **刷新配置列表**: 刷新列表。
- **一键处理角色（64）**: 根据列表中所选模板对导入的64密度尺寸的角色模型进行一键处理绑定。
- **导出目录**: 导出路径。
- **导出角色（完整）**: 将整个场景导出为fbx。
- **导出角色（部件）**: 将角色按照拆分合并逻辑进行拆分导出。
- **接触底部中心创建父级**: 对角色所有连接（贴合）的部件进行分组，部件之间有接触的即划分在同一个父级下。
- **缩小1/2**: 将模型缩小一半。
- **导入模型一键处理**: 导入的模型进行一键处理：断开关联---->处理面朝向---->创建父级---->父级归零---->合并顶点---->应用变换...。
- **重命名并合并**: 根据所选模板对角色部件进行合并，并且重新命名为对应名称。



## 其他注释

- **在线更新**:在插件已激活的情况下在偏好设置中可以看到更新插件的按钮选项，点击后则会自动拉取最新版本对当前版本进行覆盖。**注意：角色配置的json文件也会被覆盖，请注意保存！** 
- **依赖包**: 该工具依赖于Pillow包进行图像处理部分的功能（自动渲染之后最图像的处理，边距等）工具包的依赖包默认自动安装本地路径下的安装包，安装包位于插件根目录的package下，如果需要在除windows外的平台使用需要自行下载对应的.tar.gz文件或者.whl文件放入该文件夹，在进行勾选激活插件时会自动将该文件夹下所有依赖包全部安装，手动安装则可以使用blender内置python进行在线安装，比如cd到blender安装目录中的python文件夹运行：python -m pip install pillow



