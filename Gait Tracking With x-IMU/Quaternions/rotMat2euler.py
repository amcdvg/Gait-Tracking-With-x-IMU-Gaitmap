import numpy as np

def rotMat2euler(R):
    # In Python, if R is 3x3, ndim is 2. If it is 3x3xN, ndim is 3.
    if R.ndim == 2:
        phi = np.arctan2(R[2, 1], R[2, 2])
        theta = -np.arctan(R[2, 0] / np.sqrt(1 - R[2, 0]**2))
        psi = np.arctan2(R[1, 0], R[0, 0])
        euler = np.array([phi, theta, psi])
    else:
        phi = np.arctan2(R[2, 1, :], R[2, 2, :])
        theta = -np.arctan(R[2, 0, :] / np.sqrt(1 - R[2, 0, :]**2))
        psi = np.arctan2(R[1, 0, :], R[0, 0, :])
        euler = np.column_stack((phi, theta, psi))
        
    return euler
