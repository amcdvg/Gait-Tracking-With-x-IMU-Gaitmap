import numpy as np

def quaternConj(q):
    if len(np.shape(q)) == 1:
        qConj = np.array([q[0], -q[1], -q[2], -q[3]])
    else:
        qConj = np.column_stack((q[:, 0], -q[:, 1], -q[:, 2], -q[:, 3]))
    return qConj
