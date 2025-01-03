import gpu


class CollisionMeshShaders:

    DONT_REGISTER_CLASS = True

    @classmethod
    def _create_capsule_shader(cls):

        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.push_constant('MAT4', "ModelViewProjectionMatrix")
        shader_info.push_constant('FLOAT', "radius")
        shader_info.push_constant('FLOAT', "height")
        shader_info.push_constant('BOOL', "srgbTarget")
        shader_info.push_constant('VEC4', "color")
        shader_info.vertex_in(0, 'VEC3', "pos")
        shader_info.fragment_out(0, 'VEC4', "fragColor")

        shader_info.vertex_source(
            """
            void main()
            {
                vec3 position = pos;
                float offset = position.z > 0 ? -1 : 1;
                position.z += offset;
                position *= radius;
                position.z -= offset * height;

                gl_Position = ModelViewProjectionMatrix * vec4(position, 1.0f);
            }
            """
        )

        shader_info.fragment_source(
            """
            vec4 blender_srgb_to_framebuffer_space(vec4 in_color)
            {
                if (srgbTarget) {
                    vec3 c = max(in_color.rgb, vec3(0.0));
                    vec3 c1 = c * (1.0 / 12.92);
                    vec3 c2 = pow((c + 0.055) * (1.0 / 1.055), vec3(2.4));
                    in_color.rgb = mix(c1, c2, step(vec3(0.04045), c));
                }
                return in_color;
            }

            void main()
            {
                fragColor = blender_srgb_to_framebuffer_space(color);
            }
            """
        )

        result = gpu.shader.create_from_info(shader_info)
        del shader_info

        return result

    @classmethod
    def register(cls):
        cls.capsule_shader = cls._create_capsule_shader()
