import pyblish.api


class ValidateSingleAssembly(pyblish.api.InstancePlugin):
    """Single Assembly

    Must have one top group node
    """

    label = "Single Assembly"
    order = pyblish.api.ValidatorOrder - 0.2
    hosts = ["maya"]

    def process(self, instance):
        from maya import cmds

        instance.data["assembly"] = ""

        assemblies = cmds.ls(instance, assemblies=True)
        assert len(assemblies) == 1, (
            "Must have a single parent transform node.")
