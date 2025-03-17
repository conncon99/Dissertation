import os
import random
import numpy as np
import torch
import matplotlib.pyplot as plt
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from deap import tools, creator, base, algorithms
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
# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DEVICE = torch.device("cpu")
original_print(f"Using device: {DEVICE}")

### **TRAINING SETTINGS** ###
GENERATIONS = 1
POPULATION_SIZE = 10
TURN_LIMIT = 100
RUN_COUNT = 10
MUTATION_PROB = 0.5
GAMES_PER_INDIVIDUAL = 4  # Run 4 games per individual for more stable fitness
# Use max CPU cores - 1 for multiprocessing
NUM_WORKERS = max(1, cpu_count() - 1)

original_print(f"Using {NUM_WORKERS} CPU cores for parallel processing")

# Initialize Neural Networks for factions and move them to GPU
models = {
    "marquise": FactionNet().to(DEVICE),
}


def save_model(model, filename="marquise_nn.pth"):
    """Saves the trained model to a file."""
    os.makedirs("saved_models", exist_ok=True)  # Ensure directory exists
    filepath = os.path.join("saved_models", filename)
    torch.save(model.state_dict(), filepath)
    original_print(f"✅ Model saved to {filepath}")


def load_model(model, filename="marquise_nn.pth"):
    """Loads the trained model if it exists."""
    filepath = os.path.join("saved_models", filename)
    if os.path.exists(filepath):
        model.load_state_dict(torch.load(filepath, map_location=DEVICE))
        model.eval()  # Set to evaluation mode
        original_print(f"✅ Loaded model from {filepath}")
        models["marquise"] = model
    else:
        original_print("⚠ No saved model found, starting fresh.")


# Load model if it exists
# load_model(models["marquise"])

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

### **Matplotlib Setup for Live Graphing (ONLY IN MAIN PROCESS)** ###
if __name__ == "__main__":
    plt.ion()
    fig, ax = plt.subplots()


def update_plot(generations, avg_fitness, best_fitness, worst_fitness, std_dev):
    """Update the fitness graph during training (Only in main process)."""
    if __name__ == "__main__":
        ax.clear()
        ax.plot(generations, avg_fitness,
                label="Average Fitness", color="blue")
        ax.plot(generations, best_fitness, label="Best Fitness", color="green")
        ax.plot(generations, worst_fitness, label="Worst Fitness", color="red")
        ax.fill_between(generations, np.array(avg_fitness) - np.array(std_dev),
                        np.array(avg_fitness) + np.array(std_dev), color='blue', alpha=0.2)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Fitness Score (Victory Points)")
        ax.set_title("Evolutionary Training Progress")
        ax.legend()
        plt.draw()
        plt.pause(0.1)

### **Weight Management Functions** ###


def set_weights(model, weights):
    """Load a flattened weight vector into a PyTorch model on GPU."""
    param_shapes = [p.shape for p in model.parameters()]
    param_sizes = [p.numel() for p in model.parameters()]

    if len(weights) != sum(param_sizes):
        raise ValueError(
            f"Weight size mismatch! Expected {sum(param_sizes)}, got {len(weights)}")

    weight_tensors = np.split(weights, np.cumsum(param_sizes)[
                              :-1])  # Split weights correctly

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
    set_weights(models[faction], individual)

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


if __name__ == "__main__":
    ## **TRAINING LOOP** ###
    try:
        pool = Pool(NUM_WORKERS)
        toolbox.register("map", pool.map)
        for faction in models.keys():
            toolbox.register("evaluate", evaluate_fitness)

            # Initialize population
            population = toolbox.population()
            hof = tools.HallOfFame(1)
            stats = tools.Statistics(lambda ind: ind.fitness.values)
            stats.register("avg", np.mean)
            stats.register("std", np.std)
            stats.register("min", np.min)
            stats.register("max", np.max)

            algorithms.eaSimple(population, toolbox, cxpb=0.0, mutpb=MUTATION_PROB,
                                ngen=GENERATIONS, stats=stats, halloffame=hof, verbose=2)

            # gen_x = []
            # avg_fitness_y = []
            # best_fitness_y = []
            # worst_fitness_y = []
            # std_dev_y = []

            # for gen in range(GENERATIONS):
            #     original_print(f"[{faction.upper()}] Generation {gen + 1}")

            #     # Evaluate all individuals in parallel
            #     fitnesses = list(tqdm(pool.imap(toolbox.evaluate, population), total=len(
            #         population), desc="Evaluating"))

            #     for ind, fit in zip(population, fitnesses):
            #         ind.fitness.values = fit

            #     # Collect statistics
            #     fitness_scores = [ind.fitness.values[0] for ind in population]
            #     avg_fitness = np.mean(fitness_scores)
            #     best_fitness = np.max(fitness_scores)
            #     worst_fitness = np.min(fitness_scores)
            #     std_dev = np.std(fitness_scores)

            #     original_print(
            #         f"Avg: {avg_fitness:.2f} | Best: {best_fitness:.2f} | Worst: {worst_fitness:.2f} | Std Dev: {std_dev:.2f}")

            #     # Update graph data
            #     gen_x.append(gen)
            #     avg_fitness_y.append(avg_fitness)
            #     best_fitness_y.append(best_fitness)
            #     worst_fitness_y.append(worst_fitness)
            #     std_dev_y.append(std_dev)

            #     # Live update of graph (Only in main process)
            #     update_plot(gen_x, avg_fitness_y, best_fitness_y,
            #                 worst_fitness_y, std_dev_y)

            #     # Select and mutate new population
            #     selected = toolbox.select(population, len(population))
            #     offspring = list(map(toolbox.clone, selected))

            #     for mutant in offspring:
            #         if random.random() < MUTATION_PROB:
            #             toolbox.mutate(mutant)
            #             del mutant.fitness.values

            #     # Replace old population with offspring
            #     population[:] = offspring

            #     # Print best fitness
            #     best_ind = tools.selBest(population, 1)[0]
            #     original_print(
            #         f"[{faction.upper()}] Best fitness: {best_ind.fitness.values[0]}")

            # # Save trained model
            # save_model(models[faction])
            pool.close()

        original_print("Training complete. Running test games...")
        plt.ioff()
        plt.show()
        load_model(models["marquise"])
        marquise = Marquise(MarquiseNNController(models["marquise"]))
        eyrie = EyrieDynasties(EyrieRandomController())
        woodland_alliance = WoodlandAlliance(AllianceRandomController())
        vagabond = Vagabond(VagabondRandomController())

        settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
        game_manager = GameManager(settings, turn_limit=TURN_LIMIT)

        game_manager.run_game()
    except KeyboardInterrupt:
        pool.close()
