import uuid
import pymel.core as pm
from maya import cmds
from maya.api import OpenMaya as om


def set_model_uuid():
    """Add modelID to `mesh node`

    Unless one already exists.

    """
    nodes = (set(cmds.ls(type="mesh", long=True)) -
             set(cmds.ls(long=True, readOnly=True)) -
             set(cmds.ls(long=True, lockedNodes=True)))

    transforms = cmds.listRelatives(list(nodes), parent=True) or list()

    # Add unique identifiers
    for node in transforms:
        attr = "{0}.modelID".format(node)

        if not cmds.objExists(attr):
            cmds.addAttr(node, longName="modelID", dataType="string")
            _, uid = str(uuid.uuid4()).rsplit("-", 1)
            cmds.setAttr(attr, uid, type="string")


def remove_all_namespaces():
    defaultNs = ["UI", "shared"]

    nsLs = cmds.namespaceInfo(listOnlyNamespaces=True)
    diffLs = [item for item in nsLs if item not in defaultNs]

    while diffLs:
        for ns in diffLs:
            nsNest = cmds.namespaceInfo(ns, listOnlyNamespaces=True)
            remove = nsNest[0] if nsNest else ns
            cmds.namespace(
                removeNamespace=remove,
                mergeNamespaceWithRoot=True,
                force=True
            )
            nsLs = cmds.namespaceInfo(listOnlyNamespaces=True)
            diffLs = [item for item in nsLs if item not in defaultNs]

    # do check
    nsLs = cmds.namespaceInfo(listOnlyNamespaces=True)
    diffLs = [item for item in nsLs if item not in defaultNs]

    if diffLs:
        cmds.error('namespace might not clear yet! Please try again...')
    else:
        cmds.warning('namespace clear!')


def remove_namespace(nodes):
    """Remove nodes's namespaces"""
    # Get nodes with pymel since we'll be renaming them
    # We don't want to keep checking the hierarchy
    # or full paths
    for node in pm.ls(nodes):
        namespace = node.namespace()
        if namespace:
            name = node.nodeName()
            node.rename(name[len(namespace):])


def serialise_shaders(nodes):
    """Generate a shader set dictionary

    Arguments:
        nodes (list): Absolute paths to nodes

    Returns:
        dictionary of (shader: id) pairs

    Schema:
        {
            "shader1": ["id1", "id2"],
            "shader2": ["id3", "id1"]
        }

    Example:
        {
            "Bazooka_Brothers01_:blinn4SG": [
                "f9520572-ac1d-11e6-b39e-3085a99791c9.f[4922:5001]",
                "f9520572-ac1d-11e6-b39e-3085a99791c9.f[4587:4634]",
                "f9520572-ac1d-11e6-b39e-3085a99791c9.f[1120:1567]",
                "f9520572-ac1d-11e6-b39e-3085a99791c9.f[4251:4362]"
            ],
            "lambert2SG": [
                "f9520571-ac1d-11e6-9dbb-3085a99791c9"
            ]
        }

    """

    valid_nodes = cmds.ls(
        nodes,
        long=True,
        recursive=True,
        showType=True,
        objectsOnly=True,
        type="transform"
    )

    meshes_by_id = {}
    for mesh in valid_nodes:
        shapes = cmds.listRelatives(valid_nodes[0],
                                    shapes=True,
                                    fullPath=True) or list()

        if shapes:
            shape = shapes[0]
            if not cmds.nodeType(shape):
                continue

            try:
                id_ = cmds.getAttr(mesh + ".modelID")

                if id_ not in meshes_by_id:
                    meshes_by_id[id_] = list()

                meshes_by_id[id_].append(mesh)

            except ValueError:
                continue

    meshes_by_shader = dict()
    for id_, mesh in meshes_by_id.items():
        shape = cmds.listRelatives(mesh,
                                   shapes=True,
                                   fullPath=True) or list()

        for shader in cmds.listConnections(shape,
                                           type="shadingEngine") or list():

            # Objects in this group are those that haven't got
            # any shaders. These are expected to be managed
            # elsewhere, such as by the default model loader.
            if shader == "initialShadingGroup":
                continue

            if shader not in meshes_by_shader:
                meshes_by_shader[shader] = list()

            shaded = cmds.sets(shader, query=True) or list()
            meshes_by_shader[shader].extend(shaded)

    shader_by_id = {}
    for shader, shaded in meshes_by_shader.items():

        if shader not in shader_by_id:
            shader_by_id[shader] = list()

        for mesh in shaded:

            # Enable shader assignment to faces.
            name = mesh.split(".f[")[0]

            transform = name
            if cmds.objectType(transform) == "mesh":
                transform = cmds.listRelatives(name, parent=True)[0]

            try:
                id_ = cmds.getAttr(transform + ".modelID")
                shader_by_id[shader].append(mesh.replace(name, id_))
            except KeyError:
                continue

        # Remove duplicates
        shader_by_id[shader] = list(set(shader_by_id[shader]))

    return shader_by_id


def apply_shaders(relationships, namespace=None):
    """Given a dictionary of `relationships`, apply shaders to meshes

    Arguments:
        relationships (avalon-core:shaders-1.0): A dictionary of
            shaders and how they relate to meshes.

    """

    if namespace is not None:
        # Append namespace to shader group identifier.
        # E.g. `blinn1SG` -> `Bruce_:blinn1SG`
        relationships = {
            "%s:%s" % (namespace, shader): relationships[shader]
            for shader in relationships
        }

    for shader, ids in relationships.items():
        print("Looking for '%s'.." % shader)
        shader = next(iter(cmds.ls(shader)), None)
        assert shader, "Associated shader not part of asset, this is a bug"

        for id_ in ids:
            mesh, faces = (id_.rsplit(".", 1) + [""])[:2]

            # Find all meshes matching this particular ID
            # Convert IDs to mesh + id, e.g. "nameOfNode.f[1:100]"
            meshes = list(".".join([mesh, faces])
                          for mesh in lsattr("modelID", value=mesh))

            if not meshes:
                continue

            print("Assigning '%s' to '%s'" % (shader, ", ".join(meshes)))
            cmds.sets(meshes, forceElement=shader)


def lsattr(attr, value=None):
    """Return nodes matching `key` and `value`

    Arguments:
        attr (str): Name of Maya attribute
        value (object, optional): Value of attribute. If none
            is provided, return all nodes with this attribute.

    Example:
        >> lsattr("id", "myId")
        ["myNode"]
        >> lsattr("id")
        ["myNode", "myOtherNode"]

    """

    if value is None:
        return cmds.ls("*.%s" % attr)
    return lsattrs({attr: value})


def lsattrs(attrs):
    """Return nodes with the given attribute(s).

    Arguments:
        attrs (dict): Name and value pairs of expected matches

    Example:
        >> lsattr("age")  # Return nodes with attribute `age`
        >> lsattr({"age": 5})  # Return nodes with an `age` of 5
        >> # Return nodes with both `age` and `color` of 5 and blue
        >> lsattr({"age": 5, "color": "blue"})

    Returns a list.

    """

    dep_fn = om.MFnDependencyNode()
    dag_fn = om.MFnDagNode()
    selection_list = om.MSelectionList()

    first_attr = attrs.iterkeys().next()

    try:
        selection_list.add("*.{0}".format(first_attr),
                           searchChildNamespaces=True)
    except RuntimeError, e:
        if str(e).endswith("Object does not exist"):
            return []

    matches = set()
    for i in range(selection_list.length()):
        node = selection_list.getDependNode(i)
        if node.hasFn(om.MFn.kDagNode):
            fn_node = dag_fn.setObject(node)
            full_path_names = [path.fullPathName()
                               for path in fn_node.getAllPaths()]
        else:
            fn_node = dep_fn.setObject(node)
            full_path_names = [fn_node.name()]

        for attr in attrs:
            try:
                plug = fn_node.findPlug(attr, True)
                if plug.asString() != attrs[attr]:
                    break
            except RuntimeError:
                break
        else:
            matches.update(full_path_names)

    return list(matches)
