import numpy as np

def quatern2euler(q):
    # from paper: "Adaptive Filter for a Miniature MEMS Based Attitude and
    # Heading Reference System" by Wang et al, IEEE.
    
    # We construct only the required elements of R to save computation and match MATLAB vectorized operations
    R11 = 2 * q[:, 0]**2 - 1 + 2 * q[:, 1]**2
    R21 = 2 * (q[:, 1] * q[:, 2] - q[:, 0] * q[:, 3])
    R31 = 2 * (q[:, 1] * q[:, 3] + q[:, 0] * q[:, 2])
    R32 = 2 * (q[:, 2] * q[:, 3] - q[:, 0] * q[:, 1])
    R33 = 2 * q[:, 0]**2 - 1 + 2 * q[:, 3]**2
    
    phi = np.arctan2(R32, R33)
    theta = -np.arctan(R31 / np.sqrt(1 - R31**2))
    psi = np.arctan2(R21, R11)
    
    if np.isscalar(phi):
        euler = np.array([phi, theta, psi])
    else:
        euler = np.column_stack((phi, theta, psi))
        
    return euler
