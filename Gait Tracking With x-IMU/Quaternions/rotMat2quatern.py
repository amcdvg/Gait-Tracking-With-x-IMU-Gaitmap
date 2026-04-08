import numpy as np

def rotMat2quatern(R):
    if R.ndim == 2:
        R_3d = R[:, :, np.newaxis]
    else:
        R_3d = R
        
    numR = R_3d.shape[2]
    q = np.zeros((numR, 4))
    K = np.zeros((4, 4))
    
    for i in range(numR):
        K[0, 0] = (1.0/3.0) * (R_3d[0, 0, i] - R_3d[1, 1, i] - R_3d[2, 2, i])
        K[0, 1] = (1.0/3.0) * (R_3d[1, 0, i] + R_3d[0, 1, i])
        K[0, 2] = (1.0/3.0) * (R_3d[2, 0, i] + R_3d[0, 2, i])
        K[0, 3] = (1.0/3.0) * (R_3d[1, 2, i] - R_3d[2, 1, i])
        
        K[1, 0] = (1.0/3.0) * (R_3d[1, 0, i] + R_3d[0, 1, i])
        K[1, 1] = (1.0/3.0) * (R_3d[1, 1, i] - R_3d[0, 0, i] - R_3d[2, 2, i])
        K[1, 2] = (1.0/3.0) * (R_3d[2, 1, i] + R_3d[1, 2, i])
        K[1, 3] = (1.0/3.0) * (R_3d[2, 0, i] - R_3d[0, 2, i])
        
        K[2, 0] = (1.0/3.0) * (R_3d[2, 0, i] + R_3d[0, 2, i])
        K[2, 1] = (1.0/3.0) * (R_3d[2, 1, i] + R_3d[1, 2, i])
        K[2, 2] = (1.0/3.0) * (R_3d[2, 2, i] - R_3d[0, 0, i] - R_3d[1, 1, i])
        K[2, 3] = (1.0/3.0) * (R_3d[0, 1, i] - R_3d[1, 0, i])
        
        K[3, 0] = (1.0/3.0) * (R_3d[1, 2, i] - R_3d[2, 1, i])
        K[3, 1] = (1.0/3.0) * (R_3d[2, 0, i] - R_3d[0, 2, i])
        K[3, 2] = (1.0/3.0) * (R_3d[0, 1, i] - R_3d[1, 0, i])
        K[3, 3] = (1.0/3.0) * (R_3d[0, 0, i] + R_3d[1, 1, i] + R_3d[2, 2, i])
        
        # eigh returns eigenvalues in ascending order, so the last column is the principal eigenvector
        D, V = np.linalg.eigh(K)
        q_raw = V[:, 3]
        q[i, :] = [q_raw[3], q_raw[0], q_raw[1], q_raw[2]]
        
    if R.ndim == 2:
        return q[0, :]
    else:
        return q
