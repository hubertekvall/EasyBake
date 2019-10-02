# Purpose of Fork

The intent of this fork is to add support for baking of metallicness. Currently there's no native support for baking metallicness in Blender, even worse when doing the color baking of a material metallic colors will not show up. This might be technically correct since metals lack diffuse and are all specular, but in a metallic workflow this is a burden since we often want color in our workflow to create gold, bronze, copper, etc. 

As a bonus this fork also implements an emission baking pass.


# EasyBake
Texture baking UI for Blender that lives in the 3D Viewport.
Small but powerful! Fast one-click baking and iteration.

Gas canister asset example, all maps baked using EasyBake:
![screenshot](http://www.brameulaers.net/blender/addons/github_images/easybake_example.jpg)

**instructions:**

1. put EasyBake.py in your addon folder
2. install add-on in user preferences (look for EasyBake)
3. you can find the UI under the "bake" tab in the tools UI (top right in the 3D viewport)

UI functions:

![UI screenshot](http://www.brameulaers.net/blender/addons/github_images/easybake_instructions.png)

**currently supports:**

- tangent normals
- object normals
- color
- roughness
- occlusion
- uv wireframe

**future plans:**

- metalness map (once this is bakeable in 2.8)
- position map 
