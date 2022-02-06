from NEAT.utils.species import Specie
import numpy as np


def speciation_init(neat: 'NEAT', population):
    species = []
    not_assigned = list(range(neat.pop_size))
    while not_assigned:
        id = np.random.choice(not_assigned)
        class_representative = population[id]
        specie = Specie(representative=class_representative)
        for id in not_assigned:
            individual = population[id]
            if compatibility_difference(class_representative, individual, neat) < neat.threshold:
                specie.members.append(individual)
                not_assigned.remove(id)
        specie.size = len(specie.members)
        species.append(specie)
    return species


def compatibility_difference(individual_1, individual_2, neat):
    conn_1 = [conn for conn in individual_1.connections if conn.enabled]
    conn_2 = [conn for conn in individual_2.connections if conn.enabled]
    num_conn_1 = len(conn_1)
    num_conn_2 = len(conn_2)
    overlapping_1,overlapping_2 = intersection(conn_1, conn_2)

    if overlapping_1:
        W = np.mean([(conn_1.weight-conn_2.weight) for conn_1, conn_2 in zip(overlapping_1,overlapping_2)])
    else:
        W = 0
    E = 0
    D = num_conn_1 + num_conn_2 - 2 * len(overlapping_1)
    N = max(num_conn_1, num_conn_2)

    E = E / N
    D = D / N
    return neat.c_1 * E + neat.c_2 * D + neat.c_3 * W

def get_num_of_excess_genes(conn_1, conn_2):
    def get_max(conn):
        max_innov = 0
        for connection in conn:
            max_innov = max(max_innov,connection.innov)
    max_1 = get_max(conn_1)
    max_2 = get_max(conn_2)
    searched_value = 0
    if max_1 < max_2:
        for connection in conn_2:
            if connection.innov > max_1:
                searched_value += 1
    elif max_2 < max_1:
        for connection in conn_1:
            if connection.innov > max_2:
                searched_value += 1
    return searched_value

def intersection(conn_1, conn_2):
    def contain(innov):
        for connection_2 in conn_2:
            if connection_2.innov == innov:
                return [connection_2]
        return []

    overlapping_1, overlapping_2 = [], []
    for connection_1 in conn_1:
        connection_2 = contain(connection_1.innov)
        if connection_2:
            overlapping_1.append(connection_1)
            overlapping_2 += connection_2
    return overlapping_1,overlapping_2


def speciation(neat: 'NEAT'):
    population = [member for specie in neat.species for member in specie.members]

    for specie in neat.species:
        if specie.generation_since_improved > 15:
            neat.species.remove(specie)
        specie.representative = np.random.choice(specie.members)
        specie.members = []

    # assert len(population) == neat.pop_size

    not_assigned = list(range(neat.pop_size))

    for specie in neat.species:
        for id in not_assigned:
            individual = population[id]
            if compatibility_difference(specie.representative, individual, neat) < neat.threshold:
                specie.members.append(individual)
                not_assigned.remove(id)
        specie.size = len(specie.members)

    while not_assigned:
        id = np.random.choice(not_assigned)
        class_representative = population[id]
        specie = Specie(representative=class_representative)
        for id in not_assigned:
            individual = population[id]
            if compatibility_difference(class_representative, individual, neat) < neat.threshold:
                specie.members.append(individual)
                not_assigned.remove(id)
        specie.size = len(specie.members)
        neat.species.append(specie)

    if len(neat.species) < neat.target_number_of_species:
        neat.threshold -= 0.5
    elif len(neat.species) > neat.target_number_of_species:
        neat.threshold += 0.5