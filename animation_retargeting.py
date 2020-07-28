import maya.cmds
import os

def create_reference(file_path):
    if not os.path.exists(file_path):
        maya.cmds.error("File path {0} doesn't exist".format(file_path))
        return
    
    head, tail = os.path.split(file_path)
    root, ext = os.path.splitext(tail)
    if root[0].isdigit():
        root = "anim" + root
    
    maya.cmds.file(file_path, r=True, ns=root)
    return root
    
def get_joints_from_namespace(ns):
    return maya.cmds.ls(ns + ":*", type="joint")
    
def connect_attributes(src, dst, attr):
    srcString = "{0}.{1}".format(src, attr)
    dstString = "{0}.{1}".format(dst, attr)
    maya.cmds.connectAttr(srcString, dstString, f=True)
    
def run():
    # Create a new scene
    maya.cmds.file(new=True, f=True)
    
    # Create char and anim namespaces
    animation_filename = r"D:\CapnSquirrel\Development\TechArt\exercise\animations\maya\01_01.ma"
    character_filename = "D:\CapnSquirrel\Development\TechArt\exercise\character.mb"
    
    # Bring in character
    character_namespace = create_reference(character_filename)
    
    # Bring in the animation
    animation_namespace = create_reference(animation_filename)
    
    # get a list of joints of both the anim and char
    animation_joints = get_joints_from_namespace(animation_namespace)
    character_joints = get_joints_from_namespace(character_namespace)
    
    # Attach animation to character
    attributes = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
    
    for char_joint in character_joints:
        cjoint_name = char_joint[char_joint.find(":")+1:]
        for anim_joint in animation_joints:
            ajoint_name = anim_joint[anim_joint.find(":")+1:]
            if cjoint_name == ajoint_name:
                print(anim_joint, char_joint)
                for attr in attributes:
                    connect_attributes(anim_joint, char_joint, attr)
    
    # Remove references

    # Save a file
    
run()