from NEAT.Evolutionary_operators.weight_mutation import weight_mutation
from NEAT.Evolutionary_operators.topology_mutation import topology_mutation
from NEAT.Evolutionary_operators.crossover import crossover
from NEAT.Evolutionary_operators.speciation import speciation_init, speciation
from NEAT.Evolutionary_operators.fitness_evaluation import fitness_evaluation
from NEAT.Evolutionary_operators.selection import selection
from NEAT.utils.initialize_population import get_init_population
from NEAT.utils.termination_conditions import iteration
from NEAT.utils.visualization import visualize
from benchmarks.xor import xor, xor_as_Kenneth_said
from benchmarks.frogger_benchmark import frogbenchMultiprocess
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")
from tqdm import trange


class NEAT:
    def __init__(self, **kwargs):
        self.pop_size = kwargs.get('pop_size', 100)

        # Mutation parameters
        self.probability_of_small_weight_mutation = kwargs.get('probability_of_small_weight_mutation', 0.8 * 0.9)
        self.probability_of_total_weight_mutation = kwargs.get('probability_of_total_weight_mutation', 0.8 * 0.2)

        self.probability_of_adding_a_node = kwargs.get('probability_of_adding_a_node', 0.05)
        self.probability_of_adding_a_connection = kwargs.get('probability_of_adding_a_connection', 0.05)

        self.elitism = kwargs.get('elitism', 3)
        self.not_improved_penalty = kwargs.get('not_improved_penalty', 15)

        self.termination_condition = kwargs.get('termination_condition', False)
        self.fitness_function = kwargs.get('fitness_function', lambda *args: np.random.randint(0, 100))
        self.track_performance = kwargs.get('track_performance', True)

        # speciation parameters from paper
        self.c_1 = kwargs.get('c_1', 1)
        self.c_2 = kwargs.get('c_2', 1)
        self.c_3 = kwargs.get('c_3', 0.4)
        self.threshold = kwargs.get('threshold', 3.0)
        self.target_number_of_species = kwargs.get('target_number_of_species', 7)
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
        self.threads = kwargs.get('threads', 12)
        self.info = {}

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

    def collect_info(self):
        self.info.setdefault('threshold', []).append(self.threshold)
        self.info.setdefault('num_of_species', []).append(len(self.species))
        self.info.setdefault('best_score', []).append(max([max(specie.fitness) for specie in self.species]))

    def train(self):
        # while not self.termination_condition:
        for i in range(11):
            best_1 = -100
            for specie in neat.species:
                best_1 = max(max(specie.fitness), best_1)
            print(i, best_1, len(self.species))
            if i % 5 == 0:
                visualize(neat.species)
            crossover(self)
            weight_mutation(self)
            topology_mutation(self)
            speciation(self)
            fitness_evaluation(self)
            self.collect_info()

        self.show_info()
        visualize(neat.species)

    def save_model(self, file_name):
        # saving current population and model parameters to pickle file
        return NotImplementedError

    def return_best_model(self):
        return NotImplementedError

    def track_performance(self):
        return NotImplementedError

    def show_info(self):
        fig, axs = plt.subplots(3)
        x = np.arange(len(self.info['threshold']))
        axs[0].plot(x, self.info['threshold'])
        axs[0].set_title('threshold')
        axs[1].plot(x, self.info['num_of_species'])
        axs[1].plot(x, np.ones(len(self.info['threshold'])) * self.target_number_of_species, c='r')
        axs[1].set_title('num_of_species')
        axs[2].plot(x, self.info['best_score'])
        axs[2].set_title('best_score')
        fig.tight_layout()
        plt.show()


if __name__ == '__main__':
    np.random.seed(0)
    # neat = NEAT(input_n=2,
    #             hidden_n=2,
    #             output_n=1,
    #             pop_size=200,
    #             target_number_of_species=7,
    #             fitness_function=xor,
    #             c_1=1,
    #             c_2=1,
    #             c_3=1)
    # neat.train()%

    neat = NEAT(input_n=13 * 15,
                output_n=4,
                pop_size=200,
                threshold=5,
                threads=12,
                fitness_function=frogbenchMultiprocess)
    neat.train()
