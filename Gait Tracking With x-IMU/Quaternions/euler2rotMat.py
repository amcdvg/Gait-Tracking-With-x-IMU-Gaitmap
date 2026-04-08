import numpy as np

def euler2rotMat(phi, theta, psi):
    # In MATLAB this was creating a 3x3xN matrix automatically.
    n_samples = phi.shape[0] if not np.isscalar(phi) else 1
    
    if n_samples == 1:
        R = np.zeros((3, 3))
        R[0, 0] = np.cos(psi) * np.cos(theta)
        R[0, 1] = -np.sin(psi) * np.cos(phi) + np.cos(psi) * np.sin(theta) * np.sin(phi)
        R[0, 2] = np.sin(psi) * np.sin(phi) + np.cos(psi) * np.sin(theta) * np.cos(phi)
        
        R[1, 0] = np.sin(psi) * np.cos(theta)
        R[1, 1] = np.cos(psi) * np.cos(phi) + np.sin(psi) * np.sin(theta) * np.sin(phi)
        R[1, 2] = -np.cos(psi) * np.sin(phi) + np.sin(psi) * np.sin(theta) * np.cos(phi)
        
        R[2, 0] = -np.sin(theta)
        R[2, 1] = np.cos(theta) * np.sin(phi)
        R[2, 2] = np.cos(theta) * np.cos(phi)
    else:
        R = np.zeros((3, 3, n_samples))
        R[0, 0, :] = np.cos(psi) * np.cos(theta)
        R[0, 1, :] = -np.sin(psi) * np.cos(phi) + np.cos(psi) * np.sin(theta) * np.sin(phi)
        R[0, 2, :] = np.sin(psi) * np.sin(phi) + np.cos(psi) * np.sin(theta) * np.cos(phi)
        
        R[1, 0, :] = np.sin(psi) * np.cos(theta)
        R[1, 1, :] = np.cos(psi) * np.cos(phi) + np.sin(psi) * np.sin(theta) * np.sin(phi)
        R[1, 2, :] = -np.cos(psi) * np.sin(phi) + np.sin(psi) * np.sin(theta) * np.cos(phi)
        
        R[2, 0, :] = -np.sin(theta)
        R[2, 1, :] = np.cos(theta) * np.sin(phi)
        R[2, 2, :] = np.cos(theta) * np.cos(phi)
        
    return R
