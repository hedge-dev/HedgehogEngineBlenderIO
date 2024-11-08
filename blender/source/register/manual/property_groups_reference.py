raw_mapping = [

]

manual_mapping = []
for raw in raw_mapping:
    manual_mapping.append(("bpy.types.heio_" + raw[0].lower() + "*", raw[1]))