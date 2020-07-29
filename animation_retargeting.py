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
    
def get_joint_name(jnt):
    return jnt[jnt.find(":")+1:]

def get_time_range(joint_list):
    start_time = maya.cmds.findKeyframe(joint_list[0], which = "first")
    end_time = maya.cmds.findKeyframe(joint_list[0], which = "last")
    return start_time, end_time
            
def connect_joints(src_joints, dst_joints):
    src_ns = src_joints[0].split(":")[0]
    dst_ns = dst_joints[0].split(":")[0]
    
    for src_joint in src_joints:
        src_joint_name = src_joint.split(":")[1]
        dst_joint = "{}:{}".format(dst_ns, src_joint_name)
        if maya.cmds.objExists(src_joint) and maya.cmds.objExists(dst_joint):
            maya.cmds.orientConstraint(src_joint, dst_joint, mo=True)
            if src_joint_name == "Hips":
                maya.cmds.parentConstraint(src_joint, dst_joint, mo=True)

def run(animation_filename, character_filename):
    # Create a new scene
    maya.cmds.file(new=True, f=True)
    
    # Create char and anim namespaces and bring in character and animation
    character_namespace = create_reference(character_filename)
    animation_namespace = create_reference(animation_filename)
    
    # get a list of joints of both the anim and char
    animation_joints = get_joints_from_namespace(animation_namespace)
    character_joints = get_joints_from_namespace(character_namespace)
    
    #set animation start and end times
    start_time, end_time = get_time_range(animation_joints)
    maya.cmds.currentTime(start_time)
    maya.cmds.viewFit(f = 0.5)
    #connect joints
    connect_joints(animation_joints, character_joints)

    # bake animation
    maya.cmds.select(character_joints)
    maya.cmds.bakeResults(
        simulation = True,
        time = (start_time, end_time),
        disableImplicitControl = True,
        preserveOutsideKeys = True,
        minimizeRotation = True,
        shape = True
    )

    # Remove references
    maya.cmds.file(animation_filename, rr = True)
    
    # Save a file
    renamed_file = r"D:\CapnSquirrel\Development\TechArt\exercise\{0}_{1}".format(character_namespace, animation_namespace)
    maya.cmds.file(rename=renamed_file)
    maya.cmds.file(save=True, f=True)

animations_dir = r"D:\CapnSquirrel\Development\TechArt\exercise\animations\maya"
animation_files = [animations_dir + r"\01_" + ('%02d' %x) + ".ma" for x in range(1,11)]
character_filename = "D:\CapnSquirrel\Development\TechArt\exercise\character.mb"

for anim_file in animation_files:
    run(anim_file, character_filename)