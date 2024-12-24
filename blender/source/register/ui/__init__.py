from . import (
    sca_parameter_panel,
    scene_panel,
    mesh_panel,
    material_panel,
    menus,
    viewport_toolbar
)

to_register = [
    sca_parameter_panel.HEIO_UL_SCAParameterList,

    scene_panel.HEIO_PT_Scene,

    mesh_panel.HEIO_UL_Layers,
    mesh_panel.HEIO_MT_LayersContextMenu,
    mesh_panel.HEIO_UL_Meshgroups,
    mesh_panel.HEIO_MT_MeshgroupsContextMenu,
    mesh_panel.HEIO_PT_Mesh,

    material_panel.HEIO_UL_ParameterList,
    material_panel.HEIO_UL_CustomParameterList,
    material_panel.HEIO_UL_TextureList,
    material_panel.HEIO_UL_CustomTextureList,
    material_panel.HEIO_PT_Material,

    menus.TOPBAR_MT_HEIO_Export,
    menus.TOPBAR_MT_HEIO_Import,
    menus.NativeHooks,

    viewport_toolbar.HEIO_PT_VTP_Material,
    viewport_toolbar.HEIO_PT_VTP_Info
]