from NEAT.Evolutionary_operators.weight_mutation import weight_mutation
from NEAT.Evolutionary_operators.topology_mutation import topology_mutation
from NEAT.Evolutionary_operators.crossover import crossover
from NEAT.Evolutionary_operators.speciacion import speciacion
from NEAT.Evolutionary_operators.fitness_evaluation import fitness_evaluation
from NEAT.Evolutionary_operators.selection import selection
from NEAT.utils.initialize_population import get_init_population
from NEAT.utils.termination_conditions import iteration
import numpy as np


class NEAT:
    def __init__(self, **kwargs):
        self.pop_size = kwargs.get('pop_size', 50)
        self.probability_of_weight_mutation = kwargs.get('probability_of_weight_mutation', 0.15)
        self.probability_of_topology_mutation = kwargs.get('probability_of_topology_mutation', 0.8)
        self.elitism_factor = kwargs.get('elitism_factor', 0.1)
        self.termination_condition = kwargs.get('termination_condition', iteration)
        self.population = kwargs.get('population', get_init_population(self.pop_size))
        self.fitness_values = kwargs.get('fitness_values', np.zeros(self.pop_size))
        self.fitness_function = kwargs.get('fitness_function', None)
        self.track_performance = kwargs.get('track_performance', True)
        self.species = kwargs.get('species', np.zeros(self.pop_size))
        # speciation parameters from paper
        self.c_1 = kwargs.get('c_1', 1)
        self.c_2 = kwargs.get('c_2', 1)
        self.c_3 = kwargs.get('c_3', 0.4)
        self.delta_t = kwargs.get('delta_t', 3.0)
        self.N = kwargs.get('N', True)

    def train(self):
        while not self.termination_condition(self):
            new_population = weight_mutation(self)
            new_population = topology_mutation(self, new_population)
            new_population = crossover(self, new_population)
            new_population = speciacion(self, new_population)
            new_population = fitness_evaluation(self, new_population)
            selection(self, new_population)

            if self.track_performance:
                self.track_performance()

            if self.verbose:
                self.show_information()

    def save_model(self, file_name):
        # saving current population and model parameters to pickle file
        return NotImplementedError

    def return_best_model(self):
        return NotImplementedError

    def track_performance(self):
        return NotImplementedError

    def show_information(self):
        return NotImplementedError
