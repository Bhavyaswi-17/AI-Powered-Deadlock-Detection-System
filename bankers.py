import numpy as np
def bankers_algorithm(allocation, request, available):
    alloc = allocation.copy()
    req = request.copy()
    avail = available.copy()
    P, R = alloc.shape
    finish = [False]*P
    sequence = []
    changed = True
    while changed:
        changed = False
        for i in range(P):
            if not finish[i]:
                if all(int(req[i,j]) <= int(avail[j]) for j in range(R)):
                    avail = avail + alloc[i]
                    finish[i] = True
                    sequence.append(i)
                    changed = True
    deadlocked = [i for i in range(P) if not finish[i]]
    safe = len(deadlocked)==0
    return safe, sequence, deadlocked
