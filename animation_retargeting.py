import maya.cmds
import os

def create_reference(file_path):
    if not os.path.exists(file_path):
        maya.cmds.error("File path {0} doesn't exist".format(file_path))
        return
    
    head, tail = os.path.split(file_path)
    root, ext = os.path.splitext(tail)
    maya.cmds.file(file_path, r=True, ns=root)

def get_joints_from_namespace(ns):
    return maya.cmds.ls(ns + ":*", type="joint")

# Create a new scene
maya.cmds.file(new=True, f=True)

# Create char and anim namespaces

# animations_dir = r"D:\CapnSquirrel\Development\TechArt\exercise\animations\maya"
# prefix = r"\01_"
# animation_namespaces = [animations_dir + prefix + ('%02d' %x) + ".ma" for x in range(1,11)]
# animation_namespace = r"D:\CapnSquirrel\Development\TechArt\exercise\animations\maya\01_01.ma"
# character_namespace = "D:\CapnSquirrel\Development\TechArt\exercise\character.mb"

# for ns in animation_namespaces:
#    create_reference(ns)

# Create char and anim namespaces
animation_filename = r"D:\CapnSquirrel\Development\TechArt\exercise\animations\maya\01_01.ma"
character_filename = "D:\CapnSquirrel\Development\TechArt\exercise\character.mb"

# Bring in character
character_namespace = create_reference(character_filename)

# Bring in the animation
animation_namespace = create_reference(animation_filename)

# get a list of joints of both the anim and char
character_joints = get_joints_from_namespace(character_namespace)
animation_joints = get_joints_from_namespace(animation_namespace)
character_joints