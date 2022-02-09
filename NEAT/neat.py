from NEAT.Evolutionary_operators.weight_mutation import weight_mutation
from NEAT.Evolutionary_operators.topology_mutation import topology_mutation
from NEAT.Evolutionary_operators.crossover import crossover
from NEAT.Evolutionary_operators.speciation import speciation_init, speciation
from NEAT.Evolutionary_operators.fitness_evaluation import fitness_evaluation
from NEAT.Evolutionary_operators.selection import selection
from NEAT.utils.initialize_population import get_init_population
from NEAT.utils.termination_conditions import iteration
from NEAT.utils.visualization import visualize
from benchmarks.xor import xor
import numpy as np

# np.random.seed(0)


class NEAT:
    def __init__(self, **kwargs):
        self.pop_size = kwargs.get('pop_size', 100)

        # Mutation parameters
        self.probability_of_small_weight_mutation = kwargs.get('probability_of_small_weight_mutation', 0.8*0.8)
        self.probability_of_total_weight_mutation = kwargs.get('probability_of_total_weight_mutation', 0.8*0.2)

        self.probability_of_adding_a_node = kwargs.get('probability_of_adding_a_node', 0.01)
        self.probability_of_adding_a_connection = kwargs.get('probability_of_adding_a_connection', 0.01)

        self.elitism = kwargs.get('elitism', 3)
        self.not_improved_penalty = kwargs.get('not_improved_penalty', 35)

        self.termination_condition = kwargs.get('termination_condition', False)
        self.fitness_function = kwargs.get('fitness_function', lambda *args: np.random.randint(0, 100))
        self.track_performance = kwargs.get('track_performance', True)

        # speciation parameters from paper
        self.c_1 = kwargs.get('c_1', 1)
        self.c_2 = kwargs.get('c_2', 1)
        self.c_3 = kwargs.get('c_3', 0.4)
        self.threshold = kwargs.get('threshold', 3.0)
        self.target_number_of_species = kwargs.get('target_number_of_species', 15)
        self.N = kwargs.get('N', True)

        # initialization parameters
        self.input_n = kwargs.get('input_n', 4)
        self.output_n = kwargs.get('output_n', 2)
        self.hidden_n = kwargs.get('hidden_n', 1)
        self.init_connection_density = kwargs.get('init_connection_density', 0.3)
        self.innov = 1
        self.lookup_table_innov = [[0] * 3000 for _ in range(3000)]
        self.new_node_id = self.input_n + self.output_n + self.hidden_n
        self.lookup_dict_nodes = {}

        population = kwargs.get('population', get_init_population(self))
        self.species = speciation_init(self, population)
        fitness_evaluation(self)

    def get_innov(self, input, output):
        innov = self.lookup_table_innov[input][output]
        if innov == 0:
            innov = self.innov
            self.lookup_table_innov[input][output] = innov
            self.innov += 1
        return innov

    def get_new_node_id(self, node_1, node_2):
        new_node_id = self.lookup_dict_nodes.get((min(node_1, node_2), max(node_1, node_2)), self.new_node_id)
        if new_node_id == self.new_node_id:
            self.new_node_id += 1
        return new_node_id

    def train(self):
        # while not self.termination_condition:
        for i in range(50000):

            print(i,str(max([max(specie.fitness) for specie in neat.species])))
            crossover(self)
            weight_mutation(self)
            topology_mutation(self)
            speciation(self)
            fitness_evaluation(self)
        visualize(neat.species)

    def save_model(self, file_name):
        # saving current population and model parameters to pickle file
        return NotImplementedError

    def return_best_model(self):
        return NotImplementedError

    def track_performance(self):
        return NotImplementedError

    def show_information(self):
        return NotImplementedError


if __name__ == '__main__':
    neat = NEAT(input_n=14*15,
                output_n=4)
    visualize(neat.species)
    individual = neat.species[0].members[0]
    visualize(individual)
    individual.evaluate(neat.input_n,neat.output_n)
    
    print(individual.processing([0]*(14*15)))