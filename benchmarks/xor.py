# def xor(processing_function):
#     total_score = 0
#     total_score += (1 - processing_function([1, 0])[0]) ** 2
#     total_score += (1 - processing_function([0, 1])[0]) ** 2
#     total_score += (processing_function([1, 1])[0]) ** 2
#     total_score += (processing_function([0, 0])[0]) ** 2
#     return 4-total_score

def xor(processing_functions, *args, **kwargs):
    scores = []
    for processing_function in processing_functions:
        total_score = 0
        total_score += (1 - processing_function([1, 1])[0])
        total_score += (1 - processing_function([0, 0])[0])
        total_score += (processing_function([0, 1])[0])
        total_score += (processing_function([1, 0])[0])
        scores.append(total_score)
    return scores


def xor_as_Kenneth_said(processing_function):
    total_score = 0
    total_score += int(processing_function([1, 1])[0] < 0.5)
    total_score += int(processing_function([0, 0])[0] < 0.5)
    total_score += int(processing_function([1, 0])[0] >= 0.5)
    total_score += int(processing_function([0, 1])[0] >= 0.5)
    return total_score


if __name__ == '__main__':
    # Genotype that solves a xor problem
    from NEAT.utils.visualization import visualize
    from NEAT.utils.genotype_class import Genotype, Node, Connection

    genotype = Genotype()

    nodes = [Node(0, 0, "Sensor"), Node(1, 0, "Sensor"), Node(5, 0, "Bias"), Node(2, 2, "Output"), Node(3, 1, "Hidden"),
             Node(4, 1, "Hidden")]
    genotype += nodes

    connection1 = Connection(0, 3, 20.0, True, 1, False)
    connection2 = Connection(0, 4, -20.0, True, 2, False)
    connection3 = Connection(1, 3, 20.0, True, 3, False)
    connection4 = Connection(1, 4, -20.0, True, 4, False)
    connection5 = Connection(5, 3, -10.0, True, 5, False)
    connection6 = Connection(5, 4, 30.0, True, 6, False)
    connection7 = Connection(3, 2, 20.0, True, 7, False)
    connection8 = Connection(4, 2, 20.0, True, 8, False)
    connection9 = Connection(5, 2, -30, True, 9, False)

    connections = [connection1, connection2, connection3, connection4, connection5, connection6, connection7,
                   connection8, connection9]
    genotype += connections

    genotype.evaluate(2, 1)

    print(xor_as_Kenneth_said(genotype.processing))
    print(xor(genotype.processing))

    visualize(genotype)
