bl_info = {
    "name": "MiaoToolBox",
    "author": "MuyouHCD",
    "version": (4,8,37),
    "blender": (3, 6, 1),
    "location": "View3D",
    "description": "python.exe -m pip install pillow",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}
import sys
import os
import subprocess
import bpy
#------------------------------------------------------------------------------------------
#自动检测缺失库进行补充安装

def install_and_import(module_name, package_name=None):
    package_name = package_name or module_name
    try:
        __import__(module_name)
        print(f"模块 '{module_name}' 已经安装。")
    except ImportError:
        print(f"模块 '{module_name}' 未安装。正在安装 '{package_name}'...")
        try:
            # 获取 Blender 内置的 Python 解释器路径
            python_executable = sys.executable
            python_bin_dir = os.path.dirname(python_executable)

            # 使用完整的路径，并用引号括起来
            cmd = f'cmd /c "cd /d "{python_bin_dir}" & "{python_executable}" -m pip install {package_name}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            print(result.stdout)
            print(result.stderr)

            if result.returncode != 0:
                raise Exception(f"命令执行失败：{result.stderr}")

            print(f"模块 '{package_name}' 安装成功。")
        except Exception as e:
            print(f"模块 '{package_name}' 安装失败：{e}")
            raise
    finally:
        globals()[module_name] = __import__(module_name)
        print(f"模块 '{module_name}' 已经导入。")

# 检查并安装模块
def check_and_install_modules():
    # 使用 'PIL' 模块，实际与 'Pillow' 包名关联
    required_modules = {'PIL': 'Pillow'}
    for module_name, package_name in required_modules.items():
        install_and_import(module_name, package_name)

#------------------检测模块是否存在-------------------
check_and_install_modules()
#------------------------------------------------------------------------------------------

from . import update
from . import operators
from . import panels
from . import CorrectRotation
from . import renderconfig
from . import RemoveUnusedMatSlots
from . import AutoRender
from . import AutoRenameCar
from . import ExportFbx
from . import Voxelizer
from . import AutoRig
from . import AutolinkTexture
from . import MoveOrigin
from . import AutoBake
from . import AutoBakeRemesh
from . import Combin
from . import RenameTool
from . import RemoveObj
from . import SelectTool
from . import ExoprtObj
from . import MaterialOperator
from . import UVCleaner
from . import UVformater
from . import RenderFrame
from . import BoneProcess


def register():
    AutoBake.register()
    AutoBakeRemesh.register()
    AutoRenameCar.register()
    AutoRender.register()
    AutoRig.register()
    AutolinkTexture.register()
    BoneProcess.register()
    Combin.register()
    CorrectRotation.register()
    ExoprtObj.register()
    ExportFbx.register()
    MaterialOperator.register()
    MoveOrigin.register()
    operators.register()
    panels.register()
    RenameTool.register()
    RemoveObj.register()
    renderconfig.register()
    RenderFrame.register()
    RemoveUnusedMatSlots.register()
    SelectTool.register()
    UVCleaner.register()
    UVformater.register()
    update.register()
    Voxelizer.register()

def unregister():
    AutoBake.unregister()
    AutoBakeRemesh.unregister()
    AutoRenameCar.unregister()
    AutoRender.unregister()
    AutoRig.unregister()
    AutolinkTexture.unregister()
    BoneProcess.unregister()
    Combin.unregister()
    CorrectRotation.unregister()
    ExoprtObj.unregister()
    ExportFbx.unregister()
    MaterialOperator.unregister()
    MoveOrigin.unregister()
    operators.unregister()
    panels.unregister()
    RenameTool.unregister()
    RemoveObj.unregister()
    renderconfig.unregister()
    RenderFrame.unregister()
    RemoveUnusedMatSlots.unregister()
    SelectTool.unregister()
    UVCleaner.unregister()
    UVformater.unregister()
    update.unregister()
    Voxelizer.unregister()



if __name__ == "__main__":
    register()