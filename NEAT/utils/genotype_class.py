import math
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt


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


def sigmoid(x, steepness=1):
    # if x < 100:
    #     return 0
    # elif x > 100:
    #     return 1
    return 1 / (1 + math.exp(-x * steepness))


class Genotype:
    def __init__(self, list_of_nodes=[], list_of_connections=[]):
        assert all(isinstance(node, Node) for node in list_of_nodes)
        assert all(isinstance(connection, Connection) for connection in list_of_connections)
        self.nodes = list_of_nodes
        self.connections = list_of_connections
        self.processing_parameters = "Perform evaluation first!"

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

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def evaluate(self, input_size, output_size):
        incoming_nodes = {}
        id_layers = {node.id: node.layer for node in self.nodes}
        bias_id = [node.id for node in self.nodes if node.placement == 'Bias']
        assert len(bias_id) == 1
        bias_id = bias_id[0]
        for conn in self.connections:
            if conn.enabled and not conn.is_recurrent:
                incoming_nodes.setdefault(conn.g_out, []).append((conn.g_in, conn.weight))

        to_evaluate = []
        evaluating_method = {}

        # checks which nodes should be activated for each layer to calculate values on output nodes
        # moreover saves in evaluating method, how to evaluate single node
        def calculate_layers(node_id):
            if node_id < input_size or node_id == bias_id:
                to_evaluate.append(node_id)
                return True

            worth_evaluating = False
            for previous_node_id, weight in incoming_nodes.get(node_id, []):
                if previous_node_id in to_evaluate or calculate_layers(previous_node_id):
                    worth_evaluating = True
                    evaluating_method.setdefault(node_id, []).append((previous_node_id, weight))
            if worth_evaluating:
                to_evaluate.append(node_id)
            return worth_evaluating

        output_ids = list(range(input_size, input_size + output_size))
        for output_id in output_ids:
            calculate_layers(output_id)

        layers = {}
        for node_id in to_evaluate:
            layers.setdefault(id_layers[node_id], []).append(node_id)

        self.processing_parameters = (layers, evaluating_method, to_evaluate, input_size, output_size, bias_id)

    def processing(self, input_layer, activation_function=sigmoid):
        layers, evaluating_method, to_evaluate, input_size, output_size, bias_id = self.processing_parameters
        node_values = {node_id: 0 if input_size + output_size > node_id >= input_size else None for node_id in
                       to_evaluate}
        node_values[bias_id] = 1
        for i, val in enumerate(input_layer):
            if i in to_evaluate:
                node_values[i] = val
        layers_numbers = sorted(list(layers.keys()))
        layers_numbers.remove(0)
        while layers_numbers:
            nodes = layers[layers_numbers.pop(0)]
            for node_id in nodes:
                node_values[node_id] = activation_function(
                    np.sum([weight * node_values[sub_node_id] for sub_node_id, weight in evaluating_method[node_id]]))

        return [node_values[node_id] for node_id in range(input_size, input_size + output_size)]


if __name__ == '__main__':
    from NEAT.utils.visualization import visualize_single

    genotype = Genotype()

    nodes = [Node(0, 0, "Sensor"), Node(1, 0, "Sensor"), Node(2, 0, "Bias"), Node(3, 2, "Output"), Node(4, 1, "Hidden")]
    genotype += nodes

    connection1 = Connection(0, 3, 0.7, True, 1, False)
    connection3 = Connection(2, 3, 0.5, True, 3, False)
    connection4 = Connection(1, 4, 0.2, True, 4, False)
    # connection5 = Connection(4, 3, 0.4, True, 5, False)
    connection6 = Connection(0, 4, 0.6, True, 6, False)
    # connection7 = Connection(4, 5, 0.6, True, 11, True)

    connections = [connection1, connection3, connection4, connection6]
    genotype += connections

    genotype.evaluate(3, 1)
    print(genotype.processing([1, 2, 3]))

    X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range = visualize_single(
        genotype)
    plt.scatter(X_nodes, Y_nodes)
    plt.plot(X_conn_enabled, Y_conn_enabled, c='g')
    plt.plot(X_conn_disabled, Y_conn_disabled, c='r')
    plt.plot(X_conn_rec, Y_conn_rec, c='b')
    plt.yticks([])
    plt.xticks([])
    plt.show()
