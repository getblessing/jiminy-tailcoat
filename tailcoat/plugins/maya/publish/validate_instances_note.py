import pyblish.api
from maya import cmds


class ValidateInstancesNote(pyblish.api.InstancePlugin):
    """Validate Notes
    Check if there have some notes
    """

    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    label = "Check Note"

    def process(self, instance):
        assembly = instance.data["assembly"]
        if assembly:
            try:
                notes = cmds.getAttr(assembly + ".notes")
            except ValueError:
                notes = ""
            if not notes:
                self.log.warning("Did not found notes. Better write some.")
        else:
            raise Exception("No assembly found.")
