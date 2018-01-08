import pyblish.api
from maya import cmds


class SelectDuplicated(pyblish.api.Action):
    label = "Duplicated Name"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):
        cmds.select(plugin.duplicated)


class ValidateUniqueName(pyblish.api.InstancePlugin):
    """
    """
    label = "Unique Name"
    families = [
        "tailcoat.model",
        "tailcoat.rig",
    ]
    order = pyblish.api.ValidatorOrder
    host = ["maya"]
    actions = [
        pyblish.api.Category("Select"),
        SelectDuplicated,
    ]

    duplicated = []

    def process(self, instance):
        short_name = cmds.ls(instance)
        self.duplicated.extend([node for node in short_name if "|" in node])

        if self.duplicated:
            raise Exception("Duplicated node name found.")
