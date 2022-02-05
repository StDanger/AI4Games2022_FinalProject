from NEAT.Evolutionary_operators.weight_mutation import weight_mutation
from NEAT.Evolutionary_operators.topology_mutation import topology_mutation
from NEAT.Evolutionary_operators.crossover import crossover
from NEAT.Evolutionary_operators.speciation import speciation
from NEAT.Evolutionary_operators.fitness_evaluation import fitness_evaluation
from NEAT.Evolutionary_operators.selection import selection
from NEAT.utils.initialize_population import get_init_population
from NEAT.utils.termination_conditions import iteration
from NEAT.utils.visualization import visualize
import numpy as np
import matplotlib.pyplot as plt


class NEAT:
    def __init__(self, **kwargs):
        self.pop_size = kwargs.get('pop_size',10)
        self.probability_of_weight_mutation = kwargs.get('probability_of_weight_mutation', 0.8)
        self.probability_of_topology_mutation = kwargs.get('probability_of_topology_mutation', 0.8)
        self.elitism = kwargs.get('elitism', 1)
        self.termination_condition = kwargs.get('termination_condition', iteration)
        self.fitness_function = kwargs.get('fitness_function', lambda *args: np.random.randint(0,100))
        self.track_performance = kwargs.get('track_performance', True)

        # speciation parameters from paper
        self.c_1 = kwargs.get('c_1', 1)
        self.c_2 = kwargs.get('c_2', 1)
        self.c_3 = kwargs.get('c_3', 0.4)
        self.threshold = kwargs.get('threshold', 3.0)
        self.N = kwargs.get('N', True)

        # initialization parameters
        self.input_n = kwargs.get('input_n',7)
        self.output_n = kwargs.get('output_n',6)
        self.hidden_n = kwargs.get('hidden_n',3)
        self.init_connection_density = kwargs.get('init_connection_density',0.3)
        self.innov = 1
        self.lookup_table = [[0] * 100 for _ in range(100)]

        population = kwargs.get('population', get_init_population(self))
        self.species = speciation(self,population)
        fitness_evaluation(self)

    def get_innov(self,input,output):
        innov = self.lookup_table[input][output]
        if innov == 0:
            innov = self.innov
            self.lookup_table[input][output] = innov
            self.innov += 1
        return innov

    def train(self):
        while not self.termination_condition(self):
            new_population = crossover(self)
            new_population = weight_mutation(self)
            new_population = topology_mutation(self, new_population)
            new_population = fitness_evaluation(self, new_population)
            new_population = speciation(self, new_population)
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

