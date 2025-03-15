import random
import numpy as np
import torch
import matplotlib.pyplot as plt
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from deap import tools, creator, base
from utils.game_settings import GameSettings
from utils.game_manager import GameManager
from factions import *
from controllers.random_controllers import *
from controllers.nn_controllers.marquise_nn_controller import MarquiseNNController
from controllers.nn_controllers.faction_net import FactionNet
import gc
import builtins
from utils.colour_utils import colored_print, original_print
from actions.action_group_registry import ActionGroupRegistry

builtins.print = colored_print

### **GPU CHECK & SETUP** ###
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
original_print(f"Using device: {DEVICE}")

### **TRAINING SETTINGS** ###
GENERATIONS = 200
POPULATION_SIZE = 100
TURN_LIMIT = 100
RUN_COUNT = 10
MUTATION_PROB = 0.2
GAMES_PER_INDIVIDUAL = 4  # Run 4 games per individual for more stable fitness
# Use max CPU cores - 1 for multiprocessing
NUM_WORKERS = max(1, cpu_count() - 1)

original_print(f"Using {NUM_WORKERS} CPU cores for parallel processing")

# Initialize Neural Networks for factions and move them to GPU
models = {
    "marquise": FactionNet().to(DEVICE),
}

# Initialize DEAP Evolutionary Algorithm
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
weight_size = sum(p.numel() for p in models["marquise"].parameters())

toolbox.register("attr_float", lambda: np.random.uniform(-1, 1, weight_size))
toolbox.register("individual", tools.initIterate,
                 creator.Individual, toolbox.attr_float)
toolbox.register("population", tools.initRepeat, list,
                 toolbox.individual, n=POPULATION_SIZE)

toolbox.register("mutate", tools.mutGaussian, mu=0,
                 sigma=0.1, indpb=MUTATION_PROB)
toolbox.register("select", tools.selTournament, tournsize=3)

### **Matplotlib Setup for Live Graphing** ###


def setup_plot():
    plt.ion()
    fig, ax = plt.subplots()
    return fig, ax


def update_plot(ax, gen_x, avg_fitness_y, best_fitness_y, worst_fitness_y, std_dev_y):
    """Update the fitness graph during training."""
    ax.clear()
    ax.plot(gen_x, avg_fitness_y, label="Average Fitness", color="blue")
    ax.plot(gen_x, best_fitness_y, label="Best Fitness", color="green")
    ax.plot(gen_x, worst_fitness_y, label="Worst Fitness", color="red")
    ax.fill_between(gen_x, np.array(avg_fitness_y) - np.array(std_dev_y),
                    np.array(avg_fitness_y) + np.array(std_dev_y), color='blue', alpha=0.2)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness Score (Victory Points)")
    ax.set_title("Evolutionary Training Progress")
    ax.legend()
    plt.pause(0.1)

### **GPU-Optimized Weight Handling** ###


def set_weights(model, weights):
    """Load a flattened weight vector into a PyTorch model on GPU."""
    param_shapes = [p.shape for p in model.parameters()]
    param_sizes = [p.numel() for p in model.parameters()]

    if len(weights) != sum(param_sizes):
        raise ValueError(
            f"Weight size mismatch! Expected {sum(param_sizes)}, got {len(weights)}")

    weight_tensors = np.split(weights, np.cumsum(param_sizes)[:-1])

    with torch.no_grad():
        for param, w in zip(model.parameters(), weight_tensors):
            param.copy_(torch.tensor(w.reshape(param.shape),
                        dtype=torch.float32, device=DEVICE))


def get_weights(model):
    """Flatten and return model weights as a 1D NumPy array."""
    return np.concatenate([p.data.cpu().numpy().flatten() for p in model.parameters()])

### **Optimized Fitness Function: Average Over Multiple Games on GPU** ###


def evaluate_fitness(individual):
    """Runs multiple games with the same weights and returns the average fitness."""
    faction = "marquise"
    set_weights(models[faction], individual)  # Move weights to GPU

    total_vp = 0  # Total victory points

    for _ in range(GAMES_PER_INDIVIDUAL):
        marquise = Marquise(MarquiseNNController(models["marquise"]))
        eyrie = EyrieDynasties(EyrieRandomController())
        woodland_alliance = WoodlandAlliance(AllianceRandomController())
        vagabond = Vagabond(VagabondRandomController())

        settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
        game_manager = GameManager(settings, turn_limit=TURN_LIMIT)

        game_manager.run_game()

        total_vp += game_manager.game_state.marquise.victory_points

    # Average victory points over multiple games
    avg_vp = total_vp / GAMES_PER_INDIVIDUAL
    return avg_vp,


def parallel_evaluate(population):
    """Evaluate individuals in parallel using multiprocessing."""
    with Pool(processes=NUM_WORKERS) as pool:
        results = list(tqdm(pool.imap(toolbox.evaluate, population),
                       total=len(population), desc="Evaluating"))
    return results


if __name__ == "__main__":
    fig, ax = setup_plot()

    ### **TRAINING LOOP** ###
    for faction in models.keys():
        toolbox.register("evaluate", evaluate_fitness)

        # Initialize population
        population = toolbox.population()

        gen_x = []
        avg_fitness_y = []
        best_fitness_y = []
        worst_fitness_y = []
        std_dev_y = []

        for gen in range(GENERATIONS):
            original_print(f"[{faction.upper()}] Generation {gen + 1}")

            # Evaluate all individuals in parallel
            fitnesses = parallel_evaluate(population)
            for ind, fit in zip(population, fitnesses):
                ind.fitness.values = fit

            # Collect statistics
            fitness_scores = [ind.fitness.values[0] for ind in population]
            avg_fitness = np.mean(fitness_scores)
            best_fitness = np.max(fitness_scores)
            worst_fitness = np.min(fitness_scores)
            std_dev = np.std(fitness_scores)

            original_print(
                f"Avg: {avg_fitness:.2f} | Best: {best_fitness:.2f} | Worst: {worst_fitness:.2f} | Std Dev: {std_dev:.2f}")

            # Select and mutate new population
            selected = toolbox.select(population, len(population))
            offspring = list(map(toolbox.clone, selected))

            for mutant in offspring:
                if random.random() < MUTATION_PROB:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Replace old population with offspring
            population[:] = offspring

            # Print best fitness
            best_ind = tools.selBest(population, 1)[0]
            original_print(
                f"[{faction.upper()}] Best fitness: {best_ind.fitness.values[0]}")

        # Load best model weights
        set_weights(models[faction], best_ind)

    original_print("Training complete. Running test games...")
    plt.ioff()
    plt.show()
