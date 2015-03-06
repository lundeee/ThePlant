# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# ThePlant Addon
# --------------------------------------------------------------------------
#
# Author:
# Lundeee
#
#

bl_info = {"name": "ThePlant",
           "author": "Lundeee",
   	       "version": (0, 0, 4, "experimental"),
           "blender": (2, 72, 0),
           "category": "Object",
           "location": "",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "description": "Script for mass duplication of complete rigs"}

import bpy
import random


class ToolsPanel(bpy.types.Panel):
    def __init__(self):
        pass
    bl_label = "The Plant Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "The Plant"
    bl_context = "objectmode"

    
    def draw(self, context):
        layout = self.layout
        layout.label("Duplication!")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("theplant.button", text="Duplicate Characters", icon='MOD_ARRAY')
        row = layout.row(align=True)
        row.operator("theplant.duplicatetomesh", text="Duplicate Characters to mesh", icon='MOD_ARRAY')
        #row.prop_search(self, "lowpoly", bpy.context.scene, "objects")
        
        layout.label("Face tools")
        row = layout.row(align=True)
        row.operator("theplant.makepointcache", text="Make point cache", icon='PARTICLE_POINT')
        row = layout.row(align=True)
        row.operator("theplant.makepointcache", text="Unlink drivers", icon='SCRIPT')
        row = layout.row(align=True)
        row.operator("theplant.makepointcache", text="Unlink shape keys", icon='SCRIPT')        
        layout.label("Tools")
        
        row = layout.row(align=True)
        row.operator("theplant.button2", text="Seperate to layers by distance", icon='RENDERLAYERS')
        row = layout.row(align=True)
        row.operator("theplant.randomizetime", text="Randomize time offset", icon='TIME')
        row = layout.row(align=True)
        row.operator("theplant.randomizetimedistance", text="Offset time by distance", icon='TIME')
        row = layout.row(align=True)
        row.operator("theplant.replacemesh", text="Replace mesh", icon='MESH_DATA')
        row = layout.row(align=True)
        row.operator("theplant.deletehierarchy", text="Delete hierarchy!!", icon='X')


class OBJECT_OT_Button(bpy.types.Operator):
    bl_idname = "theplant.button"
    bl_label="Button"

    def execute(self, context):
        bpy.ops.theplant.charactercopy_dialogoperator('INVOKE_DEFAULT')
        return{'FINISHED'}

class OBJECT_OT_Button2(bpy.types.Operator):
    bl_idname = "theplant.button2"
    bl_label = "Button"

    def execute(self, context):
        bpy.ops.theplant.seperatetolayers('INVOKE_DEFAULT')
        return{'FINISHED'}

###############################
#      deleteHierarchy(
###############################
class deleteHierarchy(bpy.types.Operator):
    bl_idname = "theplant.makepointcache"
    bl_label = "Make point cache"

    def execute(self, context):
       

        return{'FINISHED'}

###############################
#      deleteHierarchy(
###############################

class deleteHierarchy(bpy.types.Operator):
    bl_idname = "theplant.deletehierarchy"
    bl_label = "DeleteHierarchy"

    def execute(self, context):
        ly = []
        for l in bpy.context.scene.layers:
            ly.append(l)

        bpy.context.scene.layers = tuple(True for i in range(0, 20))
        childrens = []
        for o in bpy.context.selected_objects:
            childrens.append(o)
        while childrens != []:
            cur = childrens.pop()
            for c in cur.children:
                childrens.append(c)
            cur.select = True

        bpy.ops.object.delete()
        bpy.context.scene.layers = ly

        return{'FINISHED'}

###############################
#      Randomize time
###############################

class randomizeTime(bpy.types.Operator):
    bl_idname = "theplant.randomizetime"
    bl_label = "Seperate to layers"
    rFactor = bpy.props.FloatProperty(name="Randomize by:",
                                      min=0, max=300)
    offset = bpy.props.IntProperty(name="Offset all by:")

    def execute(self, context):
        obj = bpy.context.scene.objects.active
        for o in obj.children:
            if o.type == "ARMATURE":
                try:
                    timeOffset = random.random()*self.rFactor+self.offset
                    st = o.animation_data.nla_tracks[0].strips[0]
                    st.frame_end = st.frame_end + timeOffset
                    st.frame_start = st.frame_start + timeOffset
                except:
                    pass
                    #print("nono")

        return {'FINISHED'}

    def invoke(self, context, event):

        self.rFactor = 30
        self.offset = 0

        return context.window_manager.invoke_props_dialog(self)
###############################
#   Duplicate rig to mesh
###############################

class duplicateToMesh(bpy.types.Operator):
    bl_idname = "theplant.duplicatetomesh"
    bl_label = "Duplicate rig to mesh vertices"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        
        obj=bpy.context.object
        
        mesh = None        
        for o in bpy.context.selected_objects:
            if o != obj:
                if o.type == "MESH":
                    mesh = o
        
        if mesh != None and obj != None:
            bpy.ops.object.add()
            master = bpy.context.object
            master.location=(0,0,0)
            master.name="Crowd"
            
            for vertice in mesh.data.vertices.items():
                
                obj_new = None
                allObj=[obj]
                copyRel={}
                hasDrivers=[]

                while allObj != []:
                    cur = allObj.pop(0)
                    cur_new=cur.copy()
                    copyRel[cur.name] = cur_new.name
                    bpy.context.scene.objects.link(cur_new)
                    
                    if obj_new == None:
                        obj_new=cur_new
                      
                    if hasattr(cur_new.animation_data , "drivers"):
                        if len(cur_new.animation_data.drivers) > 0:
                            hasDrivers.append(cur_new)

                    if cur.parent != None:
                        if cur.parent.name in copyRel:
                            cur_new.parent=bpy.data.objects[copyRel[cur.parent.name]]                         
                        cur_new.matrix_world = cur.matrix_world
                   
                    if cur_new.type == "MESH":
                        for mod in cur.modifiers:
                            if mod.name == "Armature":
                                if mod.object.name in copyRel:
                                    new_armature_object = copyRel[cur.modifiers['Armature'].object.name]
                                    cur_new.modifiers['Armature'].object = bpy.data.objects[new_armature_object]

                    for ch in cur.children:
                        allObj.append(ch)
                
                for drob in hasDrivers:
                    for d in drob.animation_data.drivers:
                        for var in d.driver.variables:
                            for tar in var.targets:
                                if tar.id != None:
                                    if tar.id.name in copyRel:
                                        new_driver_target = copyRel[tar.id.name]
                                        tar.id = bpy.data.objects[new_driver_target]

                obj_new.parent = master
                obj_new.location = mesh.matrix_world*vertice[1].co 

        return {'FINISHED'}


###############################
#      Replace mesh
###############################    
    
class replaceMesh(bpy.types.Operator):
    bl_idname = "theplant.replacemesh"
    bl_label = "Replace mesh"

#    offset = bpy.props.IntProperty(name="Offset all by:")

    def execute(self, context):

        childrens = []
        obj = bpy.context.scene.objects.active

        for a in bpy.context.selected_objects:
            childrens.append(a)

        for o in childrens:
            try:
                hu = o["Crowd"]
            except:
                hu = False

            if hu == True:
                for ch in o.children:
                    if ch.type == "ARMATURE":
                        for m in ch.children:
                            pass
                            if m.type == "MESH":
                                #: print(m.name)
                                location = m.location
                                bpy.ops.object.select_all(action='DESELECT')
                                m.select = True

                                obj_new = obj.copy()
                                obj_new.location = location
                                bpy.context.scene.objects.link(obj_new)
                                obj_new.layers = obj.layers

                                bpy.ops.object.select_all(action='DESELECT')
                                m.select = True
                                bpy.ops.object.delete()

                                bpy.ops.object.select_all(action='DESELECT')
                                obj_new.select = True

                                bpy.context.scene.objects.active = ch
                                bpy.ops.object.parent_set()

                                try:
                                    obj_new.modifiers["armature"].object = ch
                                except:
                                    bpy.context.scene.objects.active = obj_new
                                    bpy.ops.object.modifier_add(type="ARMATURE")
                                    obj_new.modifiers["Armature"].object = ch

        return {'FINISHED'}

    def invoke(self, context, event):

        self.rFactor = 30
        self.offseti = 0

        return context.window_manager.invoke_props_dialog(self)

#########################################
#  randomizeTimeDistance
#########################################

class randomizeTimeDistance(bpy.types.Operator):
    bl_idname = "theplant.randomizetimedistance"
    bl_label = "Seperate to layers"

    dFactor = bpy.props.FloatProperty(name="Difference last-first:")
    offset = bpy.props.IntProperty(name="Offset all by:")
    rFactor = bpy.props.FloatProperty(name="Randomize by:")

    def execute(self, context):
        obj = bpy.context.scene.objects.active
        point = obj.location
        childrens = []

        min = 100000000000
        max = 0

        for o in bpy.context.selected_objects:
            try:
                hu = o["Crowd"]
            except:
                hu = False
            #print(hu)

            if hu == True:
                for ch in o.children:
                    #print(ch.name)
                    if ch.type == "ARMATURE":
                        #print(ch.name)
                        distanceV = ch.location-point
                        distance = distanceV.length
                        childrens.append([ch, distance])
                        if distance > max:
                            max = distance
                        if distance < min:
                            min = distance

                print(min, max)
                fac = self.dFactor/max

        for o in childrens:
            try:
                st = o[0].animation_data.nla_tracks[0].strips[0]
                timeOffset = (o[1]-min)*fac+random.random()*self.rFactor+self.offset
                st.frame_end = st.frame_end + timeOffset + 1
                st.frame_start = st.frame_start + timeOffset

            except:
                pass
                #print("nono2")

        return {'FINISHED'}

    def invoke(self, context, event):

        self.rFactor = 0
        self.offset = 0
        self.dFactor = 30

        return context.window_manager.invoke_props_dialog(self)

#########################################
#  seperateToLayers
#########################################

class seperateToLayers(bpy.types.Operator):
    bl_idname = "theplant.seperatetolayers"
    bl_label = "Seperate to layers"

    slayer = bpy.props.IntProperty(name="Start layer:",
                                   min=1, max=300)
    nlayers = bpy.props.IntProperty(name="Number of layers:",
                                    min=1, max=300)

    def execute(self, context):
        bpy.context.scene.layers = tuple(True for i in range(0, 20))
        childrens = []
        obj = bpy.context.scene.objects.active

        indexLayer = self.slayer
        layerSpan = self.nlayers

        point = obj.location
        for o in bpy.context.selected_objects:
            try:
                if o["Crowd"]:
                    for ch in o.children:
                        if ch.type == "ARMATURE":
                            disanceV = ch.location-point
                            childrens.append([ch, disanceV.length])
            except:
                pass
               #print("Finding charaters problem!")

        sortedCH = sorted(childrens, key=lambda a: a[1])
        numObj = len(sortedCH)

        fac = numObj/layerSpan

        for b in range(0, numObj):
            layer = int(b/fac)+indexLayer
            for c in sortedCH[b][0].children:

                if c.type == "MESH":
                    c.layers = tuple(i == layer  for i in range(0, 20))

        bpy.context.scene.layers = tuple(i == 0 for i in range(0, 20))

        return {'FINISHED'}

    def invoke(self, context, event):

        self.slayer = 10
        self.nlayers = 4

        return context.window_manager.invoke_props_dialog(self)

Xcopies = 2
Ycopies = 2
XSpacing = 10.0
YSpacing = 10.0
theBool = False
theString = "Lorem ..."
theEnum = 'one'
RandomXY = 0.8
LeaveOrg = True
ParentName = "Crowd"
Alayer = 1
Mlayer = 1
RandomTime = 10

class CharacterCopyDialogOperator(bpy.types.Operator):
    bl_idname = "theplant.charactercopy_dialogoperator"
    bl_label = "Character Copy"

    xcopies = bpy.props.IntProperty(name="Copies in X:",
                                    min=1, max=300)
    ycopies = bpy.props.IntProperty(name="Copies in Y:",
                                    min=1, max=300)
    xspacing = bpy.props.FloatProperty(name="Spacing in X:",
                                       min=1, max=300)
    yspacing = bpy.props.FloatProperty(name="Spacing in Y:",
                                       min=1, max=300)
    randomXY = bpy.props.FloatProperty(name="Randomize position:",
                                       min=0, max=300)
    alayer = bpy.props.IntProperty(name="Amramture layer:",
                                   min=1, max=20)
    mlayer = bpy.props.IntProperty(name="Geometry layer:",
                                   min=1, max=20)

    my_bool = bpy.props.BoolProperty(name="Leave original:")
    my_string = bpy.props.StringProperty(name="Parent Empty name:")

    def execute(self, context):
        global ParentName, Xcopies, Ycopies, XSpacing
        global YSpacing, RandomXY, LeaveOrg, Alayer, Mlayer, RandomTime
        RandomXY = self.randomXY
        Xcopies = self.xcopies
        Ycopies = self.ycopies
        XSpacing = self.xspacing
        YSpacing = self.yspacing
        LeaveOrg = self.my_bool
        ParentName = self.my_string
        Alayer = self.alayer
        Mlayer = self.mlayer
        RandomTime = self.randomTime
        bpy.ops.theplant.charactercopy()

        return {'FINISHED'}

    def invoke(self, context, event):

        global ParentName, Xcopies, Ycopies, XSpacing, YSpacing, theBool
        global theString, theEnum, RandomXY, LeaveOrg, Alayer, Mlayer, RandomTime
        self.randomTime = RandomTime
        self.randomXY = RandomXY
        self.xspacing = XSpacing
        self.yspacing = YSpacing
        self.xcopies = Xcopies
        self.ycopies = Ycopies
        self.my_bool = LeaveOrg
        self.my_string = theString
        self.my_enum = theEnum
        self.my_string = ParentName
        self.alayer = Alayer
        self.mlayer = Mlayer

        return context.window_manager.invoke_props_dialog(self)

class CharacterCopy(bpy.types.Operator):
    """Duplicating objecs"""
    bl_idname = "theplant.charactercopy"
    bl_label = "theplant.charactercopy"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):        # execute() is called by blender when running the operator.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # Get the current scene
        scene = context.scene
        obj = scene.objects.active

        bpy.ops.object.add()
        parent = scene.objects.active

        parent.location = (0, 0, 0)
        parent["Crowd"] = True

        global ParentName, Xcopies, Ycopies, XSpacing, YSpacing
        global RandomXY, LeaveOrg, Alayer, Mlayer, RandomTime

        alayer = Alayer
        mlayer = Mlayer
        leaveOrg = LeaveOrg
        width = Xcopies
        depth = Ycopies
        xspacing = XSpacing
        yspacing = YSpacing
        rA = RandomXY
        parent.name = ParentName

        for i in range(width):
            for j in range(depth):
                r1 = (random.random()-0.5)*2*rA
                r2 = (random.random()-0.5)*2*rA

                #location = (j, i, obj.location[2])
                obj_new = None
                allObj=[obj]
                copyRel={}

                
                if obj != None:
                    while allObj != []:
                        cur = allObj.pop(0)
                        if cur.parent != None:
                            cur_new=cur.copy()
                            copyRel[cur.name] = cur_new.name
                            bpy.context.scene.objects.link(cur_new)
                            try:
                                cur_new.parent=bpy.data.objects[copyRel[cur.parent.name]]
                                
                            except:
                                obj_new=cur_new
                            cur_new.matrix_world = cur.matrix_world

                        else:
                            
                            cur_new=cur.copy()
                            bpy.context.scene.objects.link(cur_new)
                            copyRel[cur.name] = cur_new.name
                            obj_new=cur_new
                        if cur_new.type == "MESH":
                            try:
                                new_armature_object=copyRel[cur.modifiers['Armature'].object.name]
                                cur_new.modifiers['Armature'].object=bpy.data.objects[new_armature_object]
                            except:
                                pass
                           

                        for i in cur.children:
                            allObj.append(i)

        bpy.ops.object.select_all(action="DESELECT")

        if leaveOrg is False:
            obj.select = True
            for o in obj.children:
                o.select = True
            bpy.ops.object.delete()
        set_layer = lambda y: tuple(i == y for i in range(0, 20))

        for c in parent.children:
            if alayer != 1:
                c.layers = set_layer(alayer-1)

            for m in c.children:
                if mlayer != 1:
                    m.layers = set_layer(mlayer-1)


        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()




