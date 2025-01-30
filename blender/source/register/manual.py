import bpy
import inspect

TYPE_PAGE_MAP = {
    "HEIO_SCA_Parameter": "object/sca_parameters",
    "HEIO_SCA_Parameters": "object/sca_parameters",
    "HEIO_SCAP_MassEdit": "tools/viewport_toolbar/sca_editor",
    "HEIO_LODInfoLevel": "object/lod_info",
    "HEIO_LODInfoLevelList": "object/lod_info",
    "HEIO_LODInfo": "object/lod_info",
    "HEIO_Scene": "settings",
    "HEIO_Armature": "object/lod_info",
    "HEIO_Node": "object/sca_parameters",
    "HEIO_RenderLayer": "object/mesh/render_layers",
    "HEIO_RenderLayerList": "object/mesh/render_layers",
    "HEIO_CollisionLayer": "object/mesh/groups",
    "HEIO_CollisionType": "object/mesh/collision_types",
    "HEIO_CollisionTypeList": "object/mesh/collision_types",
    "HEIO_CollisionFlag": "object/mesh/collision_flags",
    "HEIO_CollisionFlagList": "object/mesh/collision_flags",
    "HEIO_MeshGroup": "object/mesh/groups",
    "HEIO_MeshGroupList": "object/mesh/groups",
    "HEIO_CollisionPrimitive": "object/mesh/collision_primitives",
    "HEIO_CollisionPrimitiveList": "object/mesh/collision_primitives",
    "HEIO_Mesh": "object/mesh/export_settings",
    "HEIO_MaterialParameter": "object/material_parameters",
    "HEIO_MaterialParameterList": "object/material_parameters",
    "HEIO_MaterialTexture": "object/material_textures",
    "HEIO_MaterialTextureList": "object/material_textures",
    "HEIO_Material": "object/material",
    # "HEIO_Image": "", # internal data only, nothing to document
    "HEIO_View3DOverlay_CollisionPrimitive": "tools/collision_primitive_overlay"
}

OPS_PAGE_MAP = {
    "heio.import_material": "tools/importers",
    "heio.import_material_active": "tools/importers",
    "heio.import_material_active_if": "tools/importers",
    "heio.import_model": "tools/importers",
    "heio.import_terrainmodel": "tools/importers",
    "heio.import_collisionmesh": "tools/importers",
    "heio.import_pointcloud": "tools/importers",
    "heio.export_material": "tools/exporters",
    "heio.export_material_active": "tools/exporters",
    "heio.export_model": "tools/exporters",
    "heio.export_terrainmodel": "tools/exporters",
    "heio.export_collisionmesh": "tools/exporters",
    "heio.export_pointcloud": "tools/exporters",
    "heio.export_pointclouds": "tools/exporters",
    "heio.sca_parameters_add": "object/sca_parameters",
    "heio.sca_parameters_remove": "object/sca_parameters",
    "heio.sca_parameters_move": "object/sca_parameters",
    "heio.sca_parameters_newfrompreset": "object/sca_parameters",
    "heio.lod_info_initialize": "object/lod_info",
    "heio.lod_info_delete": "object/lod_info",
    "heio.lod_info_add": "object/lod_info",
    "heio.lod_info_remove": "object/lod_info",
    "heio.lod_info_move": "object/lod_info",
    "heio.mesh_info_initialize": "object/mesh/index",
    "heio.mesh_info_delete": "object/mesh/index",
    "heio.mesh_info_assign": "object/mesh/index",
    "heio.collision_flag_remove": "object/mesh/index",
    "heio.mesh_info_de_select": "object/mesh/index",
    "heio.mesh_info_add": "object/mesh/index",
    "heio.mesh_info_remove": "object/mesh/index",
    "heio.mesh_info_move": "object/mesh/index",
    "heio.material_setup_nodes": "viewport_toolbar/general.html",
    "heio.material_setup_nodes_active": "viewport_toolbar/general.html",
    "heio.material_parameters_add": "",
    "heio.material_parameters_remove": "",
    "heio.material_parameters_move": "",
    "heio.split_meshgroups": "viewport_toolbar/general.html",
    "heio.merge_submeshes": "viewport_toolbar/general.html",
    "heio.collision_primitives_to_geometry": "viewport_toolbar/general.html",
    "heio.reimport_images": "viewport_toolbar/general.html",
    "heio.scap_massedit_select": "tools/viewport_toolbar/sca_editor",
    "heio.scap_massedit_set": "tools/viewport_toolbar/sca_editor",
    "heio.scap_massedit_remove": "tools/viewport_toolbar/sca_editor",
    "heio.info_manual": "tools/viewport_toolbar/info",
    "heio.info_discord": "tools/viewport_toolbar/info",
    "heio.info_report": "tools/viewport_toolbar/info",
    "heio.info_dds_addon": "tools/viewport_toolbar/info",
    # "heio.collision_primitive_gizmo_clicked": "",
    # "heio.collision_primitive_move": "",
    # "heio.collision_primitive_rotate": "",
    # "heio.collision_primitive_viewrotate": "",
    # "heio.collision_primitive_scale": "",
    # "heio.snap_active_collision_primitive_to_cursor": "",
    # "heio.snap_cursor_to_active_collision_primitive": "",
}

def _to_link(path: str, dir: str):
    return "/user_interface/" + dir + ".html#" + path.replace(".", "-").replace("_", "-")


def get_mapping(classes):

    mapping = [
        ("bpy.types.HEIO_Scene.show_all_shaders*", _to_link("bpy.types.HEIO_Scene.show_all_shaders", "object/material"))
    ]

    for cls in classes:
        if issubclass(cls, bpy.types.Operator):
            path = "bpy.ops." + cls.bl_idname
            page_mapping = OPS_PAGE_MAP.get(cls.bl_idname, None)
        elif issubclass(cls, bpy.types.PropertyGroup):
            path = "bpy.types." + cls.__name__
            page_mapping = TYPE_PAGE_MAP.get(cls.__name__, None)
        else:
            continue

        if page_mapping is None:
            continue

        page = _to_link(path, page_mapping)

        annotations = inspect.get_annotations(cls)
        for name in annotations.keys():
            mapping.append((
                (path + "." + name + "*").lower(),
                page + "-" + name.replace("_", "-")))

        mapping.append((
            (path + "*").lower(),
            page))

    return mapping
