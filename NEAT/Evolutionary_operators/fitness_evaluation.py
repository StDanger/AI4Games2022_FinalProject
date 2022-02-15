import numpy as np


def fitness_evaluation(neat: 'NEAT'):
    fitness_adjusted = []
    for specie in neat.species:
        max_score = specie.max_score
        specie.fitness = []
        specie.adjusted_fitness = []
        [individual.evaluate(neat.input_n, neat.output_n) for individual in specie.members]
        specie.fitness = neat.fitness_function([individual.processing for individual in specie.members],
                                               process_count=min(neat.threads, specie.size))
        specie.adjusted_fitness = [val / specie.size for val in specie.fitness]
        specie.max_score = max(specie.max_score, max(specie.fitness))

        if specie.max_score > max_score:
            specie.generation_since_improved = 0
        else:
            specie.generation_since_improved += 1
        specie.avg_fitness_adjusted = np.mean(specie.adjusted_fitness)
        fitness_adjusted.append(np.sum(specie.adjusted_fitness))

    global_avg = np.sum(fitness_adjusted) / neat.pop_size

    total = 0
    decimals = []

    if len(neat.species) == 1:
        neat.species[0].offspring_size = neat.pop_size
        return None

    for specie in neat.species:
        num = (specie.avg_fitness_adjusted / global_avg) * specie.size
        floor = int(np.floor(num))
        total += floor
        decimals.append(num - floor)
        specie.offspring_size = floor

    if total != neat.pop_size:
        for i in np.argsort(decimals)[total - neat.pop_size:]:
            neat.species[i].offspring_size += 1
