import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

sys.path.append(os.path.join(os.path.dirname(__file__), 'Quaternions'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ximu_matlab_library'))

from ximu_matlab_library.xIMUdataClass import xIMUdataClass
from AHRS import AHRS
from Quaternions.quaternRotate import quaternRotate
from Quaternions.quaternConj import quaternConj
from Quaternions.quatern2rotMat import quatern2rotMat
from SixDofAnimation import SixDofAnimation

# -------------------------------------------------------------------------
# Select dataset (comment in/out)

filePath = 'datasets/caminata_5metros_20260406_185421_tem2.txt'
startTime = 0
stopTime = 10000

# filePath = 'Datasets/straightLine'
# startTime = 6
# stopTime = 26

# filePath = 'Datasets/stairsAndCorridor'
# startTime = 5
# stopTime = 53

# filePath = 'Datasets/spiralStairs'
# startTime = 4
# stopTime = 47

# -------------------------------------------------------------------------
# Import data

if filePath.endswith('.txt'):
    import pandas as pd
    
    # Defaulting to 50 Hz just in case the format varies
    samplePeriod = 1.0 / 100.0 
    try:
        with open(filePath, 'r') as f:
            first_line = f.readline().strip()
            if 'Frecuencia' in first_line:
                freq_str = first_line.split(';')[1].replace(',', '.')
                print(freq_str)
                samplePeriod = 1.0 / float(freq_str)
    except Exception as e:
        print(f"Warning: Could not read Frecuencia from {filePath}. Using default 50 Hz. ({e})")
        
    df = pd.read_csv(filePath, sep=';', decimal=',', skiprows=1)
    
    # Filter for canal == 'Mov' for both ids
    df_id1 = df[(df['canal'] == 'Mov') & (df['id'] == 1)].reset_index(drop=True)
    #df_id2 = df[(df['canal'] == 'Mov') & (df['id'] == 2)].reset_index(drop=True)
    
    # Ensure they have the same length
    n_samples = len(df_id1)#min(len(df_id1), len(df_id2))
    time_vec = np.arange(n_samples) * samplePeriod
    
    # Gyroscope data is identical on both IDs
    gyrX = df_id1['rawGirX'].iloc[:n_samples].to_numpy()
    gyrY = df_id1['rawGirY'].iloc[:n_samples].to_numpy()
    gyrZ = df_id1['rawGirZ'].iloc[:n_samples].to_numpy()
    
    # sum id=1 (Linear Acceleration) and id=2 (Gravity) to reconstruct the full Raw Accelerometer 
    # vector expected by the algorithm, and divide by 9.81 to scale from m/s² back to 'g' space.
    accX = (df_id1['rawAccX'].iloc[:n_samples].to_numpy())/9.81# + df_id2['rawAccX'].iloc[:n_samples].to_numpy()) / 9.81
    accY = (df_id1['rawAccY'].iloc[:n_samples].to_numpy())/9.81# + df_id2['rawAccY'].iloc[:n_samples].to_numpy()) / 9.81
    accZ = (df_id1['rawAccZ'].iloc[:n_samples].to_numpy())/9.91# + df_id2['rawAccZ'].iloc[:n_samples].to_numpy()) / 9.81
# if filePath.endswith('.txt'):
#     import pandas as pd
    
#     # Defaulting to 50 Hz just in case the format varies
#     samplePeriod = 1.0 / 50.0 
#     try:
#         with open(filePath, 'r') as f:
#             first_line = f.readline().strip()
#             if 'Frecuencia' in first_line:
#                 freq_str = first_line.split(';')[1].replace(',', '.')
#                 samplePeriod = 1.0 / float(freq_str)
#     except Exception as e:
#         print(f"Warning: Could not read Frecuencia from {filePath}. Using default 50 Hz. ({e})")
        
#     df = pd.read_csv(filePath, sep=';', decimal=',', skiprows=1)
    
#     # Filter for canal == 'Mov' and id == 1 (as requested instead of 2)
#     df_filtered = df[(df['canal'] == 'Mov') & (df['id'] == 1)]
    
#     # Extract data, generate time vector
#     time_vec = np.arange(len(df_filtered)) * samplePeriod
    
#     gyrX = df_filtered['rawGirX'].to_numpy()
#     gyrY = df_filtered['rawGirY'].to_numpy()
#     gyrZ = df_filtered['rawGirZ'].to_numpy()
#     # The txt dataset provides raw values in m/s^2, but the script expects values in 'g' format for stationary detection and further calculation.
#     accX = df_filtered['rawAccX'].to_numpy() / 9.81
#     accY = df_filtered['rawAccY'].to_numpy() / 9.81
#     accZ = df_filtered['rawAccZ'].to_numpy() / 9.81
else:
    samplePeriod = 1.0/256.0
    xIMUdata = xIMUdataClass(filePath, 'InertialMagneticSampleRate', 1.0/samplePeriod)
    time_vec = xIMUdata.CalInertialAndMagneticData.Time
    gyrX = xIMUdata.CalInertialAndMagneticData.Gyroscope['X']
    gyrY = xIMUdata.CalInertialAndMagneticData.Gyroscope['Y']
    gyrZ = xIMUdata.CalInertialAndMagneticData.Gyroscope['Z']
    accX = xIMUdata.CalInertialAndMagneticData.Accelerometer['X']
    accY = xIMUdata.CalInertialAndMagneticData.Accelerometer['Y']
    accZ = xIMUdata.CalInertialAndMagneticData.Accelerometer['Z']

# -------------------------------------------------------------------------
# Manually frame data

indexSel = np.where((time_vec >= startTime) & (time_vec <= stopTime))[0]
time_vec = time_vec[indexSel]
gyrX = gyrX[indexSel]
gyrY = gyrY[indexSel]
gyrZ = gyrZ[indexSel]
accX = accX[indexSel]
accY = accY[indexSel]
accZ = accZ[indexSel]

# -------------------------------------------------------------------------
# Detect stationary periods

# Compute accelerometer magnitude
acc_mag = np.sqrt(accX*accX + accY*accY + accZ*accZ)

# HP filter accelerometer data
filtCutOff = 0.01
b, a = butter(1, (2.0*filtCutOff)/(1.0/samplePeriod), btype='high')
acc_magFilt = filtfilt(b, a, acc_mag)

# Compute absolute value
acc_magFilt = np.abs(acc_magFilt)

# LP filter accelerometer data
filtCutOff = 5
b, a = butter(1, (2.0*filtCutOff)/(1.0/samplePeriod), btype='low')
acc_magFilt = filtfilt(b, a, acc_magFilt)

# Threshold detection
print(acc_magFilt)
stationary = acc_magFilt < 0.5

# -------------------------------------------------------------------------
# Plot data raw sensor data and stationary periods

fig = plt.figure(figsize=(10, 6), num='Sensor Data')

ax1 = fig.add_subplot(211)
ax1.plot(time_vec, gyrX, 'r', label='X')
ax1.plot(time_vec, gyrY, 'g', label='Y')
ax1.plot(time_vec, gyrZ, 'b', label='Z')
ax1.set_title('Gyroscope')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Angular velocity ($^\\circ$/s)')
ax1.legend()

ax2 = fig.add_subplot(212, sharex=ax1)
ax2.plot(time_vec, accX, 'r', label='X')
ax2.plot(time_vec, accY, 'g', label='Y')
ax2.plot(time_vec, accZ, 'b', label='Z')
ax2.plot(time_vec, acc_magFilt, ':k', label='Filtered')
ax2.plot(time_vec, stationary.astype(float), 'k', linewidth=2, label='Stationary')
ax2.set_title('Accelerometer')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Acceleration (g)')
ax2.legend()

plt.tight_layout()

# -------------------------------------------------------------------------
# Compute orientation

quat = np.zeros((len(time_vec), 4))
AHRSalgorithm = AHRS(SamplePeriod=samplePeriod, Kp=1, KpInit=1)

# Initial convergence
# Focus on the first stationary period to calibrate vertical gravity to prevent Z-drift (staircase effect)
stat_indices = np.where(stationary)[0]
if len(stat_indices) > 0:
    indexSel_init = stat_indices[:min(10, len(stat_indices))]
else:
    indexSel_init = np.array([0])
    
for i in range(2000):
    AHRSalgorithm.UpdateIMU([0, 0, 0], [np.mean(accX[indexSel_init]), np.mean(accY[indexSel_init]), np.mean(accZ[indexSel_init])])
    
# For all data
for t in range(len(time_vec)):
    if stationary[t]:
        AHRSalgorithm.Kp = 0.5
    else:
        AHRSalgorithm.Kp = 0.0
    AHRSalgorithm.UpdateIMU(np.deg2rad([gyrX[t], gyrY[t], gyrZ[t]]), [accX[t], accY[t], accZ[t]])
    quat[t, :] = AHRSalgorithm.Quaternion

# -------------------------------------------------------------------------
# Compute translational accelerations

# Rotate body accelerations to Earth frame
acc = quaternRotate(np.column_stack((accX, accY, accZ)), quaternConj(quat))

# Convert acceleration measurements to m/s/s
acc = acc * 9.81

# Plot translational accelerations
fig2 = plt.figure(figsize=(10, 3), num='Accelerations')
plt.plot(time_vec, acc[:, 0], 'r', label='X')
plt.plot(time_vec, acc[:, 1], 'g', label='Y')
plt.plot(time_vec, acc[:, 2], 'b', label='Z')
plt.title('Acceleration')
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s/s)')
plt.legend()
plt.tight_layout()

# -------------------------------------------------------------------------
# Compute translational velocities

acc[:, 2] = acc[:, 2] - 9.81

# Integrate acceleration to yield velocity
vel = np.zeros_like(acc)
for t in range(1, len(vel)):
    vel[t, :] = vel[t-1, :] + acc[t, :] * samplePeriod
    if stationary[t] == 1:
        vel[t, :] = [0, 0, 0] # force zero velocity when foot stationary
        
# Compute integral drift during non-stationary periods
velDrift = np.zeros_like(vel)
diff_stat = np.diff(stationary.astype(int))
stationaryStart = np.where(np.concatenate(([0], diff_stat)) == -1)[0]
stationaryEnd = np.where(np.concatenate(([0], diff_stat)) == 1)[0]

#====================================================================
# Fix edge case where there is no matching start or end
if not stationary[0]:
    stationaryStart = np.insert(stationaryStart, 0, 0)
if not stationary[-1]:
    stationaryEnd = np.append(stationaryEnd, len(stationary))
#====================================================================
for i in range(len(stationaryEnd)):
    driftRate = vel[stationaryEnd[i]-1, :] / (stationaryEnd[i] - stationaryStart[i])
    enum = np.arange(1, (stationaryEnd[i] - stationaryStart[i]) + 1)
    drift = np.column_stack((enum * driftRate[0], enum * driftRate[1], enum * driftRate[2]))
    velDrift[stationaryStart[i]:stationaryEnd[i], :] = drift
    
# Remove integral drift
vel = vel - velDrift

# Plot translational velocity
fig3 = plt.figure(figsize=(10, 3), num='Velocity')
plt.plot(time_vec, vel[:, 0], 'r', label='X')
plt.plot(time_vec, vel[:, 1], 'g', label='Y')
plt.plot(time_vec, vel[:, 2], 'b', label='Z')
plt.title('Velocity')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.legend()
plt.tight_layout()

# -------------------------------------------------------------------------
# Compute translational position
# -------------------------------------------------------------------------
# # Integrate velocity to yield position
# pos = np.zeros_like(vel)
# for t in range(1, len(pos)):
#     pos[t, :] = pos[t-1, :] + vel[t, :] * samplePeriod
    
# # --- TRASLACIÓN DE LA SEÑAL EN Z ---
# # Encuentra el punto más bajo de la trayectoria en el eje Z
# #z_min = np.min(pos[:, 2])

# # Traslada toda la señal hacia arriba para que el mínimo sea exactamente 0
# #pos[:, 2] = pos[:, 2] - z_min

# -------------------------------------------------------------------------
# 9. Compute translational position
# -------------------------------------------------------------------------
# Integrar velocidad para obtener posición inicial
pos = np.zeros_like(vel)
for t in range(1, len(pos)):
    pos[t, :] = pos[t-1, :] + vel[t, :] * samplePeriod

# --- CORRECCIÓN CONTINUA DE DERIVA EN Z ---
# Aseguramos que el pie regrese al nivel del suelo en cada paso
for i in range(len(stationaryEnd)):
    start_idx = stationaryStart[i]
    end_idx = stationaryEnd[i]
    
    # Cuánta altura errónea se acumuló durante este paso específico
    delta_z = pos[end_idx-1, 2] - pos[start_idx, 2]
    
    # Distribuimos este error suavemente a lo largo del paso (como una rampa)
    # para trasladar la curva sin deformar la dinámica del movimiento
    n_samples = end_idx - start_idx
    drift_ramp = np.linspace(0, delta_z, n_samples)
    
    # Restamos la rampa solo al paso actual
    pos[start_idx:end_idx, 2] -= drift_ramp
    
    # Trasladamos todo el resto de la señal futura para mantener la continuidad (sin saltos bruscos)
    if end_idx < len(pos):
        pos[end_idx:, 2] -= delta_z

# Finalmente, trasladamos toda la gráfica para que el punto más bajo sea el 0 exacto.
# Esto asegura de forma definitiva que ningún valor de la matriz Z sea negativo.
pos[:, 2] = pos[:, 2] - np.min(pos[:, 2])

# Graficar posición traslacional
fig4 = plt.figure(figsize=(10, 6), num='Position')
plt.plot(time_vec, pos[:, 0], 'r', label='X')
plt.plot(time_vec, pos[:, 1], 'g', label='Y')
plt.plot(time_vec, pos[:, 2], 'b', label='Z')
plt.title('Position')
plt.xlabel('Time (s)')
plt.ylabel('Position (m)')
plt.legend()
plt.tight_layout()

# -------------------------------------------------------------------------
# Plot 3D foot trajectory

posPlot = pos
quatPlot = quat

extraTime = 20
onesVector = np.ones((int(extraTime * (1.0/samplePeriod)), 1))
posPlot_append = np.column_stack((posPlot[-1, 0]*onesVector, posPlot[-1, 1]*onesVector, posPlot[-1, 2]*onesVector))
quatPlot_append = np.column_stack((quatPlot[-1, 0]*onesVector, quatPlot[-1, 1]*onesVector, quatPlot[-1, 2]*onesVector, quatPlot[-1, 3]*onesVector))

posPlot = np.vstack((posPlot, posPlot_append))
quatPlot = np.vstack((quatPlot, quatPlot_append))
fs = float(freq_str)
if fs == 50.0:
    SamplePlotFreq = 2
else: SamplePlotFreq = 2
Spin = 120
spin_array = np.arange(100, 100+Spin + Spin/(len(posPlot)-1), Spin/(len(posPlot)-1))
if len(spin_array) > len(posPlot):
    spin_array = spin_array[:len(posPlot)]

view_angle = np.column_stack((spin_array, 10*np.ones(len(spin_array))))

SixDofAnimation(posPlot, quatern2rotMat(quatPlot),fs,
                SamplePlotFreq=SamplePlotFreq, Trail='All',
                View=view_angle, AxisLength=0.1, ShowArrowHead=False,
                Xlabel='X (m)', Ylabel='Y (m)', Zlabel='Z (m)', ShowLegend=False)