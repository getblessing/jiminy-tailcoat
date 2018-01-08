import pyblish.api
from maya import cmds


class FreezeTransform(pyblish.api.Action):
    label = "Freeze Transform"
    on = "failed"

    def process(self, context, plugin):
        cmds.makeIdentity(plugin.unfreezed, apply=True)


class SelectUnfreezed(pyblish.api.Action):
    label = "Select Unfreezed"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):
        cmds.select(plugin.unfreezed)


class ValidateTransformFreezed(pyblish.api.InstancePlugin):

    label = "Transform Freezed"
    order = pyblish.api.ValidatorOrder
    families = [
        "tailcoat.model",
        "tailcoat.rig",
    ]
    host = ["maya"]
    actions = [
        pyblish.api.Category("Select"),
        SelectUnfreezed,
        pyblish.api.Category("Fix It"),
        FreezeTransform,
    ]

    unfreezed = []

    def process(self, instance):

        transform_attrs = {
            ".translate": [(0.0, 0.0, 0.0)],
            ".rotate": [(0.0, 0.0, 0.0)],
            ".scale": [(1.0, 1.0, 1.0)],
            ".shear": [(0.0, 0.0, 0.0)]
        }

        for transform in cmds.ls(instance, type="transform"):
            has_freeze = (
                all([cmds.getAttr(transform + attr) == transform_attrs[attr]
                    for attr in transform_attrs.keys()])
            )

            if not has_freeze:
                self.unfreezed.append(transform)

        if self.unfreezed:
            raise Exception("Unfreezed transform found.")
