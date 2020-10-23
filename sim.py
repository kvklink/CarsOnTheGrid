import multiprocessing as mp

from main import *


def run(amount: int) -> [int]:
    result = []
    for count in range(amount):
        RAND_SEED = "%.30f" % time()
        print(count, RAND_SEED)

        simulation = RWP2DSimulation(RAND_SEED, SOURCE_POS, SOURCE_TARGETS)
        simulation.simulate()
        rounds = len(simulation.num_of_broadcasters) - 1
        result.append(rounds)

    return result


if __name__ == '__main__':
    # Simulation settings
    # MAKE SURE VARIABLES IN HELP.PY ARE ALSO CORRECT
    # EXCEED_MOVES must be set to True
    SOURCE_POS = (0, 0)
    SOURCE_TARGETS = None
    TOTAL_SIMULATION_COUNT = 10000

    cpus = mp.cpu_count()
    print(f'Amount of cores available: {cpus}')
    L = list(range(cpus))
    chunk_size = TOTAL_SIMULATION_COUNT // cpus
    chunks = [chunk_size for i in range(cpus)]
    for i in range(TOTAL_SIMULATION_COUNT % cpus):
        chunks[i] += 1

    p = mp.Pool(cpus, initargs=(mp.RLock(),))
    results = p.map(run, chunks)
    p.close()
    p.join()

    # Flatten all result arrays into one
    results = [item for sublist in results for item in sublist]

    print(f'Average number of rounds: {sum(results) / len(results)}')
