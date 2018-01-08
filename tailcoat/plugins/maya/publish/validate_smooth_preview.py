import pyblish.api
from maya import cmds


class SelectSmoothed(pyblish.api.Action):
    label = "Select Smoothed"
    on = "processed"
    icon = "hand-o-up"

    def process(self, context, plugin):
        cmds.select(plugin.smoothed)


class ValidateSmoothPreview(pyblish.api.InstancePlugin):
    """Emit Warning If There are any mesh has smooth preview"""

    families = ["tailcoat.model"]
    order = pyblish.api.ValidatorOrder + 0.45
    actions = [
        pyblish.api.Category("Select"),
        SelectSmoothed,
    ]
    hosts = ["maya"]
    label = "Smooth Preview"

    smoothed = []

    def process(self, instance):
        """Process all the nodes in the instance"""

        for mesh in cmds.ls(instance, type="mesh", long=True):
            if cmds.getAttr("{0}.displaySmoothMesh".format(mesh)):
                self.smoothed.append(mesh)

        if self.smoothed:
            self.log.warning("Smooth Preview found. Better turn off.")
