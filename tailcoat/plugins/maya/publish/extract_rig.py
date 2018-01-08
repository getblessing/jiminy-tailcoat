import pyblish.api


class ExtractRig(pyblish.api.InstancePlugin):
    """Produce a stripped down Maya file from instance

    This plug-in takes into account only nodes relevant to models
    and discards anything else, especially deformers along with
    their intermediate nodes.

    """

    families = ["tailcoat.rig"]
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    label = "Extract Rig"

    def process(self, instance):
        import os
        from maya import cmds
        from jiminy import lib
        from tailcoat import pipeline
        from tailcoat.utils import capsule

        template_data = {
            "publish": pipeline.publish_repo(),
            "silo": instance.data["silo"],
            "asset": instance.data["asset"],
            "subset": instance.data["subset"],
            "representation": ".ma",
        }

        template_publish = pipeline.publish_template()

        path = template_publish.format(**template_data)
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)

        # Perform extraction
        self.log.info("Performing extraction..")
        with capsule.no_display_layers(instance):
            with capsule.no_smooth_preview():
                with lib.maintained_selection(), lib.without_extension():
                    self.log.info(
                        "Extracting %s" % instance.data["name"])
                    cmds.select(instance, noExpand=True)
                    cmds.file(
                        path,
                        force=True,
                        typ="mayaAscii",
                        exportSelected=True,
                        preserveReferences=False,
                        constructionHistory=True
                    )

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {path}".format(**locals()))
