import bpy
import bmesh


def _process_attribute_if(
        context: bpy.types.Context,
        mesh: bpy.types.Mesh,
        attribute_name: str,
        get_func):

    if context is not None and context.mode == 'EDIT_MESH' and context.active_object.data == mesh:
        mesh = context.edit_object.data
        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int[attribute_name]

        for face in bm.faces:
            new_value = get_func(face[layer])
            if new_value is not None:
                face[layer] = new_value

        bmesh.update_edit_mesh(mesh)
    else:
        attribute: bpy.types.IntAttribute = mesh.attributes[attribute_name]

        for value in attribute.data:
            new_value = get_func(value.value)
            if new_value is not None:
                value.value = new_value


def _process_attribute(
        context: bpy.types.Context,
        mesh: bpy.types.Mesh,
        attribute_name: str,
        get_func):

    if context is not None and context.mode == 'EDIT_MESH' and context.active_object.data == mesh:
        mesh = context.edit_object.data
        bm = bmesh.from_edit_mesh(mesh)
        layer = bm.faces.layers.int[attribute_name]

        for face in bm.faces:
            face[layer] = get_func(face[layer])

        bmesh.update_edit_mesh(mesh)
    else:
        attribute: bpy.types.IntAttribute = mesh.attributes[attribute_name]

        for value in attribute.data:
            value.value = get_func(value.value)


def swap_int_values(
        context: bpy.types.Context,
        mesh: bpy.types.Mesh,
        attribute_name: str,
        a: int,
        b: int):

    _process_attribute_if(
        context,
        mesh,
        attribute_name,
        lambda x: b if x == a else (a if x == b else None)
    )


def change_int_values(
        context: bpy.types.Context,
        mesh: bpy.types.Mesh,
        attribute_name: str,
        from_value: int,
        to_value: int):

    _process_attribute_if(
        context,
        mesh,
        attribute_name,
        lambda x: to_value if x == from_value else None
    )


def decrease_int_values(
        context: bpy.types.Context,
        mesh: bpy.types.Mesh,
        attribute_name: str,
        threshold_value: int):

    _process_attribute_if(
        context,
        mesh,
        attribute_name,
        lambda x: x - 1 if x >= threshold_value else None
    )


def swap_int_flags(
        context: bpy.types.Context,
        mesh: bpy.types.Mesh,
        attribute_name: str,
        a: int,
        b: int):

    ab = a | b
    inv_a = ~a
    inv_b = ~b

    def swap(x):
        if (x & ab) == ab:
            return None
        elif (x & a) != 0:
            return (x & inv_a) | b
        elif (x & b) != 0:
            return (x & inv_b) | a

        return None

    _process_attribute_if(
        context,
        mesh,
        attribute_name,
        swap
    )


def change_int_flags(
        context: bpy.types.Context,
        mesh: bpy.types.Mesh,
        attribute_name: str,
        from_flag: int,
        to_flag: int):

    inv_from_flag = ~from_flag

    def change(x):
        if (x & from_flag) != 0:
            return (x & inv_from_flag) | to_flag
        return None

    _process_attribute_if(
        context,
        mesh,
        attribute_name,
        change
    )


def remove_int_flags(
        context: bpy.types.Context,
        mesh: bpy.types.Mesh,
        attribute_name: str,
        flag: int):

    inv_flag = ~flag

    _process_attribute(
        context,
        mesh,
        attribute_name,
        lambda x: x & inv_flag
    )


def rightshift_int_flags(
        context: bpy.types.Context,
        mesh: bpy.types.Mesh,
        attribute_name: str,
        bit_offset: int,
        bits_count: int):

    if bits_count == 0:
        return

    shift_mask = 0xFFFFFFFF << (bit_offset + bits_count)
    retain_mask = ~(0xFFFFFFFF << bit_offset)

    _process_attribute(
        context,
        mesh,
        attribute_name,
        lambda x: ((x & shift_mask) >> bits_count) | (x & retain_mask)
    )


class AttributeUtility:

    context: bpy.types.Context | None
    mesh: bpy.types.Mesh
    attribute_name: str

    def __init__(
            self,
            context: bpy.types.Context | None,
            mesh: bpy.types.Mesh,
            attribute_name: str):

        self.context = context
        self.mesh = mesh
        self.attribute_name = attribute_name

    def swap_int_values(
            self,
            a: int,
            b: int):

        swap_int_values(
            self.context,
            self.mesh,
            self.attribute_name,
            a,
            b
        )

    def change_int_values(
            self,
            from_value: int,
            to_value: int):

        change_int_values(
            self.context,
            self.mesh,
            self.attribute_name,
            from_value,
            to_value
        )

    def decrease_int_values(
            self,
            threshold_value: int):

        decrease_int_values(
            self.context,
            self.mesh,
            self.attribute_name,
            threshold_value
        )

    def swap_int_flags(
            self,
            a: int,
            b: int):

        swap_int_flags(
            self.context,
            self.mesh,
            self.attribute_name,
            a,
            b
        )

    def change_int_flags(
            self,
            from_flag: int,
            to_flag: int):

        change_int_flags(
            self.context,
            self.mesh,
            self.attribute_name,
            from_flag,
            to_flag
        )

    def remove_int_flags(
            self,
            flag: int):

        remove_int_flags(
            self.context,
            self.mesh,
            self.attribute_name,
            flag
        )

    def rightshift_int_flags(
            self,
            bit_offset: int,
            bits_count: int):

        rightshift_int_flags(
            self.context,
            self.mesh,
            self.attribute_name,
            bit_offset,
            bits_count
        )
