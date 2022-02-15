from NEAT.utils.genotype_class import Genotype, Connection, Node
import numpy as np


def get_init_population(neat: 'NEAT'):
    return [create_individual(neat) for _ in range(neat.pop_size)]


def create_individual(neat: 'NEAT'):
    # Nodes initialization
    nodes = [Node(id=ID, layer=0, placement='Sensor') for ID in range(neat.input_n)]
    nodes += [Node(id=ID, layer=2, placement='Output') for ID in
              range(neat.input_n, neat.input_n + neat.output_n)]
    nodes += [Node(id=ID, layer=1, placement='Hidden') for ID in
              range(neat.input_n + neat.output_n, neat.input_n + neat.output_n + neat.hidden_n)]
    bias_id = neat.input_n + neat.output_n + neat.hidden_n
    nodes.append(Node(id=bias_id, layer=0, placement='Bias'))

    if neat.hidden_n != 0:
        # Connections initialization
        input_to_hidden = set()
        out = set()

        while not input_to_hidden:
            input_to_hidden = set()
            connections = []
            for connection_in in range(neat.input_n):
                for connection_out in range(neat.input_n + neat.output_n, neat.input_n + neat.output_n + neat.hidden_n):
                    if np.random.random() < neat.init_connection_density:
                        innov = neat.get_innov(connection_in, connection_out)
                        connections.append(
                            Connection(connection_in, connection_out, np.random.normal(0, 1, 1)[0], True, innov, False))
                        input_to_hidden.add(connection_out)

        while len(out) != neat.output_n:
            connections_second_layer = []
            out = set()
            for connection_in in list(input_to_hidden):
                for connection_out in range(neat.input_n, neat.input_n + neat.output_n):
                    if np.random.random() < neat.init_connection_density:
                        innov = neat.get_innov(connection_in, connection_out)
                        connections_second_layer.append(
                            Connection(connection_in, connection_out, np.random.normal(0, 1, 1)[0], True, innov, False))
                        out.add(connection_out)
        connections += connections_second_layer

    else:
        out = set()
        while len(out) != neat.output_n:
            connections = []
            out = set()
            for connection_in in range(neat.input_n):
                for connection_out in range(neat.input_n, neat.input_n + neat.output_n):
                    if np.random.random() < neat.init_connection_density:
                        innov = neat.get_innov(connection_in, connection_out)
                        connections.append(
                            Connection(connection_in, connection_out, np.random.normal(0, 1, 1)[0], True, innov, False))
                        out.append(connection_out)

    for i in range(neat.input_n, bias_id):
        innov = neat.get_innov(bias_id, i)
        connections.append(Connection(bias_id, i, np.random.normal(0, 1, 1)[0], True, innov, False))
    return Genotype(nodes, connections)
