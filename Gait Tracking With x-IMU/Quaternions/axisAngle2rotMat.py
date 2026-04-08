import numpy as np

def axisAngle2rotMat(axis, angle):
    kx = axis[:, 0]
    ky = axis[:, 1]
    kz = axis[:, 2]
    cT = np.cos(angle)
    sT = np.sin(angle)
    vT = 1 - np.cos(angle)
    
    n_samples = kx.shape[0] if not np.isscalar(kx) else 1
    
    if n_samples == 1:
        R = np.zeros((3, 3))
        R[0, 0] = kx * kx * vT + cT
        R[0, 1] = kx * ky * vT - kz * sT
        R[0, 2] = kx * kz * vT + ky * sT
        
        R[1, 0] = kx * ky * vT + kz * sT
        R[1, 1] = ky * ky * vT + cT
        R[1, 2] = ky * kz * vT - kx * sT
        
        R[2, 0] = kx * kz * vT - ky * sT
        R[2, 1] = ky * kz * vT + kx * sT
        R[2, 2] = kz * kz * vT + cT
    else:
        R = np.zeros((3, 3, n_samples))
        R[0, 0, :] = kx * kx * vT + cT
        R[0, 1, :] = kx * ky * vT - kz * sT
        R[0, 2, :] = kx * kz * vT + ky * sT
        
        R[1, 0, :] = kx * ky * vT + kz * sT
        R[1, 1, :] = ky * ky * vT + cT
        R[1, 2, :] = ky * kz * vT - kx * sT
        
        R[2, 0, :] = kx * kz * vT - ky * sT
        R[2, 1, :] = ky * kz * vT + kx * sT
        R[2, 2, :] = kz * kz * vT + cT
        
    return R
