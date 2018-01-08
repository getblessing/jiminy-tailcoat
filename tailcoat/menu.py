import sys
import os
import logging
from maya import cmds
from jiminy.vendor.Qt import QtCore
from jiminy import api as jiminy
from . import pipeline


self = sys.modules[__name__]
self._menu = "jiminymaya"

log = logging.getLogger(__name__)

global SILO


def install():
    def deferred():

        cmds.menuItem(
            "Create Model",
            command=createModel,
            image="polyCube.svg",
            parent=self._menu,
        )

        cmds.menuItem(
            "Create Rig",
            command=createRig,
            image="joint.svg",
            parent=self._menu,
        )

        cmds.menuItem(
            "Create Look",
            command=createLook,
            image="shaderGlow.svg",
            parent=self._menu,
        )

        cmds.menuItem(divider=True, label="Project...")

        cmds.menuItem(
            "Link Global Project",
            command=link_global_project,
            image="SP_DirveNetIcon.png",
            parent=self._menu,
        )

    # Allow time for uninstallation to finish.
    QtCore.QTimer.singleShot(200, deferred)


def uninstall():
    pass


def link_global_project(*args):
    path = cmds.fileDialog2(
        cap="Select Global Project",
        fileMode=3,
        dialogStyle=2,
        okCaption="Link",
    )
    if os.path.isdir(path):
        # (TODO) if current workspace is at global project,
        # should not drop anchor
        with open(pipeline.project_anchor(), 'w') as anchor:
            anchor.write(path)
        os.makedirs(pipeline.publish_repo())


def _list_silo():
    root_repo = pipeline.publish_repo()
    if os.path.isdir(root_repo):
        for silo in os.listdir(root_repo):
            if os.path.isdir(os.path.join(root_repo, silo)):
                cmds.menuItem(label=silo, parent="jiminy_silo_menu")


def _list_asset(*args):
    silo = cmds.optionMenu("jiminy_silo_menu", q=True, value=True)
    if silo:
        silo_repo = os.path.join(pipeline.publish_repo(), silo)
        if os.path.isdir(silo_repo):
            _ = cmds.optionMenu("jiminy_asset_menu", q=True, itemListLong=True)
            for item in _ or []:
                cmds.deleteUI(item)
            for asset in os.listdir(silo_repo):
                if os.path.isdir(os.path.join(silo_repo, asset)):
                    cmds.menuItem(label=asset, parent="jiminy_asset_menu")


def _asset_naming_dialog(*args):
    # Get the dialog's formLayout.
    form = cmds.setParent(q=True)
    cmds.formLayout(form, e=True, width=260)

    silo_obj = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text("Silo : ", width=70, align="right")
    cmds.optionMenu("jiminy_silo_menu", changeCommand=_list_asset)
    _list_silo()
    cmds.setParent("..")

    asset_obj = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text("Asset : ", width=70, align="right")
    cmds.optionMenu("jiminy_asset_menu")
    _list_asset()
    cmds.setParent("..")

    ok_btn = cmds.button(
        label="OK",
        width=80,
        height=30,
        command=(
            'cmds.layoutDialog('
            'dismiss=('
            'cmds.optionMenu("jiminy_asset_menu", q=True, value=True) +'
            '"." +'
            'cmds.optionMenu("jiminy_silo_menu", q=True, value=True)'
            '))')
    )

    no_btn = cmds.button(
        label="Cancel",
        width=80,
        height=30,
        command='cmds.layoutDialog(dismiss="dismiss")'
    )

    cmds.formLayout(
        form,
        edit=True,
        attachForm=[
            (silo_obj, "top", 10),
            (silo_obj, "left", 5),
            (silo_obj, "right", 5),
            (asset_obj, "left", 5),
            (asset_obj, "right", 5),
            (ok_btn, "left", 5),
            (no_btn, "right", 5)
        ],
        attachControl=[
            (asset_obj, "top", 10, silo_obj),
            (ok_btn, "top", 16, asset_obj),
            (no_btn, "top", 16, asset_obj)
        ],
        attachPosition=[
            (ok_btn, 'right', 5, 50),
            (no_btn, 'left', 5, 50),
            (ok_btn, "bottom", 5, 97),
            (no_btn, "bottom", 5, 97)
        ]
    )


def _create_registered_asset():
    while True:
        result = cmds.layoutDialog(ui=_asset_naming_dialog).strip()
        if not result or result == "dismiss":
            return "", ""
        else:
            return result.split(".")


def createModel(*args):
    asset, silo = _create_registered_asset()
    if asset and silo:
        jiminy.create(
            "ModelDefault", asset, "tailcoat.model",
            options=None, data={"silo": silo}
        )


def createRig(*args):
    asset, silo = _create_registered_asset()
    if asset and silo:
        jiminy.create(
            "RigDefault", asset, "tailcoat.rig",
            options=None, data={"silo": silo}
        )


def createLook(*args):
    asset, silo = _create_registered_asset()
    if asset and silo:
        jiminy.create(
            "LookDefault", asset, "tailcoat.look",
            options=None, data={"silo": silo}
        )
