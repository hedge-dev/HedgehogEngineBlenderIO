from . import (
    property_groups_reference,
    operator_references
)

MANUAL_PREFIX = "https://hedge-dev.github.io/HedgehogEngineBlenderIO"
manual_mapping = []

manual_mapping.extend(property_groups_reference.manual_mapping)
manual_mapping.extend(operator_references.manual_mapping)


def add_manual_map():
    return MANUAL_PREFIX, manual_mapping
