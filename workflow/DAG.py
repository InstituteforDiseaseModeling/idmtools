class DAG:

    class NoSuchNodeException(Exception):
        pass

    class LoopException(Exception):
        pass

    def __init__(self, nodes):
        # TODO: we currently assume each node has a different name; we should error check this
        self.nodes = nodes
        self.nodes_by_name = None
        self.build()

    def build(self):
        # - Can be called at anytime to rebuild the dag (in case node structure has changed)
        # - Needs to call set_dependents (maybe dependees) on the tasks
        # - This method essentially sets dependee/dependent references on the nodes as objects, not strings (names)
        # - Needs to call self.verify()
        # resolve depends_on attribute of each node to dependent/dependee references
        self.nodes_by_name = {node.name: node for node in self.nodes}

        # clear then rebuild dependees and dependents. TODO: THIS IS NOT MULTIPROCESS SAFE RIGHT NOW
        for node in self.nodes:
            node.dependees = []
            node.dependents = []

        for node in self.nodes:
            for dependee_node_name in node.depends_on:
                dependee_node = self.get_node_by_name(node_name=dependee_node_name)
                node.dependees.append(dependee_node)
                dependee_node.dependents.append(node)
        self.verify()

    # TODO: the loop detection is broken. Fix it, do it right.
    def verify(self):
        # Make sure there are no loops
        # Current algorithm may be overkill, but is sufficient. It is a search starting at each node that tries to find
        # itself. A more efficient way would be to dye-mark each visited node (so a loop would be detected starting at
        # any node in the subgraph containing it, not just starting at nodes in the loop. But I don't really want to dye
        # mark the nodes (modifying the Task objects, which may technically be passed around between DAGs... who knows
        # why though). This algorithm will be used with a small set of nodes, so efficiency is irrelevant.
        # A simple optimization would be to start at only root nodes (add method: self.root_nodes())
        for node in self.nodes:
            print('verifying node: %s' % node.name)
            nodes_to_check = node.dependees
            while len(nodes_to_check) > 0:
                print('nodes to check: %s' % [n.name for n in nodes_to_check])
                nodes_to_check_next = []
                # print(f'Nodes to check: {[n.name for n in nodes_to_check]}')
                for comparison_node in nodes_to_check:
                    if comparison_node.name == node.name:
                        raise self.LoopException(f'Loop detected in DAG including node: {node.name}')
                    else:
                        nodes_to_check_next += comparison_node.dependees
                nodes_to_check = nodes_to_check_next

    def get_node_by_name(self, node_name):
        try:
            node = self.nodes_by_name[node_name]
        except KeyError:
            raise self.NoSuchNodeException(f'Requested node with name: {node_name} not in DAG.') # ck4, revert node_name.name to node_name after debug
        return node

    def get_dependee_nodes(self, node, include_indirect=False):
        # requires a DAG to be built (duplicate node name error check) before running this else we can run into
        # node duplicate removal issues.
        nodes = node.dependees
        if include_indirect:
            indirect_dependees = []
            for dependee_node in nodes:
                indirect_dependees += self.get_dependee_nodes(node=dependee_node, include_indirect=True)
            # remove potential duplicates
            nodes = list({n.name: n for n in (nodes + indirect_dependees)}.values())
        return nodes

    def to_json(self):
        return [node.to_json() for node in self.nodes]

    def add_node(self, node):
        # any depends_on must have already been set or the node is disjoint from the existing dag
        if node.name not in self.nodes_by_name:
            self.nodes.append(node)

