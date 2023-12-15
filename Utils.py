import os
import platform
import shutil

def get_notepadpp_info():
    if platform.system() != 'Windows':
        return False, None
    
    # 检查是否在 PATH 中
    notepadpp_executable = shutil.which('notepad++')
    if notepadpp_executable is not None:
        return True, notepadpp_executable

    # 检查指定安装路径
    notepadpp_path = r'C:\Program Files\Notepad++\notepad++.exe'  # 替换为你的安装路径
    if os.path.exists(notepadpp_path):
        return True, notepadpp_path

    # 检查备用安装路径
    notepadpp_path_x86 = r'C:\Program Files (x86)\Notepad++\notepad++.exe'  # 替换为你的安装路径
    if os.path.exists(notepadpp_path_x86):
        return True, notepadpp_path_x86

    # 如果都没有找到，返回False和None
    return False, None

