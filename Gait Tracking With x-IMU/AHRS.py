import numpy as np

class AHRS:
    def __init__(self, **kwargs):
        self.SamplePeriod = 1.0/256.0
        self.Quaternion = np.array([1.0, 0.0, 0.0, 0.0])
        self.Kp = 2.0
        self.Ki = 0.0
        self.KpInit = 200.0
        self.InitPeriod = 5.0
        
        self.q = np.array([1.0, 0.0, 0.0, 0.0])
        self.IntError = np.array([0.0, 0.0, 0.0])
        self.KpRamped = self.KpInit
        
        # In MATLAB args were passed as pairs e.g. 'SamplePeriod', 1/256
        for k, v in kwargs.items():
            if k == 'SamplePeriod': self.SamplePeriod = v
            elif k == 'Quaternion': 
                self.Quaternion = np.array(v)
                self.q = self._quaternConj(self.Quaternion)
            elif k == 'Kp': self.Kp = v
            elif k == 'Ki': self.Ki = v
            elif k == 'KpInit': self.KpInit = v
            elif k == 'InitPeriod': self.InitPeriod = v
            else: raise Exception('Invalid argument')
            
        self.KpRamped = self.KpInit
        
    def Update(self, Gyroscope, Accelerometer, Magnetometer):
        raise Exception('This method is unimplemented')
        
    def UpdateIMU(self, Gyroscope, Accelerometer):
        Accelerometer = np.array(Accelerometer, dtype=float)
        Gyroscope = np.array(Gyroscope, dtype=float)
        
        norm_acc = np.linalg.norm(Accelerometer)
        if norm_acc == 0:
            print('Warning: Accelerometer magnitude is zero. Algorithm update aborted.')
            return
        else:
            Accelerometer = Accelerometer / norm_acc
            
        v = np.array([
            2*(self.q[1]*self.q[3] - self.q[0]*self.q[2]),
            2*(self.q[0]*self.q[1] + self.q[2]*self.q[3]),
            self.q[0]**2 - self.q[1]**2 - self.q[2]**2 + self.q[3]**2
        ])
        
        error = np.cross(v, Accelerometer)
        self.IntError = self.IntError + error
        
        Ref = Gyroscope - (self.Kp * error + self.Ki * self.IntError)
        Ref_ext = np.array([0.0, Ref[0], Ref[1], Ref[2]])
        
        pDot = 0.5 * self._quaternProd(self.q, Ref_ext)
        self.q = self.q + pDot * self.SamplePeriod
        self.q = self.q / np.linalg.norm(self.q)
        
        self.Quaternion = self._quaternConj(self.q)
        
    def Reset(self):
        self.KpRamped = self.KpInit
        self.IntError = np.array([0.0, 0.0, 0.0])
        self.q = np.array([1.0, 0.0, 0.0, 0.0])
        
    def _quaternProd(self, a, b):
        ab = np.zeros(4)
        ab[0] = a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3]
        ab[1] = a[0]*b[1] + a[1]*b[0] + a[2]*b[3] - a[3]*b[2]
        ab[2] = a[0]*b[2] - a[1]*b[3] + a[2]*b[0] + a[3]*b[1]
        ab[3] = a[0]*b[3] + a[1]*b[2] - a[2]*b[1] + a[3]*b[0]
        return ab
        
    def _quaternConj(self, q):
        return np.array([q[0], -q[1], -q[2], -q[3]])
