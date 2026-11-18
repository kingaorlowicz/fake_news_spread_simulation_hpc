import random


def get_immunized_nodes(adj_list, all_nodes, strategy="none", fraction=0.05):
    """set ID immunized nodes before the start of the fake news wave"""
    if strategy == "none" or fraction <= 0:
        return set()

    budget = int(len(all_nodes) * fraction)

    if strategy == "random":
        return set(random.sample(all_nodes, budget))

    elif strategy == "hubs":
        sorted_nodes = sorted(
            all_nodes, key=lambda n: len(adj_list[n]), reverse=True
        )
        return set(sorted_nodes[:budget])

    elif strategy == "acquaintance":
        immunized = set()
        while len(immunized) < budget:
            random_user = random.choice(all_nodes)
            friends = adj_list[random_user]
            if friends:
                chosen_friend = random.choice(friends)
                immunized.add(chosen_friend)
        return immunized

    else:
        raise ValueError(f"Unknown strategy: {strategy}")