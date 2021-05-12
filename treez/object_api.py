"""Just a bunch of useful classes."""
from typing import List, Sequence, Tuple, Optional
import json
from .util import (
    Node,
    NodeProperties,
    NodeProperty,
    SymbolicNodeProperty,
    NumericalNodeProperty,
    Parenthood,
    Childhood,
    Edge,
    EdgeProperties,
    EdgeProperty,
    NumericalEdgeProperty,
    SymbolicEdgeProperty,
    UFDS,
    InvalidEdgeProps,
    InvalidNodeProps,
    UndefinedParenthood,
    UndefinedChildhood
)
from .functional_api import (
    get_root as _get_root,
    get_root_path as _get_root_path,
    get_leaves as _get_leaves,
    tree_to_json as _tree_to_json,
    kruskal_tree as _kruskal_tree,
    kruskal_edges as _kruskal_edges
)


class Tree(object):
    """Object to handle trees."""

    def __init__(
        self,
        nodes: Sequence[Node] = None,
        parents: Parenthood = None,
        children: Childhood = None,
        nodeprops: NodeProperties = None,
        edgeprops: EdgeProperties = None,
        jsonfile: str = None
    ):
        """Init tree object."""
        self.nodes = nodes
        self.parents = parents
        self.children = children
        self.nodeprops = nodeprops
        self.edgeprops = edgeprops
        if jsonfile is not None:
            self.from_json(jsonfile)

    def get_root(self, node: Node = None) -> Node:
        """Give root of the tree."""
        if self.parents is not None:
            return _get_root(self.parents, node)
        raise UndefinedParenthood(
            "Parenthood of the tree was not defined, please build the tree before use."
        )

    def get_root_path(self, node: Node) -> List[Node]:
        """Get path to root of the tree."""
        if self.parents is not None:
            return _get_root_path(self.parents, node)
        raise UndefinedParenthood(
            "Parenthood of the tree was not defined, please build the tree before use."
        )

    def get_leaves(self, node: Node) -> List[Node]:
        """Get leaves of a node."""
        if self.children is not None:
            return _get_leaves(self.children, node)
        raise UndefinedChildhood(
            "Childhood of the tree was not defined, please build the tree before use."
        )

    def to_json(self, jsonfile):
        """Store the tree to json file."""
        _tree_to_json(
            self.nodes,
            self.parents,
            self.children,
            jsonfile,
            self.nodeprops,
            self.edgeprops
        )

    def from_json(self, jsonfile):
        """Create the tree from a json file."""
        with open(jsonfile, "r") as jf:
            json_dict = json.load(jf)
        for k, v in json_dict.items():
            if k == "nodes":
                self.nodes = v
            if k == "parents":
                self.parents = v
            if k == "children":
                self.children = v
            if k == "edgeprops":
                self.edgeprops = v
            if k == "nodeprops":
                self.nodeprops = v

    def build_kruskal(
        self, edges: Sequence[Edge],
        weights: NumericalEdgeProperty,
        size: NumericalNodeProperty
    ):
        """Build tree with kruskal algorithm from graph edges."""
        k_parents, k_children, k_props = _kruskal_tree(edges, weights, size)
        self.parents = k_parents
        self.children = k_children
        k_nodes = set(k_parents.keys())
        # root can be missing
        k_nodes.add(self.get_root())
        self.nodes = list(k_nodes)
        self.nodeprops = k_props
