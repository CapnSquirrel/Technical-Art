import maya.cmds
import os

def create_reference(file_path):
    if not os.path.exists(file_path):
        maya.cmds.error("File path {0} doesn't exist".format(file_path))
        return
    
    _, file_name = os.path.split(file_path)
    name, _ = os.path.splitext(file_name)
    if name[0].isdigit():
        name = "anim" + name
    
    maya.cmds.file(file_path, r=True, ns=name)
    return name
    
def get_joints_from_namespace(ns):
    return maya.cmds.ls(ns + ":*", type="joint")
    
def connect_attributes(src, dst, attr):
    src_string = "{0}.{1}".format(src, attr)
    dst_string = "{0}.{1}".format(dst, attr)
    maya.cmds.connectAttr(src_string, dst_string, f=True)
    # maya.cmds.parentConstraint(src, dst, mo=True)
    
def get_joint_name(jnt):
    return jnt[jnt.find(":")+1:]
    
def connect_and_bake_joints(src_joints, dst_joints):
    rot_attributes = ["rotateX", "rotateY", "rotateZ"]
    trans_attributes = ["translateX", "translateY", "translateZ"]
    
    start_time = maya.cmds.playbackOptions(q = True, min = True)
    end_time = maya.cmds.playbackOptions(q = True, max = True)

    for dst_joint in dst_joints:
        dst_joint_name = get_joint_name(dst_joint)
        for src_joint in src_joints:
            src_joint_name = get_joint_name(src_joint)
            if dst_joint_name == src_joint_name:
                # maya.cmds.parentConstraint(src_joint, dst_joint, mo=True)
                # not sure about this
                # for attr in rot_attributes:
                #     connect_attributes(src_joint, dst_joint, attr)
                # if dst_joint_name == "Hips":
                #     for attr in trans_attributes:
                #         connect_attributes(src_joint, dst_joint, attr)

        maya.cmds.select(dst_joint)
        maya.cmds.bakeResults(
            simulation = True,
            time = (start_time, end_time),
            disableImplicitControl = True,
            preserveOutsideKeys = True,
            minimizeRotation = True,
            shape = True
        )
          
def sync_keyframes():
    maya.cmds.findKeyframe(which="first")

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
    connect_and_bake_joints(animation_joints, character_joints)
    
    # Remove references
    # maya.cmds.file(animation_filename, rr = True)
    # maya.cmds.file(character_filename, ir = True)
    
    # Save a file
    renamed_file = r"D:\CapnSquirrel\Development\TechArt\exercise\{0}_{1}".format(character_namespace, animation_namespace)
    maya.cmds.file(rename=renamed_file)
    # maya.cmds.file(save=True, f=True)
    
run()


