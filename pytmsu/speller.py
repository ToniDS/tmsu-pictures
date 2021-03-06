import numpy as np


def damerau_levenstein_distance(a, b):
    d = np.empty([len(a) + 1, len(b) + 1], dtype=int)
    for i in range(0, len(a) + 1):
        d[i, 0] = i
    for j in range(0, len(b) + 1):
        d[0, j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i-1] == b[j-1]:
                cost = 0
            else:
                cost = 1
            d[i, j] = min(d[i-1, j] + 1,  # deletion
                          d[i, j-1] + 1,  # insertion
                          d[i-1, j-1] + cost)  # substition
            if i > 1 and j > 1 and a[i-1] == b[j-2] and a[i-2] == b[j-1]:
                d[i, j] = min(d[i, j], d[i-2, j-2] + cost)  # transposition
    return d[len(a), len(b)]


def test():
    print(damerau_levenstein_distance("test", "tets"))
    print(damerau_levenstein_distance("te", "te"))
    print(damerau_levenstein_distance("Thailand", "Tailan"))
    print(damerau_levenstein_distance("gifts", "profit"))


def spellcheck(tag, all_tags):
    distance = []
    all_tags = list(all_tags)
    for spelling in all_tags:
        distance.append(damerau_levenstein_distance(tag, spelling))
    if 0 in distance:
        return []
    possible_tags = {}
    for i in range(len(distance)):
        if distance[i] <= 2:
            possible_tags[all_tags[i]] = distance[i]
    suggestions = sorted(possible_tags, key=possible_tags.get)
    if len(suggestions) >= 1:
        return suggestions[0]









