import pyblish.api
from maya import cmds


class SelectMultipleShapes(pyblish.api.Action):
    label = "Multiple Shapes"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):
        cmds.select(plugin.has_multiple_shapes)


class ValidateSingleShape(pyblish.api.InstancePlugin):
    """Transforms with a mesh must ever only contain a single mesh

    This ensures models only contain a single shape node.

    """

    label = "Single Shape"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["tailcoat.model"]
    actions = [
        pyblish.api.Category("Select"),
        SelectMultipleShapes,
    ]

    has_multiple_shapes = []

    def process(self, instance):
        # Consider only nodes of type="mesh"
        meshes = cmds.ls(instance, type="mesh", long=True)
        transforms = cmds.listRelatives(meshes, parent=True, fullPath=True)

        for transform in set(transforms):
            shapes = cmds.listRelatives(transform,
                                        shapes=True,
                                        fullPath=True) or []
            # Ensure the one child is a shape
            has_single_shape = len(shapes) == 1

            # Ensure the one shape is of type "mesh"
            has_single_mesh = (
                has_single_shape and
                cmds.nodeType(shapes[0]) == "mesh"
            )

            if not all([has_single_shape, has_single_mesh]):
                self.has_multiple_shapes.append(transform)

        assert not self.has_multiple_shapes, (
            "\"%s\" has transforms with multiple shapes: %s" % (
                instance.data["name"],
                ", ".join(self.has_multiple_shapes)
            )
        )
