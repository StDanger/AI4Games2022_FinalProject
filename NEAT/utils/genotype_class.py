class Node:
    """
        id: identification number of a node
        layer: specifies the layer of the node (longest distance to input node)
        placement:  Sensor / Bias / Output / Hidden
    """

    def __init__(self, id: int, layer: int, placement: str):
        self.id = id
        self.placement = placement
        self.layer = layer

    def __str__(self):
        return 'ID: ' + str(self.id) + ', layer: ' + str(self.layer) + ", type: " + self.placement

    def __radd__(self, other):
        return other + str(self)


class Connection:
    """
        g_in: id of the node at the beginning of the connection
        g_out: id of the node at the end of the connection
        weight: weight of the connection
        enabled: specifies state of connection (enabled / disabled)
        innov: innovation number
        is_recurrent: specifies is it a recurrent connection
    """

    def __init__(self, g_in: int, g_out: int, weight: float, enabled: bool, innov: int, is_recurrent: bool):
        self.g_in = g_in
        self.g_out = g_out
        self.weight = weight
        self.enabled = enabled
        self.innov = innov
        self.is_recurrent = is_recurrent

    def __str__(self):
        state = 'enabled' if self.enabled else 'disabled'
        is_recurrent = ' recurrent' if self.is_recurrent else ' forward'
        return 'in: ' + str(self.g_in) + ', out: ' + str(self.g_out) + ', weight:' + str(self.weight) + ', state: ' + \
               state + ', innovation number: ' + str(self.innov) + ', type: ' + is_recurrent

    def __radd__(self, other):
        return other + str(self)


class Genotype:
    def __init__(self, list_of_nodes=[], list_of_connections=[]):
        assert all(isinstance(node, Node) for node in list_of_nodes)
        assert all(isinstance(connection, Connection) for connection in list_of_connections)
        self.nodes = list_of_nodes
        self.connections = list_of_connections

    def __add__(self, other):
        """
            other: Node instance, Connection instance, list of Node instances or list of Connection instances
        """
        if isinstance(other, Connection):
            self.connections.append(other)
        elif isinstance(other, Node):
            self.nodes.append(other)
        elif isinstance(other, list):
            if all(isinstance(node, Connection) for node in other):
                self.connections += other
            elif all(isinstance(node, Node) for node in other):
                self.nodes += other
        else:
            raise NotImplementedError
        return self

    def __str__(self):
        total = "Nodes:"
        for node in self.nodes:
            total += "\n" + node
        total += "\n\nConnections:"
        for connection in self.connections:
            total += "\n" + connection
        return total


if __name__ == '__main__':
    genotype = Genotype()

    nodes = [Node(1, 0, "Sensor"), Node(2, 0, "Sensor"), Node(3, 0, "Bias"), Node(4, 2, "Output"), Node(5, 1, "Hidden")]
    genotype += nodes

    connection1 = Connection(1, 4, 0.7, True, 1, False)
    connection2 = Connection(2, 4, -0.5, False, 2, False)
    connection3 = Connection(3, 4, 0.5, True, 3, False)
    connection4 = Connection(2, 5, 0.2, True, 4, False)
    connection5 = Connection(5, 4, 0.4, True, 5, False)
    connection6 = Connection(1, 5, 0.6, True, 6, False)
    connection7 = Connection(4, 5, 0.6, True, 11, True)

    connections = [connection1, connection2, connection3, connection4, connection5, connection6, connection7]
    genotype += connections

    print(genotype)