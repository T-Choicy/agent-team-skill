def tally_statuses(statuses: list[str]) -> dict[str, int]:
    if type(statuses) is not list:
        raise TypeError("statuses must be a list")

    counts = {"pending": 0, "running": 0, "done": 0, "failed": 0}
    for index, status in enumerate(statuses):
        if type(status) is not str:
            raise TypeError(f"statuses[{index}] must be a string")
        if status not in counts:
            raise ValueError(f"statuses[{index}] must be one of {tuple(counts)}")
        counts[status] += 1
    return counts
