import numpy as np

def weight_mutation(neat: 'NEAT'):
    p1 = neat.probability_of_small_weight_mutation
    p2 = neat.probability_of_total_weight_mutation
    for specie in neat.species:
        for individual in specie.members[neat.elitism:]:
            for connection in individual.connections:
                mutation_type = np.random.choice([0,1,2],1,p=[p1,p2,1-p1-p2])
                if mutation_type == 0:
                    connection.weight = np.random.normal(loc=connection.weight,scale=min(5,np.abs(connection.weight)/3))
                elif mutation_type == 1:
                    connection.weight = np.random.normal(loc=0,scale=2)
                # else:
                #     None mutation

    # Possible enhancement:
    # change mutation rate based on improvements of a specie
