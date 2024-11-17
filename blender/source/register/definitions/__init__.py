from . import (
	shader_definitions,
	sca_parameter_definitions
)

def load_definitions():
	shader_definitions.load_shader_definitions()
	sca_parameter_definitions.load_sca_parameter_definitions()