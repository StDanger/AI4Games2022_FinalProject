from NEAT.utils.genotype_class import Genotype, Connection, Node
import numpy as np

def get_init_population(parameters: 'NEAT'):
    return [create_individual(parameters) for _ in range(parameters.pop_size)]


def create_individual(param: 'NEAT'):
    # Nodes initialization
    nodes = [Node(id=ID, layer=0, placement='Sensor') for ID in range(param.input_n)]
    nodes += [Node(id=ID, layer=2, placement='Output') for ID in
                 range(param.input_n, param.input_n + param.output_n)]
    nodes += [Node(id=ID, layer=1, placement='Hidden') for ID in
                 range(param.input_n + param.output_n, param.input_n + param.output_n + param.hidden_n)]

    nodes = [Node(id=ID, layer=0, placement='Sensor') for ID in range(param.input_n)] + [Node(id=ID, layer=2, placement='Output') for ID in
                 range(param.input_n, param.input_n + param.output_n)] + [Node(id=ID, layer=1, placement='Hidden') for ID in
                 range(param.input_n + param.output_n, param.input_n + param.output_n + param.hidden_n)]

    if param.hidden_n != 0:
        # Connections initialization
        input_to_hidden = set()
        out = set()

        while not input_to_hidden:
            input_to_hidden = set()
            connections = []
            for connection_in in range(param.input_n):
                for connection_out in range(param.input_n + param.output_n, param.input_n + param.output_n + param.hidden_n):
                    if np.random.random() < param.init_connection_density:
                        innov = param.get_innov(connection_in, connection_out)
                        connections.append(Connection(connection_in,connection_out,np.random.randint(-20,20,1),True,innov,False))
                        input_to_hidden.add(connection_out)

        while len(out) != param.output_n:
            connections_second_layer = []
            out = set()
            for connection_in in list(input_to_hidden):
                for connection_out in range(param.input_n, param.input_n + param.output_n):
                    if np.random.random() < param.init_connection_density:
                        innov = param.get_innov(connection_in,connection_out)
                        connections_second_layer.append(Connection(connection_in,connection_out,np.random.randint(-20,20,1),True,innov,False))
                        out.add(connection_out)
        connections += connections_second_layer

    else:
        out = set()
        while len(out)!=param.output_n:
            connections = []
            out = set()
            for connection_in in range(param.input_n):
                for connection_out in range(param.input_n, param.input_n + param.output_n):
                    if np.random.random() < param.init_connection_density:
                        innov = param.get_innov(connection_in, connection_out)
                        connections.append(Connection(connection_in, connection_out, np.random.randint(-20,20,1), True, innov, False))
                        out.append(connection_out)
    return Genotype(nodes,connections)