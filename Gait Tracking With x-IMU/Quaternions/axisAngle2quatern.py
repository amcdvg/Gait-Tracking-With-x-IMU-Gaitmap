import numpy as np

def axisAngle2quatern(axis, angle):
    q0 = np.cos(angle / 2.0)
    q1 = -axis[:, 0] * np.sin(angle / 2.0)
    q2 = -axis[:, 1] * np.sin(angle / 2.0)
    q3 = -axis[:, 2] * np.sin(angle / 2.0)
    
    # If q0, q1, q2, q3 are 1D arrays of shape (N,), column_stack makes them (N, 4)
    # If they are scalars, we can use np.array
    if np.isscalar(q0):
        q = np.array([q0, q1, q2, q3])
    else:
        q = np.column_stack((q0, q1, q2, q3))
    return q
