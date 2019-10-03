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
        
        
        
        # box = layout.box()

        # col = box.column(align=True)

        # row = col.row(align = True)
        # row.prop_search(context.scene, "base", context.scene, "objects", text="", icon="MESH_ICOSPHERE")
        
        
        
        # row = col.row(align = True)
        # row.prop_search(context.scene, "bakeSource", context.scene, "objects", text="", icon="MESH_UVSPHERE")
        # row.enabled = not context.scene.UseLowOnly
        
        

        

 
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
        if context.scene.bakeRoughness:
            row.prop(context.scene, "bakeMetallic", text="")
            

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
        bakeSource = {}
        base = {}

        if selection_count <= 0:
            base = bpy.context.active_object

            if selection_count == 1:
                solo_bake = True

            if selection_count == 2:
                bakeSource = any(bs for bs in bpy.context.selected_objects if bs != base)

            else:
                self.report({'WARNING'}, "Too many objects selected! Max two!")
                return {'FINISHED'}       

        else:
            self.report({'WARNING'}, "Select your objects to bake first!")    
            return {'FINISHED'}  



        
    #2 make sure we are in object mode and nothing is selected
        if bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

    #5 remember render engine and switch to CYCLES for baking
        orig_renderer = bpy.data.scenes[bpy.context.scene.name].render.engine
        bpy.data.scenes[bpy.context.scene.name].render.engine = "CYCLES"

    #6 create temporary bake image and material
        
        bakeimage = bpy.data.images.new("BakeImage", width=context.scene.bakeWidth, height=context.scene.bakeHeight)
        bakemat = bpy.data.materials.new(name="bakemat")
        bakemat.use_nodes = True

        orig_mat = bpy.context.active_object.data.materials[0]
        bpy.context.active_object.data.materials[0] = bakemat
        node_tree = bakemat.node_tree
        node = node_tree.nodes.new("ShaderNodeTexImage")
        node.select = True
        node_tree.nodes.active = node
        node.image = bakeimage









    #11 bake all maps!
        if context.scene.bakeNormal:
            bpy.context.scene.cycles.samples = context.scene.samplesNormal
            bpy.ops.object.bake(type='NORMAL', use_clear=True, use_selected_to_active=True, normal_space='TANGENT')
            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_normal.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()
        
        if context.scene.bakeObject:
            bpy.context.scene.cycles.samples = context.scene.samplesObject
            bpy.ops.object.bake(type='NORMAL', use_clear=True, use_selected_to_active=True, normal_space='OBJECT')
            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_object.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()

        if context.scene.bakeAO:
            bpy.context.scene.cycles.samples = context.scene.samplesAO
            bpy.ops.object.bake(type='AO', use_clear=True, use_selected_to_active=not context.scene.UseLowOnly)
            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_ao.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()

        if context.scene.bakeColor:
            bpy.context.scene.cycles.samples = context.scene.samplesColor
            bpy.context.scene.render.bake.use_pass_direct = False
            bpy.context.scene.render.bake.use_pass_indirect = False
            bpy.context.scene.render.bake.use_pass_color = True
            bpy.ops.object.bake(type='DIFFUSE', use_clear=True, use_selected_to_active=True)
            bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_color.tga"
            bakeimage.file_format = 'TARGA'
            bakeimage.save()
        
        if context.scene.bakeRoughness:
            bpy.context.scene.cycles.samples = context.scene.samplesRoughness
            bpy.ops.object.bake(type='ROUGHNESS', use_clear=True, use_selected_to_active=True)
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


        # # Metallicness baking
        # if context.scene.bakeMetallic:
        #     materials = {}

        #     if context.scene.UseLowOnly:
        #         materials = context.scene.base.materials
        #     else
        #         materials = context.scene.bakeSource.materials    
                

            
        #     # Store old links so we can restore them after we're done
        #     oldLinks = {}

        #     # Store newly generated nodes so we can remove them afer we're done
        #     newNodes = {}

            
        #     # Go through every material 
        #     for mat in materials:
        #         nodeTree = mat.node_tree
        #         links = mat.node_tree.links
        #         nodes = mat.nodes
        #         outputNode = mat.nodes['Material Output']

        #         # Current link to material output
        #         active_link = next(l for l in links if l.to_socket == outputNode.inputs['Surface'])
                
        #         # If the material has a metallic property
        #         if active_link.from_node.name == 'Principled BSDF':                       
                    
        #             principledNode = active_link.from_node

        #             # Store old links by material
        #             oldLinks[mat].Append(active_link)

        #             # Remove current link
        #             links.remove(active_link)

        #             # Create new diffuse node (Easiest way to capture arbitrary data)
        #             newNodes[mat] = nodes.new(type='ShaderNodeDiffuse')

        #             # Find if the metallic property has a connection or is using the default value
        #             if principledNode.inputs['Metallic'].links:
                        
        #                 # Cache this link too so we can restore it later
        #                 oldLinks[mat].Append(principledNode.inputs['Metallic'].links[0])

        #                 # Connect whatever's in the Metallic slot to our new Diffuse color slot
        #                 links.new



        #     bpy.context.scene.cycles.samples = context.scene.samplesMetallic
        #     bpy.context.scene.render.bake.use_pass_direct = False
        #     bpy.context.scene.render.bake.use_pass_indirect = False
        #     bpy.context.scene.render.bake.use_pass_color = True

        #     bpy.ops.object.bake(type='DIFFUSE', use_clear=True, use_selected_to_active=not context.scene.UseLowOnly)

        #     bakeimage.filepath_raw = context.scene.bakeFolder+context.scene.bakePrefix+"_metallic.tga"
        #     bakeimage.file_format = 'TARGA'
        #     bakeimage.save()

            #for mat in context.scene.bakeSource.materials

            # Delete output replacement and reconnect the Principled BDRSF




        #cleanup temporary objects and materials
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.images.remove(bakeimage)
        bakemat.node_tree.nodes.remove(node)
        bpy.data.materials.remove(bakemat)
        bpy.context.active_object.data.materials[0] = orig_mat
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
