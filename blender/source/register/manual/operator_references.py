raw_mapping = [

]

manual_mapping = []
for raw in raw_mapping:
    manual_mapping.append(("bpy.ops." + raw[0].bl_idname + "*", raw[1]))