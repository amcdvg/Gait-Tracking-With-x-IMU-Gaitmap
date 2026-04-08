import numpy as np
from quaternProd import quaternProd
from quaternConj import quaternConj

def quaternRotate(v, q):
    if len(np.shape(v)) == 1:
        # 1D array case
        v_ext = np.array([0.0, v[0], v[1], v[2]])
        v0XYZ = quaternProd(quaternProd(q, v_ext), quaternConj(q))
        v_rot = v0XYZ[1:4]
    else:
        # 2D array case (Nx3)
        row = v.shape[0]
        v_ext = np.column_stack((np.zeros(row), v))
        v0XYZ = quaternProd(quaternProd(q, v_ext), quaternConj(q))
        v_rot = v0XYZ[:, 1:4]
        
    return v_rot
