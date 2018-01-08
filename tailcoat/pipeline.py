from maya import cmds
import os


def project_anchor():
    worksite = cmds.workspace(query=True, rootDirectory=True)
    return str(worksite) + "proj.anchor"


def publish_root():
    anchor = project_anchor()
    root = ""
    # find anchor in local project, assume it's local
    if os.path.isfile(anchor):
        with open(anchor) as anchor:
            content = anchor.readlines()
        root = content[-1]
    else:
        # if current workspace is at global project, should exists
        # publish repo
        worksite = cmds.workspace(query=True, rootDirectory=True)
        _ = publish_repo(worksite)
        if os.path.isdir(_):
            root = worksite
    return root


def publish_repo(root=None):
    if root is None:
        root = publish_root()
    return os.path.join(
        root,
        "assets",
        "_publish_"
    )


def publish_template():
    file_name_tamplate = "{asset}.{subset}.{representation}"
    return "{publish}/{silo}/{asset}/{subset}/" + file_name_tamplate
