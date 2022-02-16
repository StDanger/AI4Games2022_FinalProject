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
from benchmarks.frogger_benchmark import frogbenchMultiprocess, frogBenchSingleVisualize
import numpy as np
import random
import matplotlib.pyplot as plt
import warnings
import pickle
import datetime

warnings.filterwarnings("ignore")
from tqdm import trange


class NEAT:
    def __init__(self, **kwargs):
        self.pop_size = kwargs.get('pop_size', 100)

        # Mutation parameters
        self.probability_of_small_weight_mutation = kwargs.get('probability_of_small_weight_mutation', 0.7 * 0.9)
        self.probability_of_total_weight_mutation = kwargs.get('probability_of_total_weight_mutation', 0.7 * 0.1)

        self.probability_of_adding_a_node = kwargs.get('probability_of_adding_a_node', 0.08)
        self.probability_of_adding_a_connection = kwargs.get('probability_of_adding_a_connection', 0.08)

        self.elitism = kwargs.get('elitism', 3)
        self.not_improved_penalty = kwargs.get('not_improved_penalty', 25)

        self.termination_condition = kwargs.get('termination_condition', False)
        self.fitness_function = kwargs.get('fitness_function', lambda *args: np.random.randint(0, 100))

        # speciation parameters from paper
        self.c_1 = kwargs.get('c_1', 1)
        self.c_2 = kwargs.get('c_2', 1)
        self.c_3 = kwargs.get('c_3', 1)
        self.threshold = kwargs.get('threshold', 3.0)
        self.target_number_of_species = kwargs.get('target_number_of_species', 10)
        self.N = kwargs.get('N', True)

        # initialization parameters
        self.input_n = kwargs.get('input_n', 4)
        self.output_n = kwargs.get('output_n', 2)
        self.hidden_n = kwargs.get('hidden_n', 1)
        self.init_connection_density = kwargs.get('init_connection_density', 0.3)
        self.innov = 1
        self.lookup_table_innov = {}
        self.new_node_id = self.input_n + self.output_n + self.hidden_n
        self.lookup_dict_nodes = {}
        self.threads = kwargs.get('threads', 12)
        self.info = {}
        self.verbose = True
        self.generations = kwargs.get('generations', 100)
        self.best_so_far = -np.inf
        self.init_time = datetime.datetime.now()

        population = kwargs.get('population', get_init_population(self))
        self.species = speciation_init(self, population)
        fitness_evaluation(self)

    def get_innov(self, input, output):
        innov = self.lookup_table_innov.get((input, output), 0)
        if innov == 0:
            innov = self.innov
            self.lookup_table_innov[(input, output)] = innov
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
        self.info.setdefault('avg_score', []).append(
            np.mean([val for specie in self.species for val in specie.fitness]))

    def save_model(self, name=None):
        # saving current population and model parameters to pickle file
        if not name:
            now = datetime.datetime.now()
            name = 'neat_' + now.strftime("%Y-%m-%d_%H-%M")
        pickle_out = open('../logs/Models/' + name + '_' + str(self.best_so_far) + '.pickle', 'wb')
        pickle.dump(self, pickle_out)
        pickle_out.close()

    def save_best_individual(self, name=None):
        if not name:
            now = datetime.datetime.now()
            name = 'individual_' + now.strftime("%Y-%m-%d_%H-%M")
        max_val = -np.inf
        best_ind = None
        for specie in self.species:
            for val, ind in zip(specie.fitness, specie.members):
                if max_val < val:
                    max_val = val
                    best_ind = ind
        assert max_val != -np.inf
        max_val = str(int(max_val))[:5]
        pickle_out = open('../logs/Best_individuals/' + name + '_' + max_val + '.pickle', 'wb')
        pickle.dump(best_ind, pickle_out)
        pickle_out.close()

    def show_info(self):
        fig, axs = plt.subplots(3)
        x = np.arange(len(self.info['threshold']))
        axs[0].plot(x, self.info['threshold'])
        axs[0].set_title('threshold')
        axs[1].plot(x, self.info['num_of_species'])
        axs[1].plot(x, np.ones(len(self.info['threshold'])) * self.target_number_of_species, c='r')
        axs[1].set_title('num_of_species')
        axs[2].plot(x, self.info['best_score'])
        axs[2].plot(x, self.info['avg_score'], c='r')
        axs[2].set_title('best_score / avg_score')
        fig.tight_layout()
        plt.show()
        print(self.info['threshold'])
        print(self.info['num_of_species'])
        print(self.info['best_score'])
        print(self.info['avg_score'])

    def track_performance(self, i):
        # Computing data for current generation
        if i==0:
            print('Generation | best score | #of species | threshold')
        show_game = False
        for specie in neat.species:
            b = max(specie.fitness)
            if b > self.best_so_far:
                self.best_so_far = b
                show_game = True
        print(i, self.best_so_far, len(self.species), self.threshold)

        # If current generation made a improvement it will show the gameplay
        individual = None
        best = 0
        if show_game:
            for specie in neat.species:
                for member, fitness in zip(specie.members, specie.fitness):
                    if fitness > best:
                        best = fitness
                        individual = member
            individual.evaluate()
            frogBenchSingleVisualize(individual.processing, timeScaling=1)

            # saving model in pickle file, once in a hundred generations
        if (i + 1) % 5 == 0:
            self.save_model('neat_' + self.init_time.strftime("%Y-%m-%d_%H-%M"))
            visualize(self.species)

    @staticmethod
    def load_model(path):
        pickle_in = open(path, 'rb')
        neat_instance = pickle.load(pickle_in)
        return neat_instance

    def train(self):
        for i in range(self.generations):
            if self.verbose:
                self.track_performance(i)
            crossover(self)
            weight_mutation(self)
            topology_mutation(self)
            speciation(self)
            fitness_evaluation(self)
            self.collect_info()
        self.save_model('neat_' + self.init_time.strftime("%Y-%m-%d_%H-%M"))
        self.save_best_individual('individual_' + self.init_time.strftime("%Y-%m-%d_%H-%M"))
        self.show_info()
        visualize(self.species)


if __name__ == '__main__':
    # np.random.seed(111)
    # random.seed(0)
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
                hidden_n=1,
                pop_size=500,
                threshold=5,
                threads=12,
                generations=12,
                not_improved_penalty=15,
                verbose=True,
                fitness_function=frogbenchMultiprocess)
    neat.train()
