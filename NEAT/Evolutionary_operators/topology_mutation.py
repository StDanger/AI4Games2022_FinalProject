from NEAT.utils.genotype_class import Node, Connection
import numpy as np


def topology_mutation(neat: 'NEAT'):
    for specie in neat.species:
        for individual in specie.members[neat.elitism:]:
            add_connection_mutation(individual, neat)
            add_node_mutation(individual, neat)
            correct_layers(individual, neat)


def add_connection_mutation(individual, neat):
    if np.random.random() < neat.probability_of_adding_a_connection:
        conn_dict = [(conn.g_in, conn.g_out) for conn in individual.connections]
        for _ in range(30):
            if add_connection(individual, conn_dict, neat):
                break


def add_connection(individual, conn_dict, neat):
    node_1, node_2 = np.random.choice(individual.nodes, 2)
    if node_1.layer == node_2.layer:
        return False
    is_recurrent = node_1.layer > node_2.layer
    if (node_1.id, node_2.id) in conn_dict:
        return False
    if node_1.id == neat.input_n + neat.output_n + neat.hidden_n:
        print("To nie powinno być możliwe")
        return False
    new_conn = Connection(node_1.id, node_2.id, np.random.normal(0, 1), True, neat.get_innov(node_1.id, node_2.id),
                          is_recurrent)
    individual.connections.append(new_conn)
    return True


def get_connections(individual):
    ingoing = {}
    recurrent = []
    for i, conn in enumerate(individual.connections):
        if conn.enabled:
            if conn.is_recurrent:
                recurrent.append(i)
            ingoing.setdefault(conn.g_out, []).append(conn.g_in)
    return ingoing, recurrent


def correct_layers(individual, neat):
    bias_id = neat.input_n + neat.output_n + neat.hidden_n
    nodes = {node.id: node.layer + 0.3 for node in individual.nodes}
    ingoing = {}
    recurrent = []
    endings = list(nodes.keys())
    for i, conn in enumerate(individual.connections):
        if conn.enabled:
            if conn.is_recurrent:
                recurrent.append(i)
            else:
                if conn.g_in in endings:
                    endings.remove(conn.g_in)
                ingoing.setdefault(conn.g_out, []).append(conn.g_in)

    def get_depth(node_id):
        if node_id < neat.input_n or node_id == bias_id:
            nodes[node_id] = 0
            return 0
        elif isinstance(nodes[node_id], int):
            return nodes[node_id]
        else:
            ingoing_nodes = ingoing.get(node_id, [])
            if ingoing_nodes:
                current_layer = max([get_depth(previous_node_id) + 1 for previous_node_id in ingoing_nodes])
            else:
                current_layer = int(nodes[node_id])
            nodes[node_id] = current_layer
            return current_layer

    max_depth = 0
    for output_id in endings:
        max_depth = max(max_depth, get_depth(output_id))
    for node_id in range(neat.input_n, neat.input_n + neat.output_n):
        nodes[node_id] = max_depth

    for node in individual.nodes:
        node.layer = int(nodes[node.id])

    for i in recurrent:
        conn = individual.connections[i]
        node_in, node_out = conn.g_in, conn.g_out
        if nodes[node_in] >= nodes[node_out]:
            conn.enabled = False
            conn.is_recurrent = False


def add_node_mutation(individual, neat):
    if np.random.random() < neat.probability_of_adding_a_node:
        add_node(individual, neat)
    # for conn in individual.connections:
    #     if conn.enabled and np.random.random() < 0.5:
    #         add_node(individual)


def add_node(individual, neat):
    bias_id = neat.input_n + neat.output_n + neat.hidden_n
    while True:
        conn = np.random.choice(individual.connections)
        if conn.enabled and not conn.is_recurrent and conn.g_in != bias_id and conn.g_out != bias_id:
            break
    node_1, node_2 = conn.g_in, conn.g_out
    conn.enabled = False
    new_node_id = neat.get_new_node_id(node_1, node_2)
    individual.nodes.append(Node(new_node_id, placement='Hidden', layer=2.5))

    innov_a = neat.get_innov(node_1, new_node_id)
    individual.connections.append(Connection(node_1, new_node_id, conn.weight, True, innov_a, False))

    innov_b = neat.get_innov(new_node_id, node_2)
    individual.connections.append(Connection(new_node_id, node_2, np.random.normal(0, 1), True, innov_b, False))

    innov_bias = neat.get_innov(bias_id, new_node_id)
    individual.connections.append(Connection(bias_id,new_node_id, np.random.normal(0, 1), True, innov_bias, False))
