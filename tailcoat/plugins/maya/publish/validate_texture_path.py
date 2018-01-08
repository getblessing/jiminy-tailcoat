import pyblish.api
from maya import cmds


class SelectInvalidFileNode(pyblish.api.Action):
    label = "Local File Nodes"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):
        cmds.select(plugin.invalid_files)


class ValidateTexturePath(pyblish.api.InstancePlugin):
    """Check Texture File Path is not in C: or D: drive
    """

    label = "Texture Path"
    families = ["tailcoat.look"]
    order = pyblish.api.ValidatorOrder
    host = ["maya"]
    actions = [
        pyblish.api.Category("Select"),
        SelectInvalidFileNode,
    ]

    invalid_files = []

    def process(self, instance):
        shading_engines = []
        file_textures = []

        for obj in instance:
            shading_engines.extend(
                cmds.listSets(
                    object=obj,
                    extendToShape=True,
                    type=1
                ) or []
            )

        shading_engines = list(set(shading_engines))

        while True:
            nodes = cmds.listConnections(
                shading_engines,
                destination=False,
                source=True,
                skipConversionNodes=True,
                shapes=False
            )
            file_textures.extend(cmds.ls(nodes, type="file"))
            if not nodes:
                break

        file_textures = list(set(file_textures))

        for node in file_textures:
            img_path = cmds.getAttr(node + ".fileTextureName")
            if img_path[:2] in ["C:", "D:"]:
                self.invalid_files.append(node)

        assert not self.invalid_files, (
            "Texture files should not be in local drive (C:, D:).")
