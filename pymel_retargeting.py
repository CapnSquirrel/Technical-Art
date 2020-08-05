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
    
    pymel.core.system.createReference(file_path, namespace = name)
    return name

def get_time_range(joint_list):
    start_time = pymel.core.animation.findKeyframe(joint_list[0], which = "first")
    end_time = pymel.core.animation.findKeyframe(joint_list[0], which = "last")
    return start_time, end_time

def get_joint_name(jnt):
    return jnt[jnt.find(":")+1:]

def get_joints_from_namespace(ns):
    return pymel.core.general.ls(ns + ":*", type="joint")

def connect_joints(src_joints, dst_joints):
    src_ns = src_joints[0].split(":")[0]
    dst_ns = dst_joints[0].split(":")[0]
    
    for src_joint in src_joints:
        src_joint_name = src_joint.split(":")[1]
        dst_joint = "{}:{}".format(dst_ns, src_joint_name)
        if pymel.core.general.objExists(src_joint) and pymel.core.general.objExists(dst_joint):
            pymel.core.animation.orientConstraint(src_joint, dst_joint, mo=True)
            if src_joint_name == "Hips":
                pymel.core.animation.parentConstraint(src_joint, dst_joint, mo=True)

def retarget_animation(animation_path, character_path):
    # create a new scene
    pymel.core.system.newFile(force=True)
    
    # create char and anim namespaces and bring in character and animation
    animation_namespace = create_reference(animation_path)
    character_namespace = create_reference(character_path)

    # get a list of joints of both the anim and char
    animation_joints = get_joints_from_namespace(animation_namespace)
    character_joints = get_joints_from_namespace(character_namespace)
    
    # set animation start and end times
    start_time, end_time = get_time_range(animation_joints)
    pymel.core.animation.currentTime(start_time)
    pymel.core.rendering.viewFit(f = 0.5)

    # connect joints
    connect_joints(animation_joints, character_joints)

    # bake animation
    pymel.core.general.select(character_joints)
    pymel.core.animation.bakeResults(
        simulation = True,
        time = (start_time, end_time),
        disableImplicitControl = True,
        preserveOutsideKeys = True,
        minimizeRotation = True,
        shape = True
    )

    # cemove references
    anim_ref = pymel.core.system.FileReference(namespace=animation_namespace)
    anim_ref.remove()

    # Save a file
    renamed_file = r"D:\CapnSquirrel\Development\TechArt\exercise\{}_{}".format(character_namespace, animation_namespace)
    pymel.core.system.renameFile(renamed_file)
    pymel.core.system.saveFile(save = True, force = True)

animation_path = r"D:\CapnSquirrel\Development\TechArt\exercise\animations\maya\01_01.ma"
character_path = r"D:\CapnSquirrel\Development\TechArt\exercise\character.mb"

retarget_animation(animation_path, character_path)