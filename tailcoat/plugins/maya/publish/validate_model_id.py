import pyblish.api
from tailcoat import utils


class RepairModelID(pyblish.api.Action):
    label = "Repair Model ID"
    on = "failed"

    def process(self, context, plugin):
        utils.set_model_uuid()


class ValidateModelID(pyblish.api.InstancePlugin):
    """All models must have an ID attribute"""

    label = "Model ID"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = [
        "tailcoat.model",
        "tailcoat.lookdev",
    ]
    actions = [
        pyblish.api.Category("Fix It"),
        RepairModelID,
    ]

    def process(self, instance):
        from maya import cmds

        missing = list()

        for node in instance:

            # Only check transforms with shapes that are meshes
            if not cmds.nodeType(node) == "transform":
                continue

            shapes = cmds.listRelatives(node,
                                        shapes=True,
                                        type="mesh",
                                        fullPath=True) or list()
            meshes = cmds.ls(shapes, type="mesh")

            if not meshes:
                continue

            try:
                cmds.getAttr(node + ".modelID")
            except ValueError:
                missing.append(node)

        assert not missing, ("Missing `modelID` attribute on: %s"
                             % ", ".join(missing))
