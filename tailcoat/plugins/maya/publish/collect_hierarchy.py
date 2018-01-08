import pyblish.api
from maya import cmds


class CollectHierarchy(pyblish.api.InstancePlugin):
    """Collect Model for model validation
    """

    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    label = "Collect Hierarchy"

    def process(self, instance):
        instance += cmds.listRelatives(instance,
                                       allDescendents=True,
                                       fullPath=True) or []
