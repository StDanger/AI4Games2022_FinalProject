import numpy as np
from copy import deepcopy

def crossover(neat: 'NEAT'):
    species = []
    for specie in neat.species:
        if specie.offspring_size:
            new_specie_members = [specie.members[i] for i in np.argsort(specie.fitness)[-neat.elitism:]]
            for _ in range(specie.offspring_size-neat.elitism):
                new_individual = single_crossover(specie)
                new_specie_members.append(new_individual)
            specie.members = new_specie_members
            specie.size = len(new_specie_members)
            species.append(specie)
    neat.species = species

def single_crossover(specie):
    if specie.size>1:
        individual_1, individual_2 = roulette_wheel_selection(specie)
        overlapping_1, overlapping_2 = intersection(individual_1.connections, individual_2.connections)
        new_individual = deepcopy(individual_1)
        for id_1, id_2 in zip(overlapping_1,overlapping_2):
            if np.random.random() < 0.5:
                new_individual.connections[id_1].weight = individual_2.connections[id_2].weight
    else:
        new_individual = deepcopy(specie.members[0])
    return new_individual

def intersection(conn_1, conn_2):
    def contain(innov):
        for id_2, connection_2 in enumerate(conn_2):
            if connection_2.innov == innov:
                return [id_2]
        return []

    overlapping_1, overlapping_2 = [], []
    for id_1, connection_1 in enumerate(conn_1):
        connection_2 = contain(connection_1.innov)
        if connection_2:
            overlapping_1.append(id_1)
            overlapping_2 += connection_2
    return overlapping_1,overlapping_2


def roulette_wheel_selection(specie):
    id_1,id_2 = np.random.choice(np.arange(specie.size),2,p=np.array(specie.fitness)/np.sum(specie.fitness))
    if specie.fitness[id_1] > specie.fitness[id_2]:
        return specie.members[id_1], specie.members[id_2]
    else:
        return specie.members[id_2], specie.members[id_1]