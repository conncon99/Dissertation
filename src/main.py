import random
from utils.game_settings import GameSettings
from utils.game_manager import GameManager
from factions import *
from controllers.random_controllers import *
from controllers.nn_controllers.marquise_nn_controller import MarquiseNNController
import gc
import builtins
from utils.colour_utils import colored_print, original_print
from actions.action_group_registry import ActionGroupRegistry
from controllers.nn_controllers.faction_net import FactionNet
from deap import tools, creator, base
import numpy as np
import torch

builtins.print = colored_print


### TRAINING SETTINGS ###

GENERATIONS = 200
POPULATION_SIZE = 100
TURN_LIMIT = 100
RUN_COUNT = 10
MUTATION_PROB = 0.2

# Create NNs for all factions

models = {
    "marquise": FactionNet(),
    # "eyrie": FactionNet(),
    # "woodland_alliance": FactionNet(),
    # "vagabond": FactionNet()
}

# Initialize DEAP EA

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# Get correct weight size for the neural network
weight_size = sum(p.numel() for p in models["marquise"].parameters())

# Fix population initialization
toolbox.register("attr_float", lambda: np.random.uniform(-1, 1, weight_size))
toolbox.register("individual", tools.initIterate,
                 creator.Individual, toolbox.attr_float)
toolbox.register("population", tools.initRepeat, list,
                 toolbox.individual, n=POPULATION_SIZE)

toolbox.register("mutate", tools.mutGaussian, mu=0,
                 sigma=0.1, indpb=MUTATION_PROB)
toolbox.register("select", tools.selTournament, tournsize=3)


def set_weights(model, weights):
    """Load a flattened weight vector into a PyTorch model."""
    param_shapes = [p.shape for p in model.parameters()]
    param_sizes = [p.numel() for p in model.parameters()]

    if len(weights) != sum(param_sizes):
        raise ValueError(
            f"Weight size mismatch! Expected {sum(param_sizes)}, got {len(weights)}")

    weight_tensors = np.split(weights, np.cumsum(param_sizes)[
                              :-1])  # Split weights correctly

    with torch.no_grad():
        for param, w in zip(model.parameters(), weight_tensors):
            param.copy_(torch.tensor(
                w.reshape(param.shape), dtype=torch.float32))


def get_weights(model):
    """Flatten and return model weights as a 1D vector."""
    return np.concatenate([p.data.numpy().flatten() for p in model.parameters()])


def evaluate_fitness(individual):
    """Runs a game with the given weights and returns fitness score (Victory Points)."""
    faction = "marquise"  # Use a global variable to keep track of the current faction being trained
    set_weights(models[faction], individual)

    # Run a new game instance for evaluation
    marquise = Marquise(MarquiseNNController(models["marquise"]))
    eyrie = EyrieDynasties(EyrieRandomController())
    woodland_alliance = WoodlandAlliance(AllianceRandomController())
    vagabond = Vagabond(VagabondRandomController())

    settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
    game_manager = GameManager(settings, turn_limit=TURN_LIMIT)

    game_manager.run_game()

    # Return VP as fitness score
    return game_manager.game_state.marquise.victory_points,


### TRAINING LOOP ###
for faction in models.keys():
    toolbox.register("evaluate", evaluate_fitness)

    # Initialize population
    population = toolbox.population()

    for gen in range(GENERATIONS):
        original_print(f"[{faction.upper()}] Generation {gen + 1}")

        # Setup fresh game with NN-controlled factions
        marquise = Marquise(MarquiseNNController(models["marquise"]))
        eyrie = EyrieDynasties(EyrieRandomController())
        woodland_alliance = WoodlandAlliance(AllianceRandomController())
        vagabond = Vagabond(VagabondRandomController())

        settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
        game_manager = GameManager(settings, turn_limit=TURN_LIMIT)

        # Evaluate all individuals
        fitnesses = list(map(toolbox.evaluate, population)
                         )  # Now map() works correctly
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        # Select and mutate new population
        selected = toolbox.select(population, len(population))
        offspring = list(map(toolbox.clone, selected))

        for mutant in offspring:
            if random.random() < MUTATION_PROB:
                toolbox.mutate(mutant)
                del mutant.fitness.values  # Reset fitness

        # Replace old population with offspring
        population[:] = offspring

        # Print best fitness
        best_ind = tools.selBest(population, 1)[0]
        original_print(
            f"[{faction.upper()}] Best fitness: {best_ind.fitness.values[0]}")

    # Load best model weights
    set_weights(models[faction], best_ind)

original_print("Training complete. Running test games...")


# def clean_up(marquise, eyrie, woodland_alliance, vagabond, settings, game_manager):
#     del marquise
#     del eyrie
#     del woodland_alliance
#     del vagabond
#     del settings
#     del game_manager
#     ActionGroupRegistry.reset()
#     gc.collect()


# for i in range(RUN_COUNT):
#     original_print(f"RUN {i}")
#     marquise = Marquise(MarquiseRandomController())
#     eyrie = EyrieDynasties(EyrieRandomController())
#     woodland_alliance = WoodlandAlliance(AllianceRandomController())
#     vagabond = Vagabond(VagabondRandomController())
#     settings = GameSettings([vagabond, marquise, eyrie, woodland_alliance])
#     game_manager = GameManager(settings, turn_limit=TURN_LIMIT)
#     game_manager.run_game()
#     # clean_up(marquise, eyrie, woodland_alliance,
#     #          vagabond, settings, game_manager)
