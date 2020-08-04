import pymel.core
import os

def create_reference(file_path):
    if not os.path.exists(file_path):
        pymel.core.system.error("File path {} doesn't exist".format(file_path))
        return
    
    _, file_name = os.path.split(file_path)
    name, _ = os.path.splitext(file_name)
    if name[0].isdigit():
        name = "anim" + name
    
    pymel.core.system.createReference(file_path, namespace=name)
    return name
    
def get_joint_name(jnt):
    return jnt[jnt.find(":")+1:]

def get_joints_from_namespace(ns):
    return pymel.core.general.ls(ns + ":*", type="joint")
    
pymel.core.system.newFile(force=True)

file_path = r"D:\CapnSquirrel\Development\TechArt\exercise\character.mb"

character_namespace = create_reference(file_path)
character_joints = get_joints_from_namespace(character_namespace)