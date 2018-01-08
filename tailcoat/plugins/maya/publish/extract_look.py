import pyblish.api


class ExtractLook(pyblish.api.InstancePlugin):
    """Export shaders for rendering

    Shaders are associated with an "modelID" attribute on
    each *transform* node.
    The extracted file is then given the name of the shader,
    and thereafter a relationship is created between a mesh
    and a file on disk.

    """

    label = "Extract Look"
    order = pyblish.api.ExtractorOrder
    families = ["tailcoat.look"]
    hosts = ["maya"]

    def process(self, instance):
        import os
        import json
        from maya import cmds
        from jiminy import lib
        from tailcoat import utils, pipeline

        template_data = {
            "publish": pipeline.publish_repo(),
            "silo": instance.data["silo"],
            "asset": instance.data["asset"],
            "subset": instance.data["subset"],
            "representation": ".json",
        }

        template_publish = pipeline.publish_template()

        path = template_publish.format(**template_data)
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)

        self.log.info("Serialising shaders..")
        relationships = utils.serialise_shaders(instance)

        self.log.info("Extracting serialisation..")
        with open(path, "w") as f:
            json.dump(
                relationships,
                f,

                # This makes the output human-readable,
                # by padding lines to look visually pleasing.
                indent=4
            )

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)

        # Write individual shaders
        # TODO(marcus): How about exporting 1 scene, and
        # maintaining a reference to the shader node name,
        # as opposed to the file?
        self.log.info("Extracting shaders..")
        template_data = {
            "publish": pipeline.publish_repo(),
            "silo": instance.data["silo"],
            "asset": instance.data["asset"],
            "subset": instance.data["subset"],
            "representation": ".json",
        }

        template_publish = pipeline.publish_template()

        path = template_publish.format(**template_data)
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)

        with lib.maintained_selection(), lib.without_extension():
            cmds.select(relationships.keys(), replace=True, noExpand=True)
            cmds.file(path,
                      force=True,
                      options="v=0;",
                      type="mayaAscii",
                      preserveReferences=False,
                      exportSelected=True,
                      constructionHistory=False)

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {path}".format(**locals()))
