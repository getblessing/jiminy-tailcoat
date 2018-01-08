import pyblish.api


class ExtractModel(pyblish.api.InstancePlugin):
    """Produce a stripped down Maya file from instance

    This plug-in takes into account only nodes relevant to models
    and discards anything else, especially deformers along with
    their intermediate nodes.

    """

    families = ["tailcoat.model"]
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    label = "Extract Model"

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
            "representation": ".mb",
        }

        template_publish = pipeline.publish_template()

        path = template_publish.format(**template_data)
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)

        # Perform extraction
        self.log.info("Performing extraction..")
        with capsule.no_display_layers(instance):
            with capsule.no_smooth_preview():
                with capsule.assign_shader(
                    cmds.ls(instance, type="mesh", long=True),
                    shadingEngine="initialShadingGroup"
                ):
                    with lib.maintained_selection(), lib.without_extension():
                        self.log.info(
                            "Extracting %s" % instance.data["name"])
                        cmds.select(instance, noExpand=True)
                        cmds.file(
                            path,
                            force=True,
                            typ="mayaBinary",
                            exportSelected=True,
                            preserveReferences=False,
                            # Shader assignment is the responsibility of
                            # riggers, for animators, and lookdev, for
                            # rendering.
                            shader=False,
                            # Construction history inherited from
                            # collection.
                            # This enables a selective export of nodes
                            # relevant to this particular plug-in.
                            constructionHistory=False
                        )

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {path}".format(**locals()))
