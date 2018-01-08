import pyblish.api
from maya import cmds


class SelectKeyObject(pyblish.api.Action):
    """
    if family is "rig", select Driver object
    if not, select Driven(nodes reciving animCurve output)
    """
    label = "Driver/Driven"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):
        if "tailcoat.rig" not in plugin.instance_type:
            attrib = ".output"
        else:
            attrib = ".input"
        cmds.select(clear=True)
        for animCurve in plugin.animCurves:
            node = cmds.listConnections(animCurve + attrib)
            cmds.select(node, add=True)


class DeleteAnimCurves(pyblish.api.Action):
    label = "Delete Key"
    on = "failed"

    def process(self, context, plugin):
        cmds.delete(plugin.animCurves)


class ValidateKeyframeClean(pyblish.api.InstancePlugin):
    """Check keyframe existence
    Model should not have any keyframe,
    Rig can keep the drivenKey
    """
    label = "Keyframe Clean"
    families = [
        "tailcoat.model",
        "tailcoat.rig",
    ]
    order = pyblish.api.ValidatorOrder
    host = ["maya"]
    actions = [
        pyblish.api.Category("Select"),
        SelectKeyObject,
        pyblish.api.Category("Fix It"),
        DeleteAnimCurves,
    ]

    animCurves = []
    instance_type = []

    def process(self, instance):

        self.animCurves[:] = cmds.ls(type="animCurve")
        self.instance_type[:] = [instance.data["family"]]

        if self.animCurves:
            if "rig" not in self.instance_type[0]:
                raise Exception(
                    "%s should not have Keyframe." % self.instance_type[0])

            else:
                # rig can have drivenKey
                for animCurve in self.animCurves:
                    if cmds.listConnections(animCurve + ".input"):
                        self.animCurves.remove(animCurve)
                if self.animCurves:
                    raise Exception(
                        "%s should not have Keyframe." % self.instance_type[0])
