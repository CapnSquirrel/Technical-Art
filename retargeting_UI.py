from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI

import pymel.core
import os

def get_maya_window():
    maya_window_ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(maya_window_ptr), QtWidgets.QWidget)
    
class AnimationRetargetDialog(QtWidgets.QDialog):
    
    def __init__(self):
        maya_main = get_maya_window()
        super(AnimationRetargetDialog, self).__init__(maya_main)
        self.setWindowTitle("Animation Retarget")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.have_src = False
        self.have_dst = False
        
    def create_widgets(self):
        self.dir_name_label = QtWidgets.QLabel()
        self.dir_name_label.setText("Source directory path:") 
        self.dir_name = QtWidgets.QLineEdit()
        self.dir_name.setEnabled(False)
        self.dir_name_button = QtWidgets.QPushButton("Open directory")

        self.char_name_label = QtWidgets.QLabel()
        self.char_name_label.setText("Destination character file path:") 
        self.char_name = QtWidgets.QLineEdit()
        self.char_name.setEnabled(False)
        self.char_name_button = QtWidgets.QPushButton("Open file")

        self.retarget_btn = QtWidgets.QPushButton("Retarget")
        self.retarget_btn.setEnabled(False)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        dir_prompt_layout = QtWidgets.QHBoxLayout(self)
        char_prompt_layout = QtWidgets.QHBoxLayout(self)
        btn_layout = QtWidgets.QHBoxLayout(self)
        
        dir_prompt_layout.addWidget(self.dir_name_label)
        dir_prompt_layout.addWidget(self.dir_name)
        dir_prompt_layout.addWidget(self.dir_name_button)

        char_prompt_layout.addWidget(self.char_name_label)
        char_prompt_layout.addWidget(self.char_name)
        char_prompt_layout.addWidget(self.char_name_button)

        btn_layout.addWidget(self.retarget_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(dir_prompt_layout)
        main_layout.addLayout(char_prompt_layout)
        main_layout.addLayout(btn_layout)
        
    def create_connections(self):
        self.retarget_btn.clicked.connect(self.retarget)
        self.cancel_btn.clicked.connect(self.close)
        self.dir_name_button.clicked.connect(self.dir_dialog)
        self.char_name_button.clicked.connect(self.file_dialog)

    def check_prereqs(self):
        return self.have_src and self.have_dst

    def dir_dialog(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select animation directory", "/home")
        if dir_path != "":
            self.have_src = True
            self.dir_name.setText(dir_path)

        if self.check_prereqs():
            self.retarget_btn.setEnabled(True)

    def file_dialog(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Select character file", "/home")[0]
        if file_path != "":
            self.have_dst = True
            self.char_name.setText(file_path)
            
        if self.check_prereqs():
            self.retarget_btn.setEnabled(True)

    def retarget(self):
        src_path = self.dir_name.text()
        dst_path = self.char_name.text()
        try:
            retarget_animations(src_path, dst_path)
        except:
            print("Something went wrong!")

try:
    dialog.close()
    dialog.deleteLater()
except:
    pass
    
dialog = AnimationRetargetDialog()
dialog.show()
    

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

'''
    Takes one source animation file path and one character rig file path as input and retargets the animation onto the character.
'''
def retarget_animation(anim_path, char_path):
    # create a new scene
    pymel.core.system.newFile(force=True)
    
    # create char and anim namespaces and bring in character and animation
    animation_namespace = create_reference(anim_path)
    character_namespace = create_reference(char_path)

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
    renamed_file = r"D:\CapnSquirrel\Development\TechArt\exercise\{}_{}.mb".format(character_namespace, animation_namespace)
    pymel.core.system.renameFile(renamed_file)
    pymel.core.system.saveFile(save = True, force = True)

'''
    Takes a directory path where one or more source animation files are stored and one character rig file path as input and retargets the animations onto the character.
'''
def retarget_animations(anim_dir, char_path):
    anims = os.listdir(anim_dir)
    for anim in anims:
        anim_path = anim_dir + "\\" + anim
        retarget_animation(anim_path, char_path)
