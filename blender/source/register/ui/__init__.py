from . import (
    material_panel,
    viewport_toolbar
)

to_register = [
    material_panel.HEIO_UL_ParameterList,
    material_panel.HEIO_UL_CustomParameterList,
	material_panel.HEIO_UL_TextureList,
    material_panel.HEIO_UL_CustomTextureList,
    material_panel.HEIO_PT_Material,

    viewport_toolbar.HEIO_PT_VTP_Info
]
