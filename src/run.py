import argparse
import os
import time
import networkx as nx
import pandas as pd
from simulator import run_parallel_simulations


def main():
    parser = argparse.ArgumentParser(
        description="Monte Carlo simulations of fake news spread on a social network"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=400,
        help="Total number of simulations to run for each parameter set",
    )
    parser.add_argument(
        "--workers", type=int, default=4, help="CPU cores"
    )
    parser.add_argument(
        "--task-id",
        type=int,
        default=0,
        help="Slurm task ID",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="folder to save results",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(
        f"[Task {args.task_id}] graph loading and start on {args.workers} cores..."
    )
    G = nx.read_edgelist("data/facebook_combined.txt", nodetype=int)
    adj_list = {node: list(G.neighbors(node)) for node in G.nodes()}
    all_nodes = list(G.nodes())

    strategies = ["none", "random", "acquaintance", "hubs"]
    betas = [0.01, 0.015, 0.02, 0.03, 0.05, 0.08]
    gamma = 0.20

    all_records = []
    start_time = time.time()

    for beta in betas:
        for strategy in strategies:
            t0 = time.time()
            seed = 100000 * args.task_id + int(beta * 10000)

            raw_results = run_parallel_simulations(
                adj_list=adj_list,
                all_nodes=all_nodes,
                beta=beta,
                gamma=gamma,
                strategy=strategy,
                fraction=0.05,
                total_runs=args.runs,
                n_workers=args.workers,
                base_seed=seed,
            )

            for pct_reached, peak, steps in raw_results:
                all_records.append({
                    "task_id": args.task_id,
                    "beta": beta,
                    "strategy": strategy,
                    "pct_reached": round(pct_reached, 3),
                    "peak_spreaders": peak,
                    "duration": steps,
                })

            print(
                f"  beta={beta:.3f} | strategy={strategy:12s} | {args.runs} simulations in {time.time() - t0:.2f}s"
            )

    df = pd.DataFrame(all_records)
    out_file = os.path.join(args.output_dir, f"sim_part_{args.task_id}.csv")
    df.to_csv(out_file, index=False)

    total_sims = len(df)
    elapsed = time.time() - start_time
    print(
        f"\n completed {total_sims} simulations in {elapsed:.2f}s ({total_sims/elapsed:.0f} sim/s)."
    )
    print(f"Save output to: {out_file}")


if __name__ == "__main__":
    main()