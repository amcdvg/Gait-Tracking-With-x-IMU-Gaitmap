import numpy as np

from axisAngle2rotMat import axisAngle2rotMat
from axisAngle2quatern import axisAngle2quatern
from quatern2rotMat import quatern2rotMat
from rotMat2quatern import rotMat2quatern
from rotMat2euler import rotMat2euler
from quatern2euler import quatern2euler
from euler2rotMat import euler2rotMat

def main():
    # Axis-angle to rotation matrix
    axis = np.array([1.0, 2.0, 3.0])
    axis = axis / np.linalg.norm(axis)
    axis = axis[np.newaxis, :] # Make it 2D for consistency
    angle = np.pi / 2.0
    
    R = axisAngle2rotMat(axis, angle)
    print("Axis-angle to rotation matrix:")
    print(f"{R[0, 0]: 1.5f}\t{R[0, 1]: 1.5f}\t{R[0, 2]: 1.5f}")
    print(f"{R[1, 0]: 1.5f}\t{R[1, 1]: 1.5f}\t{R[1, 2]: 1.5f}")
    print(f"{R[2, 0]: 1.5f}\t{R[2, 1]: 1.5f}\t{R[2, 2]: 1.5f}")
    print()
    
    # Axis-angle to quaternion
    q = axisAngle2quatern(axis, angle)
    print("Axis-angle to quaternion:")
    print(f"{q[0, 0]: 1.5f}\t{q[0, 1]: 1.5f}\t{q[0, 2]: 1.5f}\t{q[0, 3]: 1.5f}")
    print()
    
    # Quaternion to rotation matrix
    R = quatern2rotMat(q)
    print("Quaternion to rotation matrix:")
    print(f"{R[0, 0, 0]: 1.5f}\t{R[0, 1, 0]: 1.5f}\t{R[0, 2, 0]: 1.5f}")
    print(f"{R[1, 0, 0]: 1.5f}\t{R[1, 1, 0]: 1.5f}\t{R[1, 2, 0]: 1.5f}")
    print(f"{R[2, 0, 0]: 1.5f}\t{R[2, 1, 0]: 1.5f}\t{R[2, 2, 0]: 1.5f}")
    print()
    
    # Rotation matrix to quaternion
    q = rotMat2quatern(R)
    print("Rotation matrix to quaternion:")
    print(f"{q[0, 0]: 1.5f}\t{q[0, 1]: 1.5f}\t{q[0, 2]: 1.5f}\t{q[0, 3]: 1.5f}")
    print()
    
    # Rotation matrix to ZYX Euler angles
    euler = rotMat2euler(R)
    print("Rotation matrix to ZYX Euler angles:")
    print(f"{euler[0, 0]: 1.5f}\t{euler[0, 1]: 1.5f}\t{euler[0, 2]: 1.5f}")
    print()
    
    # Quaternion to ZYX Euler angles
    euler = quatern2euler(q)
    print("Quaternion to ZYX Euler angles:")
    print(f"{euler[0, 0]: 1.5f}\t{euler[0, 1]: 1.5f}\t{euler[0, 2]: 1.5f}")
    print()
    
    # ZYX Euler angles to rotation matrix
    R = euler2rotMat(np.array([euler[0, 0]]), np.array([euler[0, 1]]), np.array([euler[0, 2]]))
    print("ZYX Euler angles to rotation matrix:")
    print(f"{R[0, 0, 0]: 1.5f}\t{R[0, 1, 0]: 1.5f}\t{R[0, 2, 0]: 1.5f}")
    print(f"{R[1, 0, 0]: 1.5f}\t{R[1, 1, 0]: 1.5f}\t{R[1, 2, 0]: 1.5f}")
    print(f"{R[2, 0, 0]: 1.5f}\t{R[2, 1, 0]: 1.5f}\t{R[2, 2, 0]: 1.5f}")
    print()
    
if __name__ == "__main__":
    main()
