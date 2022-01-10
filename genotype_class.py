class Node:
    """
        id: identification number of a node
        placement:  Sensor / Output / Hidden
    """

    def __init__(self, id: int, placement: str):
        self.id = id
        self.placement = placement

    def __str__(self):
        return str(self.id) + " " + self.placement

    def __radd__(self, other):
        return other + str(self)


class Connection:
    """
        g_in: id of the node at the beginning of the connection
        g_out: id of the node at the end of the connection
        weight: weight of the connection - float from range [-1,1]
        state: Enabled / Disabled
        innov: innovation number
    """

    def __init__(self, g_in: int, g_out: int, weight: float, state: str, innov: int):
        self.g_in = g_in
        self.g_out = g_out
        self.weight = weight
        self.state = state
        self.innov = innov

    def __str__(self):
        return str(self.g_in) + ' ' + str(self.g_out) + ' ' + str(self.weight) + ' ' + self.state + ' ' + str(
            self.innov)

    def __radd__(self, other):
        return other + str(self)


class Genotype:
    def __init__(self, list_of_nodes=[], list_of_connections=[]):
        assert all(isinstance(node,Node) for node in list_of_nodes)
        assert all(isinstance(connection,Connection) for connection in list_of_connections)
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
            if all(isinstance(node, Node) for node in other):
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

    nodes = [Node(1, "Sensor"), Node(2, "Sensor"), Node(3, "Sensor"), Node(4, "Output"), Node(5, "Hidden")]
    genotype += nodes

    connection1 = Connection(1, 4, 0.7, "Enabled", 1)
    connection2 = Connection(2, 4, -0.5, "Disabled", 2)
    connection3 = Connection(3, 4, 0.5, "Enabled", 3)
    connection4 = Connection(2, 5, 0.2, "Enabled", 4)
    connection5 = Connection(5, 4, 0.4, "Enabled", 5)
    connection6 = Connection(1, 5, 0.6, "Enabled", 6)
    connection7 = Connection(4, 5, 0.6, "Enabled", 11)

    connections = [connection1, connection2, connection3, connection4, connection5, connection6, connection7]
    genotype += connections

    print(genotype)
