import pyblish.api


class ValidateModelHierarchy(pyblish.api.InstancePlugin):
    """A model hierarchy must reside under a single assembly called "MODEL"

    - Must reside within `MODEL` transform

    """

    label = "Model Format"
    order = pyblish.api.ValidatorOrder - 0.15
    hosts = ["maya"]
    families = ["tailcoat.model"]

    def process(self, instance):
        from maya import cmds

        assemblies = cmds.ls(instance, assemblies=True)
        # compare with short name string, ensure unique
        assert assemblies == ["MODEL"], (
            "Model must have a single parent called 'MODEL'.")

        instance.data["assembly"] = assemblies[0]
