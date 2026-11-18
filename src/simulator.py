import multiprocessing as mp
import random
from strategies import get_immunized_nodes


def run_single_simulation(adj_list, all_nodes, beta, gamma, initial_spreaders, immunized):
    """Simulates a single run of the SIR model for fake news spread."""
    available_nodes = [n for n in all_nodes if n not in immunized]
    spreaders = set(random.sample(available_nodes, initial_spreaders))
    stiflers = set(immunized)

    total_believed = len(spreaders)
    peak_spreaders = len(spreaders)
    steps = 0

    while spreaders:
        steps += 1
        new_spreaders = set()
        new_stiflers = set()

        for user in spreaders:
            for friend in adj_list[user]:
                if (
                    friend not in spreaders
                    and friend not in stiflers
                    and friend not in new_spreaders
                ):
                    if random.random() < beta:
                        new_spreaders.add(friend)

            if random.random() < gamma:
                new_stiflers.add(user)

        spreaders = (spreaders - new_stiflers) | new_spreaders
        stiflers = stiflers | new_stiflers
        total_believed += len(new_spreaders)

        if len(spreaders) > peak_spreaders:
            peak_spreaders = len(spreaders)

    return (
        (total_believed / len(all_nodes)) * 100.0,  # % of network reached
        peak_spreaders,  # peak number of spreaders
        steps,  # wave duration in steps
    )


def _worker_batch(args):
    """One worker runs a batch of simulations with the same parameters"""
    adj_list, all_nodes, beta, gamma, strategy, fraction, n_runs, seed = args
    random.seed(seed)

    results = []
    fixed_immunized = (
        get_immunized_nodes(adj_list, all_nodes, strategy, fraction)
        if strategy in ("none", "hubs")
        else None
    )

    for _ in range(n_runs):
        immunized = (
            fixed_immunized
            if fixed_immunized is not None
            else get_immunized_nodes(adj_list, all_nodes, strategy, fraction)
        )
        res = run_single_simulation(
            adj_list, all_nodes, beta, gamma, 5, immunized
        )
        results.append(res)

    return results


def run_parallel_simulations(
    adj_list,
    all_nodes,
    beta,
    gamma,
    strategy,
    fraction=0.05,
    total_runs=1000,
    n_workers=4,
    base_seed=42,
):
    runs_per_worker = total_runs // n_workers
    remainder = total_runs % n_workers

    tasks = []
    for i in range(n_workers):
        runs = runs_per_worker + (1 if i < remainder else 0)
        if runs > 0:
            tasks.append((
                adj_list,
                all_nodes,
                beta,
                gamma,
                strategy,
                fraction,
                runs,
                base_seed + i,
            ))

    with mp.Pool(processes=n_workers) as pool:
        batch_results = pool.map(_worker_batch, tasks)

    return [item for sublist in batch_results for item in sublist]