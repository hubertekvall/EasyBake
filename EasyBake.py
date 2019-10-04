#this script is dedicated to the public domain under CC0 (https://creativecommons.org/publicdomain/zero/1.0/)
#do whatever you want with it! -Bram

bl_info = {
    "name": "EasyBake",
    "category": "3D View",
    "blender": (2, 80, 0),
    "author": "Bram Eulaers",
    "description": "Simple texture baking UI for fast iteration. Can be found in the 3D View Sidebar under 'bake'."
    }

import bpy
import os
import bmesh
from bpy.props import EnumProperty, BoolProperty, StringProperty, FloatProperty, IntProperty



def unhide(objectType):
    if bpy.data.objects.get(objectType) is None:
        for o in bpy.data.collections[objectType].objects:
            o.hide_viewport = False
    else:
        bpy.data.objects[objectType].hide_viewport = False

def hide(objectType):
    if bpy.data.objects.get(objectType) is None:
        for o in bpy.data.collections[objectType].objects:
            o.hide_viewport = True
    else:
        bpy.data.objects[objectType].hide_viewport = True


def find_link():
    active_link = next(l for l in currentLinks if l.to_socket == outputNode.inputs['Surface'])        




class EasyBakeUIPanel(bpy.types.Panel):
    """EasyBakeUIPanel Panel"""
    bl_label = "EasyBake"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Bake"


    def draw_header(self, _):
        layout = self.layout
        layout.label(text="", icon='SCENE')

    def draw(self, context):
        layout = self.layout
        

        
        col = layout.column(align=True)
        col.separator()
        row = col.row(align = True)
        row.prop(context.scene.render.bake, "cage_extrusion", text="Ray Distance")
        col.separator()



        box = layout.box()
        col = box.column(align=True)
        row = col.row(align = True)
        row.label(text="Width:")
        row.prop(context.scene, "bakeWidth", text="")

        
        row = col.row(align = True)
        row.label(text="Height:")
        row.prop(context.scene, "bakeHeight", text="")

        row = col.row(align = True)
        row.label(text="Padding:")
        row.prop(context.scene.render.bake, "margin", text="")
        
        



        col = layout.column(align=True)
        col.separator()
        col.prop(context.scene, 'bakeFolder', text="")
        row = col.row(align = True)
        row.label(text="Filename:")
        row.prop(context.scene, "bakePrefix", text="")
        
        col.separator()




        box = layout.box()

        col = box.column(align=True)
        row = col.row(align = True)
        row.prop(context.scene, "bakeNormal", icon="SHADING_RENDERED", text="Tangent Normal")
        if context.scene.bakeNormal:
            row.prop(context.scene, "samplesNormal", text="")

        row = col.row(align = True)
        row.prop(context.scene, "bakeObject", icon="SHADING_RENDERED", text="Object Normal")
        if context.scene.bakeObject:
            row.prop(context.scene, "samplesObject", text="")

        row = col.row(align = True)
        row.prop(context.scene, "bakeAO", icon="SHADING_SOLID", text="Occlusion")
        if context.scene.bakeAO:
            row.prop(context.scene, "samplesAO", text="")
        
        row = col.row(align = True)
        row.prop(context.scene, "bakeColor", icon="SHADING_TEXTURE", text="Color")
        if context.scene.bakeColor:
            row.prop(context.scene, "samplesColor", text="")

        row = col.row(align = True)
        row.prop(context.scene, "bakeRoughness", icon="SHADING_TEXTURE", text="Roughness")
        if context.scene.bakeRoughness:
            row.prop(context.scene, "samplesRoughness", text="")

        row = col.row(align = True)
        row.prop(context.scene, "bakeMetallic", icon="SHADING_TEXTURE", text="Metallic")
        if context.scene.bakeMetallic:
            row.prop(context.scene, "samplesMetallic", text="")
            

        row = col.row(align = True)
        row.prop(context.scene, "bakeUV", icon="SHADING_WIRE", text="UV Snapshot")
        
        
        
        col = layout.column(align=True)
        col.separator()
        row = col.row(align = True)
        op = row.operator("brm.bake", text="BAKE", icon="RENDER_RESULT")

        




















class EasyBake(bpy.types.Operator):
    """Bake and save textures"""
    bl_idname = "brm.bake"
    bl_label = "set normal"
    bl_options = {"UNDO"}
    

    def execute(self, context):  

        #test if everything is set up OK first:
        #test folder
        hasfolder = os.access(context.scene.bakeFolder, os.W_OK)
        if hasfolder is False:
            self.report({'WARNING'}, "Select a valid export folder!")
            return {'FINISHED'}



        selection_count = len(bpy.context.selected_objects)
        solo_bake = False
        # bakeSource = {}
        # base = {}

        if selection_count:
            base = bpy.context.active_object
         
            if selection_count == 1:
                solo_bake = True
                bakeSource = base

            elif selection_count == 2:
                bakeSource = [bs for bs in bpy.context.selected_objects if bs != base][0]

            else:
                self.report({'WARNING'}, "Too many objects selected! Max two!")
                return {'FINISHED'}       

        else:
            self.report({'WARNING'}, "Select your objects to bake first!")    
            return {'FINISHED'}  



        
    #2 make sure we are in object mode and nothing is selected
        if bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

    #5 remember render engine and switch to CYCLES for baking
        orig_renderer = bpy.data.scenes[bpy.context.scene.name].render.engine
        bpy.data.scenes[bpy.context.scene.name].render.engine = "CYCLES"

    #6 create temporary bake image and material
        
        bakeimage = bpy.data.images.new("BakeImage", width=context.scene.bakeWidth, height=context.scene.bakeHeight)

        generated_nodes = {}
        for mat in base.data.materials:
               
            node_tree = mat.node_tree
            new_node = node_tree.nodes.new("ShaderNodeTexImage")
            generated_nodes[mat] = new_node
            new_node.select = True
            node_tree.nodes.active = new_node
            new_node.image = bakeimage
             

 
    



    #11 bake all maps!
        if context.scene.bakeNormal:
            bpy.context.scene.cycles.samples = context.scene.samplesNormal
            bpy.ops.object.bake(type='NORMAL', use_clear=True, use_selected_to_active=not solo_bake, normal_space='TANGENT')
            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_normal.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()
        
        if context.scene.bakeObject:
            bpy.context.scene.cycles.samples = context.scene.samplesObject
            bpy.ops.object.bake(type='NORMAL', use_clear=True, use_selected_to_active=not solo_bake, normal_space='OBJECT')
            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_object.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()

        if context.scene.bakeAO:
            bpy.context.scene.cycles.samples = context.scene.samplesAO
            bpy.ops.object.bake(type='AO', use_clear=True, use_selected_to_active=not solo_bake)
            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_ao.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()

        if context.scene.bakeColor:
            bpy.context.scene.cycles.samples = context.scene.samplesColor
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.context.scene.render.bake.use_pass_color = True
            bpy.ops.object.bake(type='DIFFUSE', use_clear=True, use_selected_to_active=not solo_bake)
            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_color.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()
        
        if context.scene.bakeRoughness:
            bpy.context.scene.cycles.samples = context.scene.samplesRoughness
            bpy.ops.object.bake(type='ROUGHNESS', use_clear=True, use_selected_to_active=not solo_bake)
            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_roughness.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()


        #UV SNAPSHOT
        if context.scene.bakeUV:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.editmode_toggle()
            original_type = bpy.context.area.type
            bpy.context.area.type = "IMAGE_EDITOR"
            uvfilepath = context.scene.bakeFolder+context.scene.bakePrefix+"_uv.png"
            bpy.ops.uv.export_layout(filepath=uvfilepath, size=(context.scene.bakeWidth, context.scene.bakeHeight))
            bpy.context.area.type = original_type
        
        #
        #
        # Bake Metallic
        if context.scene.bakeMetallic:
            old_materials = []
            new_materials = []
            

            # Backup old materials of the bakesource and replace the slots with new clones
            # Easier cleanup later on when we can just restore the old materials and discard our clones

            for mslot in bakeSource.material_slots:
                old_materials.append(mslot.material)
                clone = mslot.material.copy()
                mslot.material = clone
                new_materials.append(clone)


            for material in new_materials:
              
                node_tree = material.node_tree
                links = node_tree.links
                nodes = node_tree.nodes
                material_output = nodes['Material Output']
                
                # active_link = next(link for link in links if link.to_socket == material_output.inputs['Surface']) 
                active_link = material_output.inputs['Surface'].links[0]   
                metallic_socket = active_link.from_node.inputs['Metallic']

                diffuse_shader = nodes.new(type='ShaderNodeBsdfDiffuse')

                if metallic_socket:
                    if metallic_socket.is_linked:
                        metallic_value_socket = metallic_socket.links[0].from_socket
                        links.new(metallic_value_socket, diffuse_shader.inputs['Color'], True)
                    else:
                        diffuse_shader.inputs['Color'].default_value = (metallic_socket.default_value, metallic_socket.default_value, metallic_socket.default_value, 1)

                links.new(diffuse_shader.outputs[0], material_output.inputs[0], verify_limits = True)        


            bpy.context.scene.cycles.samples = context.scene.samplesMetallic
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.context.scene.render.bake.use_pass_color = True

            bpy.ops.object.bake(type='DIFFUSE', use_clear=True, use_selected_to_active=not solo_bake)

            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_metallic.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()

            for i, mslot in enumerate(bakeSource.material_slots):
                mslot.material = old_materials[i] 

            for mat in new_materials:
                bpy.data.materials.remove(mat)

     




        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.images.remove(bakeimage) 
        bpy.data.scenes[bpy.context.scene.name].render.engine = orig_renderer

        #reload all textures
        for image in bpy.data.images:
            image.reload()


        return {'FINISHED'}














def register():
    bpy.utils.register_class(EasyBake)
    bpy.utils.register_class(EasyBakeUIPanel)


    bpy.types.Scene.base = bpy.props.StringProperty (
        name = "base",
        default = "base",
        description = "base object",
        )


    bpy.types.Scene.bakeSource = bpy.props.StringProperty (
        name = "bakeSource",
        default = "bakeSource",
        description = "bakeSource object",
        )

    bpy.types.Scene.bakeNormal = bpy.props.BoolProperty (
        name = "bakeNormal",
        default = False,
        description = "Bake Tangent Space Normal Map",
        )
    bpy.types.Scene.bakeObject = bpy.props.BoolProperty (
        name = "bakeObject",
        default = False,
        description = "Bake Object Space Normal Map",
        )
    bpy.types.Scene.bakeAO = bpy.props.BoolProperty (
        name = "bakeAO",
        default = False,
        description = "Bake Ambient Occlusion Map",
        )
    bpy.types.Scene.bakeColor = bpy.props.BoolProperty (
        name = "bakeColor",
        default = False,
        description = "Bake Albedo Color Map",
        )
    bpy.types.Scene.bakeRoughness = bpy.props.BoolProperty (
        name = "bakeRoughness",
        default = False,
        description = "Bake Roughness Map",
        )
    bpy.types.Scene.bakeMetallic = bpy.props.BoolProperty (
        name = "bakeMetallic",
        default = False,
        description = "Bake Metallic Map",
        )        
    
    bpy.types.Scene.bakeUV = bpy.props.BoolProperty (
        name = "bakeUV",
        default = False,
        description = "Bake UV Wireframe Snapshot of base Mesh",
        )
    bpy.types.Scene.samplesNormal = bpy.props.IntProperty (
        name = "samplesNormal",
        default = 8,
        description = "Tangent Space Normal Map Sample Count",
        )
    bpy.types.Scene.samplesObject = bpy.props.IntProperty (
        name = "samplesObject",
        default = 8,
        description = "Object Space Normal Map Sample Count",
        )
    bpy.types.Scene.samplesAO = bpy.props.IntProperty (
        name = "samplesAO",
        default = 128,
        description = "Ambient Occlusion Map Sample Count",
        )
    bpy.types.Scene.samplesColor = bpy.props.IntProperty (
        name = "samplesColor",
        default = 1,
        description = "Color Map Sample Count",
        )
    bpy.types.Scene.samplesRoughness = bpy.props.IntProperty (
        name = "samplesRoughness",
        default = 1,
        description = "Roughness Map Sample Count",
        )
    bpy.types.Scene.samplesMetallic = bpy.props.IntProperty (
        name = "samplesMetallic",
        default = 1,
        description = "Metallic Map Sample Count",
        )


    bpy.types.Scene.bakeWidth = bpy.props.IntProperty (
        name = "bakeWidth",
        default = 512,
        description = "Export Texture Width",
        )  
    bpy.types.Scene.bakeHeight = bpy.props.IntProperty (
        name = "bakeHeight",
        default = 512,
        description = "Export Texture Height",
        )
    bpy.types.Scene.bakePrefix = bpy.props.StringProperty (
        name = "bakePrefix",
        default = "export",
        description = "export filename",
        )
    bpy.types.Scene.bakeFolder = bpy.props.StringProperty (
        name = "bakeFolder",
        default = "C:\\export",
        description = "destination folder",
        subtype = 'DIR_PATH'
        )

    bpy.types.Scene.UseLowOnly = bpy.props.BoolProperty (
        name = "UseLowOnly",
        default = False,
        description = "Only bake base on itself",
        )

def unregister():
    bpy.utils.unregister_class(EasyBake)
    bpy.utils.unregister_class(EasyBakeUIPanel)


    del bpy.types.Scene.bakeMetallic
    del bpy.types.Scene.base
    del bpy.types.Scene.bakeSource
    del bpy.types.Scene.bakeNormal
    del bpy.types.Scene.bakeObject
    del bpy.types.Scene.bakeAO
    del bpy.types.Scene.bakeColor
    del bpy.types.Scene.bakeRoughness
    del bpy.types.Scene.bakeUV
    del bpy.types.Scene.samplesNormal
    del bpy.types.Scene.samplesAO
    del bpy.types.Scene.samplesColor
    del bpy.types.Scene.samplesRoughness
    del bpy.types.Scene.samplesObject
    del bpy.types.Scene.bakeWidth
    del bpy.types.Scene.bakeHeight
    del bpy.types.Scene.bakeFolder
    del bpy.types.Scene.UseLowOnly
    
if __name__ == "__main__":
    register()
