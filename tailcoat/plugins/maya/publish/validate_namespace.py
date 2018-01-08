import pyblish.api
from tailcoat import utils
from maya import cmds


class SelectNamespace(pyblish.api.Action):
    label = "Select Namespace"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):
        cmds.select(plugin.has_namespace)


class RemoveNamespace(pyblish.api.Action):
    label = "Remove Namespace"
    on = "failed"

    def process(self, context, plugin):
        utils.remove_namespace(plugin.has_namespace)


class ValidateNamespace(pyblish.api.InstancePlugin):
    """Ensure the nodes don't have a namespace"""

    families = [
        "tailcoat.model",
        "tailcoat.rig",
    ]
    order = pyblish.api.ValidatorOrder + 0.45
    hosts = ["maya"]
    label = "Namespaces"
    actions = [
        pyblish.api.Category("Select"),
        SelectNamespace,
        pyblish.api.Category("Fix It"),
        RemoveNamespace,
    ]

    has_namespace = []

    def process(self, instance):
        """Process all the nodes in the instance"""
        for node in instance:
            if get_namespace(node):
                self.has_namespace.append(node)

        if self.has_namespace:
            raise Exception("Namespaces found.")


def get_namespace(node_name):
    # ensure only node's name (not parent path)
    node_name = node_name.rsplit("|")[-1]
    # ensure only namespace
    return node_name.rpartition(":")[0]
