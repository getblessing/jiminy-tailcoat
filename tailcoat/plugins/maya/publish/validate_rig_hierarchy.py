import pyblish.api


class ValidateRigHierarchy(pyblish.api.InstancePlugin):
    """A rig hierarchy must reside under a single assembly called "ROOT"

    - Must reside within `ROOT` transform

    """

    label = "Rig Format"
    order = pyblish.api.ValidatorOrder - 0.15
    hosts = ["maya"]
    families = ["tailcoat.rig"]

    def process(self, instance):
        from maya import cmds

        assemblies = cmds.ls(instance, assemblies=True)
        # compare with short name string, ensure unique
        assert assemblies == ["ROOT"], (
            "Rig must have a single parent called 'ROOT'.")

        instance.data["assembly"] = assemblies[0]
