import pyblish.api
from maya import cmds


class SelectNormalsLocked(pyblish.api.Action):
    label = "Normals Locked"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):
        cmds.select(plugin.locked)


class UnlockNormals(pyblish.api.Action):
    label = "Unlock Normals"
    on = "failed"

    def process(self, context, plugin):
        cmds.polyNormalPerVertex(plugin.locked, unFreezeNormal=True)


class ValidateNormalsUnlocked(pyblish.api.InstancePlugin):
    """Normals of a model may not be locked

    Locked normals shading during interactive use to behave
    unexpectedly. No part of the pipeline take advantage of
    the ability to lock normals.

    """

    label = "Normals Unlocked"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["tailcoat.model"]
    actions = [
        pyblish.api.Category("Select"),
        SelectNormalsLocked,
        pyblish.api.Category("Fix It"),
        UnlockNormals,
    ]

    locked = []

    def process(self, instance):
        mesh_list = cmds.ls(instance,
                            type="mesh",
                            long=True,
                            noIntermediate=True)
        for mesh in mesh_list:
            faces = cmds.polyListComponentConversion(mesh, toVertexFace=True)
            locked = cmds.polyNormalPerVertex(faces,
                                              query=True,
                                              freezeNormal=True)

            self.locked.append(mesh) if any(locked) else None

        # On locked normals, indicate that validation has failed
        # with a friendly message for the user.
        assert not self.locked, (
            "Meshes found with locked normals: %s" % self.locked)

        self.log.info("The normals of \"%s\" are correct." % instance)
