import numpy as np

def weight_mutation(neat: 'NEAT'):
    for specie in neat.species:
        for individual in specie.members:
            for connection in individual.connections:
                mutation_type = np.random.choice([0,1,2],1,p=[0.8*0.9,0.8*0.1,0.2])
                if mutation_type == 0:
                    connection.weight = np.random.normal(loc=connection.weight,scale=np.abs(connection.weight)/12.0)
                elif mutation_type == 1:
                    connection.weight = np.random.normal(loc=0,scale=1)
                # else:
                #     None mutation

    # Possible enhancement:
    # change mutation rate based on improvements of a specie
