import os
import logging

from pyblish import api as pyblish
from avalon import api as avalon
from tailcoat import utils
from maya import cmds, mel

from . import menu

log = logging.getLogger(__name__)


PACKAGE_DIR = os.path.dirname(__file__)
PLUGINS_DIR = os.path.join(PACKAGE_DIR, "plugins")

PUBLISH_PATH = os.path.join(PLUGINS_DIR, "maya", "publish")
LOAD_PATH = os.path.join(PLUGINS_DIR, "maya", "load")
CREATE_PATH = os.path.join(PLUGINS_DIR, "maya", "create")


def install():
    log.info("Dress on.")
    # install pipeline menu
    menu.install()
    # install pipeline plugins
    pyblish.register_plugin_path(PUBLISH_PATH)
    avalon.register_plugin_path(avalon.Loader, LOAD_PATH)
    avalon.register_plugin_path(avalon.Creator, CREATE_PATH)

    # install callbacks
    log.info("Installing callbacks ... ")
    avalon.on("init", on_init)
    avalon.on("new", on_new)
    avalon.on("save", on_save)

    # Temporarily workaround
    # script node: uiConfigurationScriptNode
    mel.eval("global proc CgAbBlastPanelOptChangeCallback(string $pass){}")
    log.info("Unknown proc <CgAbBlastPanelOptChangeCallback> "
             "workaround init.")
    # Load Alembic
    cmds.loadPlugin("AbcExport.mll", quiet=True)
    cmds.loadPlugin("AbcImport.mll", quiet=True)


def uninstall():
    log.info("Dress off.")
    # uninstall pipeline menu
    menu.uninstall()
    # uninstall pipeline plugins
    pyblish.deregister_plugin_path(PUBLISH_PATH)
    avalon.deregister_plugin_path(avalon.Loader, LOAD_PATH)
    avalon.deregister_plugin_path(avalon.Creator, CREATE_PATH)


def on_init(_):
    log.info("Running callback on init..")


def on_new(_):
    log.info("Running callback on new..")


def on_save(_):
    """Automatically add IDs to new nodes

    Any transform of a mesh, without an exising ID,
    is given one automatically on file save.

    """
    log.info("Running callback on save..")
    utils.set_model_uuid()
