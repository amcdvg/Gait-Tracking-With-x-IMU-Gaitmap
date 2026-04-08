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
from SixDofAnimationTwoSensors import SixDofAnimation

# -------------------------------------------------------------------------
# Select dataset (comment in/out)

filePath = 'datasets/caminata 10 m Aza_20260204_120349_tem2.txt'
startTime = 0
stopTime = 10000

# -------------------------------------------------------------------------
# Import data

if filePath.endswith('.txt'):
    import pandas as pd
    
    samplePeriod = 1.0 / 50.0 
    try:
        with open(filePath, 'r') as f:
            first_line = f.readline().strip()
            if 'Frecuencia' in first_line:
                freq_str = first_line.split(';')[1].replace(',', '.')
                print(f"Frecuencia detectada: {freq_str} Hz")
                samplePeriod = 1.0 / float(freq_str)
    except Exception as e:
        print(f"Warning: Could not read Frecuencia from {filePath}. Using default 50 Hz. ({e})")
        freq_str = "50.0"
        
    df = pd.read_csv(filePath, sep=';', decimal=',', skiprows=1)
    canales_repetidos_filtrado = df[df['canal'].duplicated(keep=False)]['canal'].unique().tolist()
    canales = sorted(canales_repetidos_filtrado) 
    print(canales)
    # Filter for canal == 'Mov' (Sensor 1 - Cuerpo/Pelvis)
    df1_id1 = df[(df['canal'] == canales[0]) & (df['id'] == 1)].reset_index(drop=True)
    df1_id2 = df[(df['canal'] == canales[0]) & (df['id'] == 2)].reset_index(drop=True)
    
    # Filter for canal == 'Wrist' (Sensor 2 - Pie Izquierdo)
    df2_id1 = df[(df['canal'] == canales[-1]) & (df['id'] == 1)].reset_index(drop=True)
    df2_id2 = df[(df['canal'] == canales[-1]) & (df['id'] == 2)].reset_index(drop=True)
    
    # Comprobar si existen datos con id=2 (para los archivos de 50 Hz)
    has_id2 = len(df1_id2) > 0 and len(df2_id2) > 0

    if has_id2:
        n_samples = min(len(df1_id1), len(df1_id2), len(df2_id1), len(df2_id2))
    else:
        n_samples = min(len(df1_id1), len(df2_id1))
        
    time_vec = np.arange(n_samples) * samplePeriod
    
    # --- Sensor 1 (Mov) ---
    gyrX1 = df1_id1['rawGirX'].iloc[:n_samples].to_numpy()
    gyrY1 = df1_id1['rawGirY'].iloc[:n_samples].to_numpy()
    gyrZ1 = df1_id1['rawGirZ'].iloc[:n_samples].to_numpy()
    
    if has_id2:
        accX1 = (df1_id1['rawAccX'].iloc[:n_samples].to_numpy() + df1_id2['rawAccX'].iloc[:n_samples].to_numpy()) / 9.81
        accY1 = (df1_id1['rawAccY'].iloc[:n_samples].to_numpy() + df1_id2['rawAccY'].iloc[:n_samples].to_numpy()) / 9.81
        accZ1 = (df1_id1['rawAccZ'].iloc[:n_samples].to_numpy() + df1_id2['rawAccZ'].iloc[:n_samples].to_numpy()) / 9.81
    else:
        accX1 = df1_id1['rawAccX'].iloc[:n_samples].to_numpy() / 9.81
        accY1 = df1_id1['rawAccY'].iloc[:n_samples].to_numpy() / 9.81
        accZ1 = df1_id1['rawAccZ'].iloc[:n_samples].to_numpy() / 9.81

    # --- Sensor 2 (Mov2 - Pie) ---
    gyrX2 = df2_id1['rawGirX'].iloc[:n_samples].to_numpy()
    gyrY2 = df2_id1['rawGirY'].iloc[:n_samples].to_numpy()
    gyrZ2 = df2_id1['rawGirZ'].iloc[:n_samples].to_numpy()
    
    if has_id2:
        accX2 = (df2_id1['rawAccX'].iloc[:n_samples].to_numpy() + df2_id2['rawAccX'].iloc[:n_samples].to_numpy()) / 9.81
        accY2 = (df2_id1['rawAccY'].iloc[:n_samples].to_numpy() + df2_id2['rawAccY'].iloc[:n_samples].to_numpy()) / 9.81
        accZ2 = (df2_id1['rawAccZ'].iloc[:n_samples].to_numpy() + df2_id2['rawAccZ'].iloc[:n_samples].to_numpy()) / 9.81
    else:
        accX2 = df2_id1['rawAccX'].iloc[:n_samples].to_numpy() / 9.81
        accY2 = df2_id1['rawAccY'].iloc[:n_samples].to_numpy() / 9.81
        accZ2 = df2_id1['rawAccZ'].iloc[:n_samples].to_numpy() / 9.81

else:
    samplePeriod = 1.0/256.0
    freq_str = "256.0"
    pass 

# -------------------------------------------------------------------------
# Manually frame data

indexSel = np.where((time_vec >= startTime) & (time_vec <= stopTime))[0]
time_vec = time_vec[indexSel]

gyrX1, gyrY1, gyrZ1 = gyrX1[indexSel], gyrY1[indexSel], gyrZ1[indexSel]
accX1, accY1, accZ1 = accX1[indexSel], accY1[indexSel], accZ1[indexSel]

gyrX2, gyrY2, gyrZ2 = gyrX2[indexSel], gyrY2[indexSel], gyrZ2[indexSel]
accX2, accY2, accZ2 = accX2[indexSel], accY2[indexSel], accZ2[indexSel]

# -------------------------------------------------------------------------
# Detect stationary periods

acc_mag1 = np.sqrt(accX1**2 + accY1**2 + accZ1**2)
acc_mag2 = np.sqrt(accX2**2 + accY2**2 + accZ2**2)

filtCutOff = 0.001
b, a = butter(1, (2.0*filtCutOff)/(1.0/samplePeriod), btype='high')
acc_magFilt1 = np.abs(filtfilt(b, a, acc_mag1))
acc_magFilt2 = np.abs(filtfilt(b, a, acc_mag2))

filtCutOff = 15
b, a = butter(1, (2.0*filtCutOff)/(1.0/samplePeriod), btype='low')
acc_magFilt1 = filtfilt(b, a, acc_magFilt1)
acc_magFilt2 = filtfilt(b, a, acc_magFilt2)

stationary1 = (acc_magFilt1 < 0.2) & (acc_mag1 > 0.6) & (acc_mag1 < 1.4)
stationary2 = (acc_magFilt2 < 0.2) & (acc_mag2 > 0.6) & (acc_mag2 < 1.4)

# -------------------------------------------------------------------------
# Plot raw sensor data and stationary periods
# -------------------------------------------------------------------------

# Sensor 1 (Mov)
fig_sensor1 = plt.figure(figsize=(10, 6), num=f'Sensor 1 Data ({canales[0]})')
ax1 = fig_sensor1.add_subplot(211)
ax1.plot(time_vec, gyrX1, 'r', label='X')
ax1.plot(time_vec, gyrY1, 'g', label='Y')
ax1.plot(time_vec, gyrZ1, 'b', label='Z')
ax1.set_title(f'Sensor 1 ({canales[0]}) - Gyroscope')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Angular velocity ($^\circ$/s)')
ax1.legend()

ax2 = fig_sensor1.add_subplot(212, sharex=ax1)
ax2.plot(time_vec, accX1, 'r', label='X')
ax2.plot(time_vec, accY1, 'g', label='Y')
ax2.plot(time_vec, accZ1, 'b', label='Z')
ax2.plot(time_vec, acc_magFilt1, ':k', label='Filtered')
ax2.plot(time_vec, stationary1.astype(float), 'k', linewidth=2, label='Stationary')
ax2.set_title(f'Sensor 1 ({canales[0]}) - Accelerometer')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Acceleration (g)')
ax2.legend()
plt.tight_layout()

# Sensor 2 (Mov2)
fig_sensor2 = plt.figure(figsize=(10, 6), num=f'Sensor 2 Data ({canales[1]})')
ax3 = fig_sensor2.add_subplot(211)
ax3.plot(time_vec, gyrX2, 'r', label='X')
ax3.plot(time_vec, gyrY2, 'g', label='Y')
ax3.plot(time_vec, gyrZ2, 'b', label='Z')
ax3.set_title(f'Sensor 2 ({canales[1]}) - Left Foot) - Gyroscope')
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('Angular velocity ($^\circ$/s)')
ax3.legend()

ax4 = fig_sensor2.add_subplot(212, sharex=ax3)
ax4.plot(time_vec, accX2, 'r', label='X')
ax4.plot(time_vec, accY2, 'g', label='Y')
ax4.plot(time_vec, accZ2, 'b', label='Z')
ax4.plot(time_vec, acc_magFilt2, ':k', label='Filtered')
ax4.plot(time_vec, stationary2.astype(float), 'k', linewidth=2, label='Stationary')
ax4.set_title(f'Sensor 2 ({canales[1]} - Left Foot) - Accelerometer')
ax4.set_xlabel('Time (s)')
ax4.set_ylabel('Acceleration (g)')
ax4.legend()
plt.tight_layout()


# =========================================================================
# HIBRIDACIÓN CONDICIONAL: CÁLCULO DE TRAYECTORIA (MANUAL vs GAITMAP)
# =========================================================================

acc_peak = np.percentile(acc_mag1, 99)
energia_senal = np.var(acc_mag1)
print(acc_peak)
print(energia_senal)
if acc_peak > 4.65 or energia_senal > 2.0:
    actividad_actual = 'salto'
elif acc_peak > 2.7 or energia_senal > 0.6:
    actividad_actual = 'correr'
else:
    actividad_actual = 'marcha'

print(f"\n--- CLASIFICADOR AUTOMÁTICO DE SEÑAL ---")
print(f"Pico de Aceleración (99%): {acc_peak:.2f} g")
print(f"Energía (Varianza): {energia_senal:.2f}")
print(f"-> Actividad Detectada: {actividad_actual.upper()}\n")

if actividad_actual in ['correr']:
    import pandas as pd
    from scipy.spatial.transform import Rotation as R_scipy
    from gaitmap.event_detection import RamppEventDetection
    from gaitmap.trajectory_reconstruction import RtsKalman
    from gaitmap.preprocessing.sensor_alignment import PcaAlignment

    N_BIAS_SAMPLES = 20

    def load_imu_data(filepath, sensor_name):
        with open(filepath, 'r') as f:
            first_line = f.readline()
            try:
                fs_val = float(first_line.split(';')[-1].strip())
            except:
                fs_val = 100.0

        df = pd.read_csv(filepath, sep=';', decimal=',', skiprows=1)

        if fs_val < 100.0:
            df_id1 = df[(df['canal'] == sensor_name) & (df['id'] == 1)].copy()
            df_id2 = df[(df['canal'] == sensor_name) & (df['id'] == 2)].copy()

            if df_id2.empty:
                df_sensor = df_id1.copy()
                for eje in ['rawGirX', 'rawGirY', 'rawGirZ']:
                    bias = df_sensor[eje].astype(float).iloc[:N_BIAS_SAMPLES].mean()
                    df_sensor[eje] = df_sensor[eje].astype(float) - bias
                return pd.DataFrame({
                    'acc_pa': df_sensor['rawAccX'].astype(float),
                    'acc_ml': df_sensor['rawAccY'].astype(float),
                    'acc_si': df_sensor['rawAccZ'].astype(float),
                    'gyr_pa': df_sensor['rawGirX'].astype(float),
                    'gyr_ml': df_sensor['rawGirY'].astype(float),
                    'gyr_si': df_sensor['rawGirZ'].astype(float)
                }).reset_index(drop=True)

            for eje in ['rawGirX', 'rawGirY', 'rawGirZ']:
                bias = df_id1[eje].astype(float).iloc[:N_BIAS_SAMPLES].mean()
                df_id1[eje] = df_id1[eje].astype(float) - bias

            s1 = df_id1.set_index('sample')
            s2 = df_id2.set_index('sample')
            common = sorted(s1.index.intersection(s2.index))

            if len(common) == 0:
                df_sensor = df_id1.copy()
                return pd.DataFrame({
                    'acc_pa': df_sensor['rawAccX'].astype(float).values,
                    'acc_ml': df_sensor['rawAccY'].astype(float).values,
                    'acc_si': df_sensor['rawAccZ'].astype(float).values,
                    'gyr_pa': df_sensor['rawGirX'].astype(float).values,
                    'gyr_ml': df_sensor['rawGirY'].astype(float).values,
                    'gyr_si': df_sensor['rawGirZ'].astype(float).values
                }).reset_index(drop=True)

            acc_pa = (s1.loc[common, 'rawAccX'].astype(float).values +
                      s2.loc[common, 'rawAccX'].astype(float).values)
            acc_ml = (s1.loc[common, 'rawAccY'].astype(float).values +
                      s2.loc[common, 'rawAccY'].astype(float).values)
            acc_si = (s1.loc[common, 'rawAccZ'].astype(float).values +
                      s2.loc[common, 'rawAccZ'].astype(float).values)
            gyr_pa = s1.loc[common, 'rawGirX'].astype(float).values
            gyr_ml = s1.loc[common, 'rawGirY'].astype(float).values
            gyr_si = s1.loc[common, 'rawGirZ'].astype(float).values

            data = pd.DataFrame({
                'acc_pa': acc_pa,
                'acc_ml': acc_ml,
                'acc_si': acc_si,
                'gyr_pa': gyr_pa,
                'gyr_ml': gyr_ml,
                'gyr_si': gyr_si
            }).reset_index(drop=True)
            return data

        else:
            df_sensor = df[df['canal'] == sensor_name].copy()
            if df_sensor.empty: return pd.DataFrame()
            for eje in ['rawGirX', 'rawGirY', 'rawGirZ']:
                bias = df_sensor[eje].astype(float).iloc[:N_BIAS_SAMPLES].mean()
                df_sensor[eje] = df_sensor[eje].astype(float) - bias
            data = pd.DataFrame({
                'acc_pa': df_sensor['rawAccX'].astype(float),
                'acc_ml': df_sensor['rawAccY'].astype(float),
                'acc_si': df_sensor['rawAccZ'].astype(float),
                'gyr_pa': df_sensor['rawGirX'].astype(float),
                'gyr_ml': df_sensor['rawGirY'].astype(float),
                'gyr_si': df_sensor['rawGirZ'].astype(float)
            }).reset_index(drop=True)
            return data

    def process_trajectory(imu_data, sampling_rate=100.0, tipo_actividad='salto', umbral=100.0):
        stride_list = pd.DataFrame({'start': [0], 'end': [len(imu_data)-1]})
        stride_list.index.name = 's_id'
        
        if tipo_actividad == 'correr':
            # 1. Eventos: RamppEventDetection (HMM) NO es para correr. Usamos detección de picos en giro.
            from scipy.signal import find_peaks, butter, filtfilt
            gyr_mag = np.linalg.norm(imu_data[['gyr_pa', 'gyr_ml', 'gyr_si']].values, axis=1)
            nyq = 0.5 * sampling_rate
            b_filt, a_filt = butter(2, 5.0 / nyq, btype='low')
            gyr_mag_filt = filtfilt(b_filt, a_filt, gyr_mag)
            
            # Distance garantiza zancadas rápidas (ej. 0.25s), prominence bajo asume vibración alta
            valles, _ = find_peaks(-gyr_mag_filt, distance=int(sampling_rate * 0.25), prominence=0.1)
            zero_velocity_events = {0: pd.DataFrame({'min_vel': valles})}
        else:
            ed = RamppEventDetection()
            ed = ed.detect(data=imu_data, stride_list=stride_list,
                           sampling_rate_hz=sampling_rate)
            zero_velocity_events = ed.min_vel_event_list_

        imu_xyz = imu_data.rename(columns={
            'acc_pa':'acc_x', 'acc_ml':'acc_y', 'acc_si':'acc_z',
            'gyr_pa':'gyr_x', 'gyr_ml':'gyr_y', 'gyr_si':'gyr_z'
        })

        trajectory = RtsKalman()

        # 2. Configurar el ZUPT Interno para validar apoyos ruidosos
        if hasattr(trajectory, 'zupt_detector') and trajectory.zupt_detector is not None:
            if tipo_actividad == 'correr':
                # Regla matemática de Gaitmap: Ventana > 3 muestras (0.04s a 100Hz)
                if hasattr(trajectory.zupt_detector, 'window_length_s'):
                    trajectory.zupt_detector.window_length_s = max(0.04, 3.01 / sampling_rate)
                    
                
                # CRÍTICO PARA ELIMINAR LA BARRIGA: Subir drásticamente el umbral.
                # Obliga al Kalman a aceptar la fase de apoyo aunque el pie esté vibrando por el impacto.
                if hasattr(trajectory.zupt_detector, 'inactive_signal_threshold'):
                    # Subimos el umbral para tolerar el ruido dinámico
                    trajectory.zupt_detector.inactive_signal_threshold = umbral
            else:
                if hasattr(trajectory.zupt_detector, 'window_length_s'):
                    trajectory.zupt_detector.window_length_s = max(0.05, 3.01 / sampling_rate)

        trajectory = trajectory.estimate(
            data=imu_xyz,
            stride_event_list=zero_velocity_events,
            sampling_rate_hz=sampling_rate
        )

        if isinstance(trajectory.position_, dict):
            position_df    = pd.concat(trajectory.position_.values()).reset_index(drop=True) 
            orientation_df = pd.concat(trajectory.orientation_.values()).reset_index(drop=True)
        else:
            position_df    = trajectory.position_.reset_index(drop=True) 
            orientation_df = trajectory.orientation_.reset_index(drop=True)

        pos = position_df.values[:, :3] 

        # =====================================================================
        # CORRECCIÓN DE DERIVA Z PARA CORRER (INICIO Y FIN EXACTOS EN EL SUELO)
        # Obliga matemáticamente a que la trayectoria Z valga exactamente 0.0 
        # en cada fase de apoyo (valle).
        # =====================================================================
        if tipo_actividad == 'correr' and 'valles' in locals() and len(valles) > 1:
            for i in range(len(valles) - 1):
                start_idx = valles[i]
                end_idx = valles[i+1]
                n_samples_step = end_idx - start_idx
                if n_samples_step > 0:
                    correccion_z = np.linspace(pos[start_idx, 2], pos[end_idx, 2], n_samples_step, endpoint=False)
                    pos[start_idx:end_idx, 2] -= correccion_z
            
            # Ajustar los bordes (antes del primer valle y después del último)
            if len(valles) > 0:
                pos[:valles[0], 2] -= pos[valles[0], 2]
                pos[valles[-1]:, 2] -= pos[valles[-1], 2]
        # =====================================================================

        pos[:, 2] = np.maximum(pos[:, 2], 0.0) 

        if 'w' in orientation_df.columns:
            quats = orientation_df[['x','y','z','w']].values
        elif 'q_w' in orientation_df.columns:
            quats = orientation_df[['q_x','q_y','q_z','q_w']].values
        else:
            quats = orientation_df.values

        norms = np.linalg.norm(quats, axis=1, keepdims=True)
        quats = quats / np.where(norms > 0, norms, 1.0)
        return pos, quats

    fs_val = 1.0 / samplePeriod

    # Sensor 1 (Mov)
    imu_df_1 = load_imu_data(filePath, canales[0])
    if not imu_df_1.empty:
        sensor_frame_1 = imu_df_1.rename(columns={'acc_pa':'acc_x', 'acc_ml':'acc_y', 'acc_si':'acc_z', 'gyr_pa':'gyr_x', 'gyr_ml':'gyr_y', 'gyr_si':'gyr_z'})
        pca_align_1 = PcaAlignment(target_axis="y", pca_plane_axis=("gyr_x", "gyr_y")).align(sensor_frame_1)
        body_frame_1 = pca_align_1.aligned_data_.rename(columns={'acc_x':'acc_pa', 'acc_y':'acc_ml', 'acc_z':'acc_si', 'gyr_x':'gyr_pa', 'gyr_y':'gyr_ml', 'gyr_z':'gyr_si'})
        pos1_gm, quats1_gm = process_trajectory(body_frame_1, sampling_rate=fs_val, tipo_actividad=actividad_actual, umbral=20.0)
    else:
        pos1_gm, quats1_gm = np.zeros((len(time_vec), 3)), np.zeros((len(time_vec), 4))

    # Sensor 2 (Mov2 - Pie Izquierdo)
    imu_df_2 = load_imu_data(filePath, canales[1])
    if not imu_df_2.empty:
        sensor_frame_2 = imu_df_2.rename(columns={'acc_pa':'acc_x', 'acc_ml':'acc_y', 'acc_si':'acc_z', 'gyr_pa':'gyr_x', 'gyr_ml':'gyr_y', 'gyr_si':'gyr_z'})
        pca_align_2 = PcaAlignment(target_axis="y", pca_plane_axis=("gyr_x", "gyr_y")).align(sensor_frame_2)
        body_frame_2 = pca_align_2.aligned_data_.rename(columns={'acc_x':'acc_pa', 'acc_y':'acc_ml', 'acc_z':'acc_si', 'gyr_x':'gyr_pa', 'gyr_y':'gyr_ml', 'gyr_z':'gyr_si'})
        pos2_gm, quats2_gm = process_trajectory(body_frame_2, sampling_rate=fs_val, tipo_actividad=actividad_actual, umbral=20.0)
    else:
        pos2_gm, quats2_gm = np.zeros((len(time_vec), 3)), np.zeros((len(time_vec), 4))

    # Ajustar dimensiones a time_vec original
    min_len = min(len(pos1_gm), len(pos2_gm), len(time_vec))
    pos1 = pos1_gm[:min_len]
    pos2 = pos2_gm[:min_len]
    quat1 = quats1_gm[:min_len]
    quat2 = quats2_gm[:min_len]
    time_vec = time_vec[:min_len]

    vel1 = np.vstack(([0,0,0], np.diff(pos1, axis=0) * fs_val))
    vel2 = np.vstack(([0,0,0], np.diff(pos2, axis=0) * fs_val))
    acc1 = np.vstack(([0,0,0], np.diff(vel1, axis=0) * fs_val))
    acc2 = np.vstack(([0,0,0], np.diff(vel2, axis=0) * fs_val))

    pos1[:, 2] = pos1[:, 2] - pos1[0, 2]
    pos1[:, 2] = np.maximum(pos1[:, 2], 0.0)
    
    pos2[:, 2] = pos2[:, 2] - pos2[0, 2] 
    pos2[:, 2] = np.maximum(pos2[:, 2], 0.0)

    # =========================================================================
    # --- IGUALAR ALTURAS DE ZANCADA ENTRE SENSORES ---
    # Escala la trayectoria Z de Sensor 1 para que su altura máxima (98%) 
    # coincida con la de Sensor 2, haciendo que sean relativamente iguales.
    # =========================================================================
    p_z1 = np.percentile(pos1[:, 2], 98)
    p_z2 = np.percentile(pos2[:, 2], 98)
    if p_z1 > 0.001 and p_z2 > 0.001:
        pos1[:, 2] = pos1[:, 2] * (p_z2 / p_z1)

elif actividad_actual in ['salto']:
    import pandas as pd
    from scipy.spatial.transform import Rotation as R_scipy
    from gaitmap.event_detection import RamppEventDetection
    from gaitmap.trajectory_reconstruction import RtsKalman
    from gaitmap.preprocessing.sensor_alignment import PcaAlignment

    N_BIAS_SAMPLES = 20

    def load_imu_data(filepath, sensor_name):
        with open(filepath, 'r') as f:
            first_line = f.readline()
            try:
                fs_val = float(first_line.split(';')[-1].strip())
            except:
                fs_val = 100.0

        df = pd.read_csv(filepath, sep=';', decimal=',', skiprows=1)

        if fs_val < 100.0:
            df_id1 = df[(df['canal'] == sensor_name) & (df['id'] == 1)].copy()
            df_id2 = df[(df['canal'] == sensor_name) & (df['id'] == 2)].copy()

            if df_id2.empty:
                df_sensor = df_id1.copy()
                for eje in ['rawGirX', 'rawGirY', 'rawGirZ']:
                    bias = df_sensor[eje].astype(float).iloc[:N_BIAS_SAMPLES].mean()
                    df_sensor[eje] = df_sensor[eje].astype(float) - bias
                return pd.DataFrame({
                    'acc_pa': df_sensor['rawAccX'].astype(float),
                    'acc_ml': df_sensor['rawAccY'].astype(float),
                    'acc_si': df_sensor['rawAccZ'].astype(float),
                    'gyr_pa': df_sensor['rawGirX'].astype(float),
                    'gyr_ml': df_sensor['rawGirY'].astype(float),
                    'gyr_si': df_sensor['rawGirZ'].astype(float)
                }).reset_index(drop=True)

            for eje in ['rawGirX', 'rawGirY', 'rawGirZ']:
                bias = df_id1[eje].astype(float).iloc[:N_BIAS_SAMPLES].mean()
                df_id1[eje] = df_id1[eje].astype(float) - bias

            s1 = df_id1.set_index('sample')
            s2 = df_id2.set_index('sample')
            common = sorted(s1.index.intersection(s2.index))

            if len(common) == 0:
                df_sensor = df_id1.copy()
                return pd.DataFrame({
                    'acc_pa': df_sensor['rawAccX'].astype(float).values,
                    'acc_ml': df_sensor['rawAccY'].astype(float).values,
                    'acc_si': df_sensor['rawAccZ'].astype(float).values,
                    'gyr_pa': df_sensor['rawGirX'].astype(float).values,
                    'gyr_ml': df_sensor['rawGirY'].astype(float).values,
                    'gyr_si': df_sensor['rawGirZ'].astype(float).values
                }).reset_index(drop=True)

            acc_pa = (s1.loc[common, 'rawAccX'].astype(float).values +
                      s2.loc[common, 'rawAccX'].astype(float).values)
            acc_ml = (s1.loc[common, 'rawAccY'].astype(float).values +
                      s2.loc[common, 'rawAccY'].astype(float).values)
            acc_si = (s1.loc[common, 'rawAccZ'].astype(float).values +
                      s2.loc[common, 'rawAccZ'].astype(float).values)
            gyr_pa = s1.loc[common, 'rawGirX'].astype(float).values
            gyr_ml = s1.loc[common, 'rawGirY'].astype(float).values
            gyr_si = s1.loc[common, 'rawGirZ'].astype(float).values

            data = pd.DataFrame({
                'acc_pa': acc_pa,
                'acc_ml': acc_ml,
                'acc_si': acc_si,
                'gyr_pa': gyr_pa,
                'gyr_ml': gyr_ml,
                'gyr_si': gyr_si
            }).reset_index(drop=True)
            return data

        else:
            df_sensor = df[df['canal'] == sensor_name].copy()
            if df_sensor.empty: return pd.DataFrame()
            for eje in ['rawGirX', 'rawGirY', 'rawGirZ']:
                bias = df_sensor[eje].astype(float).iloc[:N_BIAS_SAMPLES].mean()
                df_sensor[eje] = df_sensor[eje].astype(float) - bias
            data = pd.DataFrame({
                'acc_pa': df_sensor['rawAccX'].astype(float),
                'acc_ml': df_sensor['rawAccY'].astype(float),
                'acc_si': df_sensor['rawAccZ'].astype(float),
                'gyr_pa': df_sensor['rawGirX'].astype(float),
                'gyr_ml': df_sensor['rawGirY'].astype(float),
                'gyr_si': df_sensor['rawGirZ'].astype(float)
            }).reset_index(drop=True)
            return data

    def process_trajectory(imu_data, sampling_rate=100.0, tipo_actividad='salto'):
        stride_list = pd.DataFrame({'start': [0], 'end': [len(imu_data)-1]})
        stride_list.index.name = 's_id'

        ed = RamppEventDetection()
        ed = ed.detect(data=imu_data, stride_list=stride_list,
                       sampling_rate_hz=sampling_rate)
        zero_velocity_events = ed.min_vel_event_list_

        imu_xyz = imu_data.rename(columns={
            'acc_pa':'acc_x', 'acc_ml':'acc_y', 'acc_si':'acc_z',
            'gyr_pa':'gyr_x', 'gyr_ml':'gyr_y', 'gyr_si':'gyr_z'
        })

        trajectory = RtsKalman()

        if hasattr(trajectory, 'zupt_detector') and trajectory.zupt_detector is not None:
            if hasattr(trajectory.zupt_detector, 'window_length_s'):
                if tipo_actividad in ['marcha', 'correr']:
                    if tipo_actividad == 'correr':
                        min_permitido = 2.0 / sampling_rate
                    else:
                        min_permitido = 3.01 / sampling_rate
                    trajectory.zupt_detector.window_length_s = max(0.05, min_permitido)
                elif sampling_rate < 100.0:
                    trajectory.zupt_detector.window_length_s = max(0.05, 4.0 / sampling_rate)

        trajectory = trajectory.estimate(
            data=imu_xyz,
            stride_event_list=zero_velocity_events,
            sampling_rate_hz=sampling_rate
        )

        if isinstance(trajectory.position_, dict):
            position_df    = pd.concat(trajectory.position_.values()).reset_index(drop=True)
            orientation_df = pd.concat(trajectory.orientation_.values()).reset_index(drop=True)
        else:
            position_df    = trajectory.position_.reset_index(drop=True)
            orientation_df = trajectory.orientation_.reset_index(drop=True)

        pos = position_df.values[:, :3]
        pos[:, 2] = np.maximum(pos[:, 2], 0.0)

        if 'w' in orientation_df.columns:
            quats = orientation_df[['x','y','z','w']].values
        elif 'q_w' in orientation_df.columns:
            quats = orientation_df[['q_x','q_y','q_z','q_w']].values
        else:
            quats = orientation_df.values

        norms = np.linalg.norm(quats, axis=1, keepdims=True)
        quats = quats / np.where(norms > 0, norms, 1.0)
        return pos, quats

    fs_val = 1.0 / samplePeriod

    # Sensor 1 (Mov)
    imu_df_1 = load_imu_data(filePath, canales[0])
    if not imu_df_1.empty:
        sensor_frame_1 = imu_df_1.rename(columns={'acc_pa':'acc_x', 'acc_ml':'acc_y', 'acc_si':'acc_z', 'gyr_pa':'gyr_x', 'gyr_ml':'gyr_y', 'gyr_si':'gyr_z'})
        pca_align_1 = PcaAlignment(target_axis="y", pca_plane_axis=("gyr_x", "gyr_y")).align(sensor_frame_1)
        body_frame_1 = pca_align_1.aligned_data_.rename(columns={'acc_x':'acc_pa', 'acc_y':'acc_ml', 'acc_z':'acc_si', 'gyr_x':'gyr_pa', 'gyr_y':'gyr_ml', 'gyr_z':'gyr_si'})
        pos1_gm, quats1_gm = process_trajectory(body_frame_1, sampling_rate=fs_val, tipo_actividad=actividad_actual)
    else:
        pos1_gm, quats1_gm = np.zeros((len(time_vec), 3)), np.zeros((len(time_vec), 4))

    # Sensor 2 (Mov2)
    imu_df_2 = load_imu_data(filePath, canales[1])
    if not imu_df_2.empty:
        sensor_frame_2 = imu_df_2.rename(columns={'acc_pa':'acc_x', 'acc_ml':'acc_y', 'acc_si':'acc_z', 'gyr_pa':'gyr_x', 'gyr_ml':'gyr_y', 'gyr_si':'gyr_z'})
        pca_align_2 = PcaAlignment(target_axis="y", pca_plane_axis=("gyr_x", "gyr_y")).align(sensor_frame_2)
        body_frame_2 = pca_align_2.aligned_data_.rename(columns={'acc_x':'acc_pa', 'acc_y':'acc_ml', 'acc_z':'acc_si', 'gyr_x':'gyr_pa', 'gyr_y':'gyr_ml', 'gyr_z':'gyr_si'})
        pos2_gm, quats2_gm = process_trajectory(body_frame_2, sampling_rate=fs_val, tipo_actividad=actividad_actual)
    else:
        pos2_gm, quats2_gm = np.zeros((len(time_vec), 3)), np.zeros((len(time_vec), 4))

    # Ajustar dimensiones a time_vec original para que las gráficas finales no fallen
    min_len = min(len(pos1_gm), len(pos2_gm), len(time_vec))
    pos1 = pos1_gm[:min_len]
    pos2 = pos2_gm[:min_len]
    quat1 = quats1_gm[:min_len]
    quat2 = quats2_gm[:min_len]
    time_vec = time_vec[:min_len]

    # Derivadas matemáticas para alimentar las gráficas de velocidad/aceleración originales
    vel1 = np.vstack(([0,0,0], np.diff(pos1, axis=0) * fs_val))
    vel2 = np.vstack(([0,0,0], np.diff(pos2, axis=0) * fs_val))
    acc1 = np.vstack(([0,0,0], np.diff(vel1, axis=0) * fs_val))
    acc2 = np.vstack(([0,0,0], np.diff(vel2, axis=0) * fs_val))

    # Traslados en Z (Lógica estricta de Gaitmap respetada)
    pos1[:, 2] = pos1[:, 2] - pos1[0, 2]
    pos1[:, 2] = np.maximum(pos1[:, 2], 0.0)
    
    pos2[:, 2] = pos2[:, 2] - pos2[0, 2]
    pos2[:, 2] = np.maximum(pos2[:, 2], 0.0)
else:
    
    if freq_str == '100':
            import pandas as pd
            from scipy.spatial.transform import Rotation as R_scipy
            from gaitmap.event_detection import RamppEventDetection
            from gaitmap.trajectory_reconstruction import RtsKalman
            from gaitmap.preprocessing.sensor_alignment import PcaAlignment

            N_BIAS_SAMPLES = 20

            def load_imu_data(filepath, sensor_name):
                with open(filepath, 'r') as f:
                    first_line = f.readline()
                    try:
                        fs_val = float(first_line.split(';')[-1].strip())
                    except:
                        fs_val = 100.0

                df = pd.read_csv(filepath, sep=';', decimal=',', skiprows=1)

                if fs_val < 100.0:
                    df_id1 = df[(df['canal'] == sensor_name) & (df['id'] == 1)].copy()
                    df_id2 = df[(df['canal'] == sensor_name) & (df['id'] == 2)].copy()

                    if df_id2.empty:
                        df_sensor = df_id1.copy()
                        for eje in ['rawGirX', 'rawGirY', 'rawGirZ']:
                            bias = df_sensor[eje].astype(float).iloc[:N_BIAS_SAMPLES].mean()
                            df_sensor[eje] = df_sensor[eje].astype(float) - bias
                        return pd.DataFrame({
                            'acc_pa': df_sensor['rawAccX'].astype(float),
                            'acc_ml': df_sensor['rawAccY'].astype(float),
                            'acc_si': df_sensor['rawAccZ'].astype(float),
                            'gyr_pa': df_sensor['rawGirX'].astype(float),
                            'gyr_ml': df_sensor['rawGirY'].astype(float),
                            'gyr_si': df_sensor['rawGirZ'].astype(float)
                        }).reset_index(drop=True)

                    for eje in ['rawGirX', 'rawGirY', 'rawGirZ']:
                        bias = df_id1[eje].astype(float).iloc[:N_BIAS_SAMPLES].mean()
                        df_id1[eje] = df_id1[eje].astype(float) - bias

                    s1 = df_id1.set_index('sample')
                    s2 = df_id2.set_index('sample')
                    common = sorted(s1.index.intersection(s2.index))

                    if len(common) == 0:
                        df_sensor = df_id1.copy()
                        return pd.DataFrame({
                            'acc_pa': df_sensor['rawAccX'].astype(float).values,
                            'acc_ml': df_sensor['rawAccY'].astype(float).values,
                            'acc_si': df_sensor['rawAccZ'].astype(float).values,
                            'gyr_pa': df_sensor['rawGirX'].astype(float).values,
                            'gyr_ml': df_sensor['rawGirY'].astype(float).values,
                            'gyr_si': df_sensor['rawGirZ'].astype(float).values
                        }).reset_index(drop=True)

                    acc_pa = (s1.loc[common, 'rawAccX'].astype(float).values +
                            s2.loc[common, 'rawAccX'].astype(float).values)
                    acc_ml = (s1.loc[common, 'rawAccY'].astype(float).values +
                            s2.loc[common, 'rawAccY'].astype(float).values)
                    acc_si = (s1.loc[common, 'rawAccZ'].astype(float).values +
                            s2.loc[common, 'rawAccZ'].astype(float).values)
                    gyr_pa = s1.loc[common, 'rawGirX'].astype(float).values
                    gyr_ml = s1.loc[common, 'rawGirY'].astype(float).values
                    gyr_si = s1.loc[common, 'rawGirZ'].astype(float).values

                    data = pd.DataFrame({
                        'acc_pa': acc_pa,
                        'acc_ml': acc_ml,
                        'acc_si': acc_si,
                        'gyr_pa': gyr_pa,
                        'gyr_ml': gyr_ml,
                        'gyr_si': gyr_si
                    }).reset_index(drop=True)
                    return data

                else:
                    df_sensor = df[df['canal'] == sensor_name].copy()
                    if df_sensor.empty: return pd.DataFrame()
                    for eje in ['rawGirX', 'rawGirY', 'rawGirZ']:
                        bias = df_sensor[eje].astype(float).iloc[:N_BIAS_SAMPLES].mean()
                        df_sensor[eje] = df_sensor[eje].astype(float) - bias
                    data = pd.DataFrame({
                        'acc_pa': df_sensor['rawAccX'].astype(float),
                        'acc_ml': df_sensor['rawAccY'].astype(float),
                        'acc_si': df_sensor['rawAccZ'].astype(float),
                        'gyr_pa': df_sensor['rawGirX'].astype(float),
                        'gyr_ml': df_sensor['rawGirY'].astype(float),
                        'gyr_si': df_sensor['rawGirZ'].astype(float)
                    }).reset_index(drop=True)
                    return data

            def process_trajectory(imu_data, sampling_rate=100.0, tipo_actividad='salto'):
                stride_list = pd.DataFrame({'start': [0], 'end': [len(imu_data)-1]})
                stride_list.index.name = 's_id'

                ed = RamppEventDetection()
                ed = ed.detect(data=imu_data, stride_list=stride_list,
                            sampling_rate_hz=sampling_rate)
                zero_velocity_events = ed.min_vel_event_list_

                imu_xyz = imu_data.rename(columns={
                    'acc_pa':'acc_x', 'acc_ml':'acc_y', 'acc_si':'acc_z',
                    'gyr_pa':'gyr_x', 'gyr_ml':'gyr_y', 'gyr_si':'gyr_z'
                })

                trajectory = RtsKalman()

                if hasattr(trajectory, 'zupt_detector') and trajectory.zupt_detector is not None:
                    if hasattr(trajectory.zupt_detector, 'window_length_s'):
                        if tipo_actividad in ['marcha', 'correr']:
                            if tipo_actividad == 'correr':
                                min_permitido = 2.0 / sampling_rate
                            else:
                                min_permitido = 3.01 / sampling_rate
                            trajectory.zupt_detector.window_length_s = max(0.05, min_permitido)
                        elif sampling_rate < 100.0:
                            trajectory.zupt_detector.window_length_s = max(0.05, 4.0 / sampling_rate)

                trajectory = trajectory.estimate(
                    data=imu_xyz,
                    stride_event_list=zero_velocity_events,
                    sampling_rate_hz=sampling_rate
                )

                if isinstance(trajectory.position_, dict):
                    position_df    = pd.concat(trajectory.position_.values()).reset_index(drop=True)
                    orientation_df = pd.concat(trajectory.orientation_.values()).reset_index(drop=True)
                else:
                    position_df    = trajectory.position_.reset_index(drop=True)
                    orientation_df = trajectory.orientation_.reset_index(drop=True)

                pos = position_df.values[:, :3]
                pos[:, 2] = np.maximum(pos[:, 2], 0.0)

                if 'w' in orientation_df.columns:
                    quats = orientation_df[['x','y','z','w']].values
                elif 'q_w' in orientation_df.columns:
                    quats = orientation_df[['q_x','q_y','q_z','q_w']].values
                else:
                    quats = orientation_df.values

                norms = np.linalg.norm(quats, axis=1, keepdims=True)
                quats = quats / np.where(norms > 0, norms, 1.0)
                return pos, quats

            fs_val = 1.0 / samplePeriod

            # Sensor 1 (Mov)
            imu_df_1 = load_imu_data(filePath, canales[0])
            if not imu_df_1.empty:
                sensor_frame_1 = imu_df_1.rename(columns={'acc_pa':'acc_x', 'acc_ml':'acc_y', 'acc_si':'acc_z', 'gyr_pa':'gyr_x', 'gyr_ml':'gyr_y', 'gyr_si':'gyr_z'})
                pca_align_1 = PcaAlignment(target_axis="y", pca_plane_axis=("gyr_x", "gyr_y")).align(sensor_frame_1)
                body_frame_1 = pca_align_1.aligned_data_.rename(columns={'acc_x':'acc_pa', 'acc_y':'acc_ml', 'acc_z':'acc_si', 'gyr_x':'gyr_pa', 'gyr_y':'gyr_ml', 'gyr_z':'gyr_si'})
                pos1_gm, quats1_gm = process_trajectory(body_frame_1, sampling_rate=fs_val, tipo_actividad=actividad_actual)
            else:
                pos1_gm, quats1_gm = np.zeros((len(time_vec), 3)), np.zeros((len(time_vec), 4))

            # Sensor 2 (Mov2 - Pie Izquierdo)
            imu_df_2 = load_imu_data(filePath, canales[1])
            if not imu_df_2.empty:
                sensor_frame_2 = imu_df_2.rename(columns={'acc_pa':'acc_x', 'acc_ml':'acc_y', 'acc_si':'acc_z', 'gyr_pa':'gyr_x', 'gyr_ml':'gyr_y', 'gyr_si':'gyr_z'})
                pca_align_2 = PcaAlignment(target_axis="y", pca_plane_axis=("gyr_x", "gyr_y")).align(sensor_frame_2)
                body_frame_2 = pca_align_2.aligned_data_.rename(columns={'acc_x':'acc_pa', 'acc_y':'acc_ml', 'acc_z':'acc_si', 'gyr_x':'gyr_pa', 'gyr_y':'gyr_ml', 'gyr_z':'gyr_si'})
                pos2_gm, quats2_gm = process_trajectory(body_frame_2, sampling_rate=fs_val, tipo_actividad=actividad_actual)
            else:
                pos2_gm, quats2_gm = np.zeros((len(time_vec), 3)), np.zeros((len(time_vec), 4))

            # Ajustar dimensiones a time_vec original
            min_len = min(len(pos1_gm), len(pos2_gm), len(time_vec))
            pos1 = pos1_gm[:min_len]
            pos2 = pos2_gm[:min_len]
            quat1 = quats1_gm[:min_len]
            quat2 = quats2_gm[:min_len]
            time_vec = time_vec[:min_len]

            vel1 = np.vstack(([0,0,0], np.diff(pos1, axis=0) * fs_val))
            vel2 = np.vstack(([0,0,0], np.diff(pos2, axis=0) * fs_val))
            acc1 = np.vstack(([0,0,0], np.diff(vel1, axis=0) * fs_val))
            acc2 = np.vstack(([0,0,0], np.diff(vel2, axis=0) * fs_val))

            pos1[:, 2] = pos1[:, 2] - pos1[0, 2]
            pos1[:, 2] = np.maximum(pos1[:, 2], 0.0)
            
            pos2[:, 2] = pos2[:, 2] - pos2[0, 2]
            pos2[:, 2] = np.maximum(pos2[:, 2], 0.0)
    else:
        # -------------------------------------------------------------------------
        # Compute orientation
        quat1 = np.zeros((len(time_vec), 4))
        quat2 = np.zeros((len(time_vec), 4))
        AHRS1 = AHRS(SamplePeriod=samplePeriod, Kp=1, KpInit=1)
        AHRS2 = AHRS(SamplePeriod=samplePeriod, Kp=1, KpInit=1)

        stat_indices1 = np.where(stationary1)[0]
        indexSel_init1 = stat_indices1[:min(10, len(stat_indices1))] if len(stat_indices1) > 0 else np.array([0])

        stat_indices2 = np.where(stationary2)[0]
        indexSel_init2 = stat_indices2[:min(10, len(stat_indices2))] if len(stat_indices2) > 0 else np.array([0])

        for i in range(2000):
            AHRS1.UpdateIMU([0, 0, 0], [np.mean(accX1[indexSel_init1]), np.mean(accY1[indexSel_init1]), np.mean(accZ1[indexSel_init1])])
            AHRS2.UpdateIMU([0, 0, 0], [np.mean(accX2[indexSel_init2]), np.mean(accY2[indexSel_init2]), np.mean(accZ2[indexSel_init2])])
            
        for t in range(len(time_vec)):
            AHRS1.Kp = 0.5 if stationary1[t] else 0.0
            AHRS1.UpdateIMU(np.deg2rad([gyrX1[t], gyrY1[t], gyrZ1[t]]), [accX1[t], accY1[t], accZ1[t]])
            quat1[t, :] = AHRS1.Quaternion
            
            AHRS2.Kp = 0.5 if stationary2[t] else 0.0
            AHRS2.UpdateIMU(np.deg2rad([gyrX2[t], gyrY2[t], gyrZ2[t]]), [accX2[t], accY2[t], accZ2[t]])
            quat2[t, :] = AHRS2.Quaternion

        # -------------------------------------------------------------------------
        # Compute translational accelerations
        acc1 = quaternRotate(np.column_stack((accX1, accY1, accZ1)), quaternConj(quat1)) * 9.81
        acc2 = quaternRotate(np.column_stack((accX2, accY2, accZ2)), quaternConj(quat2)) * 9.81

        # -------------------------------------------------------------------------
        # Compute translational velocities
        acc1[:, 2] = acc1[:, 2] - 9.81
        acc2[:, 2] = acc2[:, 2] - 9.81

        vel1 = np.zeros_like(acc1)
        vel2 = np.zeros_like(acc2)

        for t in range(1, len(vel1)):
            vel1[t, :] = vel1[t-1, :] + acc1[t, :] * samplePeriod
            vel2[t, :] = vel2[t-1, :] + acc2[t, :] * samplePeriod
            if stationary1[t] == 1: vel1[t, :] = [0, 0, 0]
            if stationary2[t] == 1: vel2[t, :] = [0, 0, 0]

        # --- Remover Deriva Mov ---
        velDrift1 = np.zeros_like(vel1)
        diff_stat1 = np.diff(stationary1.astype(int))
        stationaryStart1 = np.where(np.concatenate(([0], diff_stat1)) == -1)[0]
        stationaryEnd1 = np.where(np.concatenate(([0], diff_stat1)) == 1)[0]
        if not stationary1[0]: stationaryStart1 = np.insert(stationaryStart1, 0, 0)
        if not stationary1[-1]: stationaryEnd1 = np.append(stationaryEnd1, len(stationary1))

        for i in range(len(stationaryEnd1)):
            driftRate1 = vel1[stationaryEnd1[i]-1, :] / (stationaryEnd1[i] - stationaryStart1[i])
            enum1 = np.arange(1, (stationaryEnd1[i] - stationaryStart1[i]) + 1)
            drift1 = np.column_stack((enum1 * driftRate1[0], enum1 * driftRate1[1], enum1 * driftRate1[2]))
            velDrift1[stationaryStart1[i]:stationaryEnd1[i], :] = drift1
        vel1 = vel1 - velDrift1

        # --- Remover Deriva Mov2 ---
        velDrift2 = np.zeros_like(vel2)
        diff_stat2 = np.diff(stationary2.astype(int))
        stationaryStart2 = np.where(np.concatenate(([0], diff_stat2)) == -1)[0]
        stationaryEnd2 = np.where(np.concatenate(([0], diff_stat2)) == 1)[0]
        if not stationary2[0]: stationaryStart2 = np.insert(stationaryStart2, 0, 0)
        if not stationary2[-1]: stationaryEnd2 = np.append(stationaryEnd2, len(stationary2))

        for i in range(len(stationaryEnd2)):
            driftRate2 = vel2[stationaryEnd2[i]-1, :] / (stationaryEnd2[i] - stationaryStart2[i])
            enum2 = np.arange(1, (stationaryEnd2[i] - stationaryStart2[i]) + 1)
            drift2 = np.column_stack((enum2 * driftRate2[0], enum2 * driftRate2[1], enum2 * driftRate2[2]))
            velDrift2[stationaryStart2[i]:stationaryEnd2[i], :] = drift2
        vel2 = vel2 - velDrift2

        # -------------------------------------------------------------------------
        # Compute translational position
        pos1 = np.zeros_like(vel1)
        pos2 = np.zeros_like(vel2)

        for t in range(1, len(pos1)):
            pos1[t, :] = pos1[t-1, :] + vel1[t, :] * samplePeriod
            pos2[t, :] = pos2[t-1, :] + vel2[t, :] * samplePeriod

        # --- CORRECCIÓN CONTINUA DE DERIVA EN Z ---
        for i in range(len(stationaryEnd1)):
            start_idx, end_idx = stationaryStart1[i], stationaryEnd1[i]
            delta_z = pos1[end_idx-1, 2] - pos1[start_idx, 2]
            n_samples_step = end_idx - start_idx
            if n_samples_step > 0:
                pos1[start_idx:end_idx, 2] -= np.linspace(0, delta_z, n_samples_step)
            if end_idx < len(pos1): pos1[end_idx:, 2] -= delta_z

        for i in range(len(stationaryEnd2)):
            start_idx, end_idx = stationaryStart2[i], stationaryEnd2[i]
            delta_z = pos2[end_idx-1, 2] - pos2[start_idx, 2]
            n_samples_step = end_idx - start_idx
            if n_samples_step > 0:
                pos2[start_idx:end_idx, 2] -= np.linspace(0, delta_z, n_samples_step)
            if end_idx < len(pos2): pos2[end_idx:, 2] -= delta_z

        # Trasladar para iniciar en 0
        pos1[:, 2] = pos1[:, 2] - np.min(pos1[:, 2])
        pos2[:, 2] = pos2[:, 2] - np.min(pos2[:, 2]) - 0.065
        pos2[:, 2] = np.maximum(pos2[:, 2], 0.0)



if actividad_actual in ['salto']:
    
    # =========================================================================
    # --- REGLA ESTRICTA AÑADIDA: ASEGURAR PROGRESIÓN HACIA +X y +Y ---
    # Evita trayectorias negativas invirtiendo los ejes si el desplazamiento neto es negativo.
    # Funciona de manera universal sin importar si vino del método híbrido o manual.
    # =========================================================================
    if pos1[-1, 0] - pos1[0, 0] < 0:
        pos1[:, 0] = -pos1[:, 0]
    if pos1[-1, 1] - pos1[0, 1] < 0:
        pos1[:, 1] = -pos1[:, 1]

    if pos2[-1, 0] - pos2[0, 0] < 0:
        pos2[:, 0] = -pos2[:, 0]
    if pos2[-1, 1] - pos2[0, 1] < 0:
        pos2[:, 1] = -pos2[:, 1]

    # =========================================================================
    # --- REGLA ESTRICTA AÑADIDA: ASEGURAR QUE Z NUNCA SEA NEGATIVO ---
    # Aplana cualquier valor residual negativo a 0 (el nivel del suelo), 
    # idéntico a la función np.maximum de tu script original de Gaitmap.
    # =========================================================================
    pos1[:, 2] = np.maximum(pos1[:, 2], 0.0)
    pos2[:, 2] = np.maximum(pos2[:, 2], 0.0)


    # =========================================================================
    # (BLOQUES DE GRÁFICAS ORIGINALES - Funcionan para ambos métodos)
    # =========================================================================

    # -------------------------------------------------------------------------
    # Plot translational accelerations
    # -------------------------------------------------------------------------
    fig_acc, (ax_acc1, ax_acc2) = plt.subplots(2, 1, figsize=(10, 6), num='Accelerations', sharex=True)
    ax_acc1.plot(time_vec, acc1[:, 0], 'r', label='X')
    ax_acc1.plot(time_vec, acc1[:, 1], 'g', label='Y')
    ax_acc1.plot(time_vec, acc1[:, 2], 'b', label='Z')
    ax_acc1.set_title(f'Sensor 1 ({canales[0]}) - Acceleration')
    ax_acc1.set_ylabel('Acceleration (m/s/s)')
    ax_acc1.legend()

    ax_acc2.plot(time_vec, acc2[:, 0], 'r', label='X')
    ax_acc2.plot(time_vec, acc2[:, 1], 'g', label='Y')
    ax_acc2.plot(time_vec, acc2[:, 2], 'b', label='Z')
    ax_acc2.set_title(f'Sensor 2 ({canales[1]}) - Acceleration')
    ax_acc2.set_xlabel('Time (s)')
    ax_acc2.set_ylabel('Acceleration (m/s/s)')
    ax_acc2.legend()
    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Plot translational velocity
    # -------------------------------------------------------------------------
    fig_vel, (ax_vel1, ax_vel2) = plt.subplots(2, 1, figsize=(10, 6), num='Velocity', sharex=True)
    ax_vel1.plot(time_vec, vel1[:, 0], 'r', label='X')
    ax_vel1.plot(time_vec, vel1[:, 1], 'g', label='Y')
    ax_vel1.plot(time_vec, vel1[:, 2], 'b', label='Z')
    ax_vel1.set_title(f'Sensor 1 ({canales[0]}) - Velocity')
    ax_vel1.set_ylabel('Velocity (m/s)')
    ax_vel1.legend()

    ax_vel2.plot(time_vec, vel2[:, 0], 'r', label='X')
    ax_vel2.plot(time_vec, vel2[:, 1], 'g', label='Y')
    ax_vel2.plot(time_vec, vel2[:, 2], 'b', label='Z')
    ax_vel2.set_title(f'Sensor 2 ({canales[1]}) - Velocity')
    ax_vel2.set_xlabel('Time (s)')
    ax_vel2.set_ylabel('Velocity (m/s)')
    ax_vel2.legend()
    plt.tight_layout()

    # -------------------------------------------------------------------------
    # --- ALINEACIÓN DE RUMBO (TENDENCIA PRINCIPAL PCA) ---
    # -------------------------------------------------------------------------

    # Umbral ajustado a 0.1 para que el salto corto de 40 cm se alinee.
    dist_total = np.linalg.norm(pos1[-1, 0:2] - pos1[0, 0:2])

    if dist_total > 0.1:  
        def calcular_yaw_pca(posiciones):
            pos_xy = posiciones[:, 0:2]
            datos_centrados = pos_xy - np.mean(pos_xy, axis=0)
            covarianza = np.cov(datos_centrados, rowvar=False)
            valores, vectores = np.linalg.eigh(covarianza)
            vec_prin = vectores[:, np.argmax(valores)]
            
            vec_avance = pos_xy[-1] - pos_xy[0]
            if np.dot(vec_prin, vec_avance) < 0:
                vec_prin = -vec_prin
                
            return np.arctan2(vec_prin[1], vec_prin[0])
            
        yaw_mov1 = calcular_yaw_pca(pos1)
        yaw_mov2 = calcular_yaw_pca(pos2)
        
        delta_yaw = yaw_mov1 - yaw_mov2
        cos_a = np.cos(delta_yaw)
        sin_a = np.sin(delta_yaw)

        x_rot = pos2[:, 0] * cos_a - pos2[:, 1] * sin_a
        y_rot = pos2[:, 0] * sin_a + pos2[:, 1] * cos_a

        pos2[:, 0] = x_rot
        pos2[:, 1] = y_rot

        R_align = np.array([
            [cos_a, -sin_a, 0],
            [sin_a,  cos_a, 0],
            [0,      0,     1]
        ])
    else:
        R_align = np.eye(3)
        yaw_mov1 = 0

    ancho_pelvico = 0.05 
    if dist_total > 0.1:  
        vector_izq_x = -np.sin(yaw_mov1) * ancho_pelvico
        vector_izq_y = np.cos(yaw_mov1) * ancho_pelvico
    else:
        vector_izq_x = 0
        vector_izq_y = ancho_pelvico

    pos2[:, 0] += vector_izq_x
    pos2[:, 1] += vector_izq_y

    # -------------------------------------------------------------------------
    # Graficar posición traslacional y comparación
    # -------------------------------------------------------------------------
    fig_pos, (ax_pos1, ax_pos2) = plt.subplots(2, 1, figsize=(10, 6), num='Position', sharex=True)
    ax_pos1.plot(time_vec, pos1[:, 0], 'r', label='X')
    ax_pos1.plot(time_vec, pos1[:, 1], 'g', label='Y')
    ax_pos1.plot(time_vec, pos1[:, 2], 'b', label='Z')
    ax_pos1.set_title(f'Sensor 1 ({canales[0]}) - Position')
    ax_pos1.set_ylabel('Position (m)')
    ax_pos1.legend()

    ax_pos2.plot(time_vec, pos2[:, 0], 'r', label='X')
    ax_pos2.plot(time_vec, pos2[:, 1], 'g', label='Y')
    ax_pos2.plot(time_vec, pos2[:, 2], 'b', label='Z')
    ax_pos2.set_title(f'Sensor 2 ({canales[1]}) - Position')
    ax_pos2.set_xlabel('Time (s)')
    ax_pos2.set_ylabel('Position (m)')
    ax_pos2.legend()
    plt.tight_layout()

    # Comparación directa Mov vs Mov2
    fig_comp, (ax_comp1, ax_comp2) = plt.subplots(2, 1, figsize=(10, 6), num='Position Comparison')

    # Plano X-Y
    ax_comp1.plot(pos1[:, 0], pos1[:, 1], color='orange', label=f'{canales[0]} (Sensor 1)')
    ax_comp1.plot(pos2[:, 0], pos2[:, 1], color='green', label=f'{canales[1]} (Sensor 2)')
    ax_comp1.set_title('Trajectory Comparison (X-Y Plane)')
    ax_comp1.set_xlabel('X Position (m)')
    ax_comp1.set_ylabel('Y Position (m)')
    ax_comp1.legend()
    ax_comp1.grid(True)

    # Comparación de Altura (Z vs Time)
    ax_comp2.plot(time_vec, pos1[:, 2], color='orange', label=f'{canales[0]} Height')
    ax_comp2.plot(time_vec, pos2[:, 2], color='green', label=f'{canales[1]} Height')
    ax_comp2.set_title('Height Comparison (Z Axis)')
    ax_comp2.set_xlabel('Time (s)')
    ax_comp2.set_ylabel('Z Position (m)')
    ax_comp2.legend()
    ax_comp2.grid(True)
    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Comparación Vista Y vs Z
    # -------------------------------------------------------------------------
    fig_yz, ax_yz = plt.subplots(1, 1, figsize=(10, 4), num='Y vs Z View')
    ax_yz.plot(pos1[:, 1], pos1[:, 2], color='orange', label=f'{canales[0]} (Sensor 1)')
    ax_yz.plot(pos2[:, 1], pos2[:, 2], color='green', label=f'{canales[1]} (Sensor 2)')
    ax_yz.set_title('Trajectory Comparison (Y-Z Plane)')
    ax_yz.set_xlabel('Y Position (m)')
    ax_yz.set_ylabel('Z Position (m)')
    ax_yz.legend()
    ax_yz.grid(True)
    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Comparación Vista X vs Z
    # -------------------------------------------------------------------------
    fig_xz, ax_xz = plt.subplots(1, 1, figsize=(10, 4), num='X vs Z View')
    ax_xz.plot(pos1[:, 0], pos1[:, 2], color='orange', label=f'{canales[0]} (Sensor 1)')
    ax_xz.plot(pos2[:, 0], pos2[:, 2], color='green', label=f'{canales[1]} (Sensor 2)')
    ax_xz.set_title('Trajectory Comparison (X-Z Plane)')
    ax_xz.set_xlabel('X Position (m)')
    ax_xz.set_ylabel('Z Position (m)')
    ax_xz.legend()
    ax_xz.grid(True)
    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Plot 3D foot trajectory

    posPlot1, quatPlot1 = pos1, quat1
    posPlot2, quatPlot2 = pos2, quat2

    extraTime = 20
    onesVector = np.ones((int(extraTime * (1.0/samplePeriod)), 1))

    # Append extra time Mov
    posPlot_append1 = np.column_stack((posPlot1[-1, 0]*onesVector, posPlot1[-1, 1]*onesVector, posPlot1[-1, 2]*onesVector))
    quatPlot_append1 = np.column_stack((quatPlot1[-1, 0]*onesVector, quatPlot1[-1, 1]*onesVector, quatPlot1[-1, 2]*onesVector, quatPlot1[-1, 3]*onesVector))
    posPlot1 = np.vstack((posPlot1, posPlot_append1))
    quatPlot1 = np.vstack((quatPlot1, quatPlot_append1))

    # Append extra time Mov2
    posPlot_append2 = np.column_stack((posPlot2[-1, 0]*onesVector, posPlot2[-1, 1]*onesVector, posPlot2[-1, 2]*onesVector))
    quatPlot_append2 = np.column_stack((quatPlot2[-1, 0]*onesVector, quatPlot2[-1, 1]*onesVector, quatPlot2[-1, 2]*onesVector, quatPlot2[-1, 3]*onesVector))
    posPlot2 = np.vstack((posPlot2, posPlot_append2))
    quatPlot2 = np.vstack((quatPlot2, quatPlot_append2))

    fs = float(freq_str)
    SamplePlotFreq = 2 if fs == 50.0 else 2
    Spin = 120
    spin_array = np.arange(100, 100+Spin + Spin/(len(posPlot1)-1), Spin/(len(posPlot1)-1))
    if len(spin_array) > len(posPlot1): spin_array = spin_array[:len(posPlot1)]

    view_angle = np.column_stack((spin_array, 10*np.ones(len(spin_array))))

    R_mats_1 = quatern2rotMat(quatPlot1)
    R_mats_2 = quatern2rotMat(quatPlot2)

    for i in range(R_mats_2.shape[2]):
        R_mats_2[:, :, i] = R_align.dot(R_mats_2[:, :, i])

    # Llamada a la animación
    SixDofAnimation(posPlot1, R_mats_1, 
                    posPlot2, R_mats_2, fs,
                    SamplePlotFreq=SamplePlotFreq, Trail='All',
                    View=view_angle, AxisLength=0.009, ShowArrowHead=True,
                    Xlabel='X (m)', Ylabel='Y (m)', Zlabel='Z (m)', ShowLegend=True)


else:
    # =========================================================================
    # --- DETRENDING ROBUSTO BASADO EN DISTANCIA (SIN ZIG-ZAGS DE BORDE) ---
    # =========================================================================
    dist_total = np.linalg.norm(pos1[-1, 0:2] - pos1[0, 0:2])

    if dist_total > 0.1:  
        def calcular_angulo_tendencia(pos):
            pos_xy = pos[:, 0:2]
            datos_centrados = pos_xy - np.mean(pos_xy, axis=0)
            covarianza = np.cov(datos_centrados, rowvar=False)
            valores, vectores = np.linalg.eigh(covarianza)
            vec_prin = vectores[:, np.argmax(valores)]
            vec_avance = pos_xy[-1] - pos_xy[0]
            if np.dot(vec_prin, vec_avance) < 0:
                vec_prin = -vec_prin
            return np.arctan2(vec_prin[1], vec_prin[0])
            
        angle_1 = calcular_angulo_tendencia(pos1)
        angle_2 = calcular_angulo_tendencia(pos2)
        
        # 1. Rotación inicial del pie
        delta_yaw = angle_1 - angle_2
        cos_a = np.cos(delta_yaw)
        sin_a = np.sin(delta_yaw)

        centro_pos2 = np.mean(pos2[:, 0:2], axis=0)
        pos2[:, 0] -= centro_pos2[0]
        pos2[:, 1] -= centro_pos2[1]

        x_rot = pos2[:, 0] * cos_a - pos2[:, 1] * sin_a
        y_rot = pos2[:, 0] * sin_a + pos2[:, 1] * cos_a
        pos2[:, 0] = x_rot
        pos2[:, 1] = y_rot

        pos2[:, 0] += centro_pos2[0]
        pos2[:, 1] += centro_pos2[1]

        vx_rot = vel2[:, 0] * cos_a - vel2[:, 1] * sin_a
        vy_rot = vel2[:, 0] * sin_a + vel2[:, 1] * cos_a
        vel2[:, 0] = vx_rot
        vel2[:, 1] = vy_rot

        ax_rot = acc2[:, 0] * cos_a - acc2[:, 1] * sin_a
        ay_rot = acc2[:, 0] * sin_a + acc2[:, 1] * cos_a
        acc2[:, 0] = ax_rot
        acc2[:, 1] = ay_rot

        # 2. ELIMINACIÓN DE BARRIGA LIGADA A LA DISTANCIA, NO AL TIEMPO
        dir_fwd = np.array([np.cos(angle_1), np.sin(angle_1)])
        dir_lat = np.array([-np.sin(angle_1), np.cos(angle_1)]) 

        # =====================================================================
        # --- CORRECCIÓN DE BARRIGA PARA SENSOR 1 ---
        # =====================================================================
        pos1_rel = pos1[:, 0:2] - pos1[0, 0:2]
        pos1_uX = np.sum(pos1_rel * dir_fwd, axis=1)
        pos1_uY = np.sum(pos1_rel * dir_lat, axis=1)
        
        x_norm1 = (pos1_uX - pos1_uX[0]) / (pos1_uX[-1] - pos1_uX[0] + 1e-9)
        
        grado_polinomio = 3 
        coefs1 = np.polyfit(x_norm1, pos1_uY, grado_polinomio)
        curva_barriga1 = np.polyval(coefs1, x_norm1)
        
        # La línea de restauración mantiene la naturalidad de la curva si el usuario gira de verdad
        linea_restauracion1 = curva_barriga1[0] + (curva_barriga1[-1] - curva_barriga1[0]) * x_norm1
        pos1_uY_sin_barriga = pos1_uY - curva_barriga1 + linea_restauracion1
        
        pos1_origen_x = pos1[0, 0]
        pos1_origen_y = pos1[0, 1]
        
        pos1[:, 0] = pos1_origen_x + (pos1_uX * dir_fwd[0]) + (pos1_uY_sin_barriga * dir_lat[0])
        pos1[:, 1] = pos1_origen_y + (pos1_uX * dir_fwd[1]) + (pos1_uY_sin_barriga * dir_lat[1])
        # =====================================================================

        pos2_rel = pos2[:, 0:2] - pos2[0, 0:2]

        # Descomponer el pie en Avance (X) y Desviación Lateral (Y)
        pos2_uX = np.sum(pos2_rel * dir_fwd, axis=1)
        pos2_uY = np.sum(pos2_rel * dir_lat, axis=1)
        
        # =====================================================================
        # CORRECCIÓN CRÍTICA: Normalizar basado en avance longitudinal (X)
        # Al hacer esto, si el pie está quieto (fase de stance o inicio/fin), 
        # la corrección también se congela, eliminando los "ganchos" artificiales.
        # =====================================================================
        x_norm = (pos2_uX - pos2_uX[0]) / (pos2_uX[-1] - pos2_uX[0] + 1e-9)
        
        coefs = np.polyfit(x_norm, pos2_uY, grado_polinomio)
        curva_barriga = np.polyval(coefs, x_norm)
        
        # Asegurar que el punto de inicio y fin coincidan perfectamente con la recta
        linea_restauracion = curva_barriga[0] + (curva_barriga[-1] - curva_barriga[0]) * x_norm

        pos2_uY_sin_barriga = pos2_uY - curva_barriga + linea_restauracion

        # 3. UBICAR EL PIE DE FORMA INDEPENDIENTE
        offset_inicial_x = 0.0
        offset_inicial_y = 0.10
        
        pos2[:, 0] = pos1[0, 0] + ((pos2_uX + offset_inicial_x) * dir_fwd[0]) + ((pos2_uY_sin_barriga + offset_inicial_y) * dir_lat[0])
        pos2[:, 1] = pos1[0, 1] + ((pos2_uX + offset_inicial_x) * dir_fwd[1]) + ((pos2_uY_sin_barriga + offset_inicial_y) * dir_lat[1])

    else:
        # Añadido seguro para pos2 respetando estructura si dist_total <= 0.1
        pos2[:, 0] = pos2[:, 0] - pos2[0, 0] + pos1[0, 0]
        pos2[:, 1] = pos2[:, 1] - pos2[0, 1] + pos1[0, 1] + 0.10


    # =========================================================================
    # --- REGLA ESTRICTA AÑADIDA: ASEGURAR PROGRESIÓN HACIA +X y +Y ---
    # =========================================================================
    if pos1[-1, 0] - pos1[0, 0] < 0:
        pos1[:, 0] = -pos1[:, 0]; pos2[:, 0] = -pos2[:, 0]
        vel1[:, 0] = -vel1[:, 0]; vel2[:, 0] = -vel2[:, 0]
        acc1[:, 0] = -acc1[:, 0]; acc2[:, 0] = -acc2[:, 0]
        
    if pos1[-1, 1] - pos1[0, 1] < 0:
        pos1[:, 1] = -pos1[:, 1]; pos2[:, 1] = -pos2[:, 1]
        vel1[:, 1] = -vel1[:, 1]; vel2[:, 1] = -vel2[:, 1]
        acc1[:, 1] = -acc1[:, 1]; acc2[:, 1] = -acc2[:, 1]

    # =========================================================================
    # --- REGLA ESTRICTA AÑADIDA: ASEGURAR QUE AMBOS SENSORES INICIEN EN X=0 ---
    # =========================================================================
    pos1[:, 0] = pos1[:, 0] - pos1[0, 0]
    pos2[:, 0] = pos2[:, 0] - pos2[0, 0]

    # =========================================================================
    # --- REGLA ESTRICTA AÑADIDA: ASEGURAR QUE Z NUNCA SEA NEGATIVO ---
    # =========================================================================
    pos1[:, 2] = np.maximum(pos1[:, 2], 0.0)
    pos2[:, 2] = np.maximum(pos2[:, 2], 0.0)


    # =========================================================================
    # (BLOQUES DE GRÁFICAS ORIGINALES)
    # =========================================================================

    # -------------------------------------------------------------------------
    # Plot translational accelerations
    # -------------------------------------------------------------------------
    fig_acc, (ax_acc1, ax_acc2) = plt.subplots(2, 1, figsize=(10, 6), num='Accelerations', sharex=True)
    ax_acc1.plot(time_vec, acc1[:, 0], 'r', label='X')
    ax_acc1.plot(time_vec, acc1[:, 1], 'g', label='Y')
    ax_acc1.plot(time_vec, acc1[:, 2], 'b', label='Z')
    ax_acc1.set_title(f'Sensor 1 ({canales[0]}) - Acceleration')
    ax_acc1.set_ylabel('Acceleration (m/s/s)')
    ax_acc1.legend()

    ax_acc2.plot(time_vec, acc2[:, 0], 'r', label='X')
    ax_acc2.plot(time_vec, acc2[:, 1], 'g', label='Y')
    ax_acc2.plot(time_vec, acc2[:, 2], 'b', label='Z')
    ax_acc2.set_title(f'Sensor 2 ({canales[1]} - Left Foot) - Acceleration')
    ax_acc2.set_xlabel('Time (s)')
    ax_acc2.set_ylabel('Acceleration (m/s/s)')
    ax_acc2.legend()
    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Plot translational velocity
    # -------------------------------------------------------------------------
    fig_vel, (ax_vel1, ax_vel2) = plt.subplots(2, 1, figsize=(10, 6), num='Velocity', sharex=True)
    ax_vel1.plot(time_vec, vel1[:, 0], 'r', label='X')
    ax_vel1.plot(time_vec, vel1[:, 1], 'g', label='Y')
    ax_vel1.plot(time_vec, vel1[:, 2], 'b', label='Z')
    ax_vel1.set_title(f'Sensor 1 ({canales[0]}) - Velocity')
    ax_vel1.set_ylabel('Velocity (m/s)')
    ax_vel1.legend()

    ax_vel2.plot(time_vec, vel2[:, 0], 'r', label='X')
    ax_vel2.plot(time_vec, vel2[:, 1], 'g', label='Y')
    ax_vel2.plot(time_vec, vel2[:, 2], 'b', label='Z')
    ax_vel2.set_title(f'Sensor 2 ({canales[1]} - Left Foot) - Velocity')
    ax_vel2.set_xlabel('Time (s)')
    ax_vel2.set_ylabel('Velocity (m/s)')
    ax_vel2.legend()
    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Graficar posición traslacional y comparación
    # -------------------------------------------------------------------------
    fig_pos, (ax_pos1, ax_pos2) = plt.subplots(2, 1, figsize=(10, 6), num='Position', sharex=True)
    ax_pos1.plot(time_vec, pos1[:, 0], 'r', label='X')
    ax_pos1.plot(time_vec, pos1[:, 1], 'g', label='Y')
    ax_pos1.plot(time_vec, pos1[:, 2], 'b', label='Z')
    ax_pos1.set_title(f'Sensor 1 ({canales[0]}) - Position')
    ax_pos1.set_ylabel('Position (m)')
    ax_pos1.legend()

    ax_pos2.plot(time_vec, pos2[:, 0], 'r', label='X')
    ax_pos2.plot(time_vec, pos2[:, 1], 'g', label='Y')
    ax_pos2.plot(time_vec, pos2[:, 2], 'b', label='Z')
    ax_pos2.set_title(f'Sensor 2 ({canales[1]} - Left Foot) - Position')
    ax_pos2.set_xlabel('Time (s)')
    ax_pos2.set_ylabel('Position (m)')
    ax_pos2.legend()
    plt.tight_layout()

    # Comparación directa Mov vs Mov2
    fig_comp, (ax_comp1, ax_comp2) = plt.subplots(2, 1, figsize=(10, 6), num='Position Comparison')

    # Plano X-Y
    ax_comp1.plot(pos1[:, 0], pos1[:, 1], color='orange', label=f'{canales[0]} (Sensor 1)')
    ax_comp1.plot(pos2[:, 0], pos2[:, 1], color='green', label=f'{canales[1]} (Sensor 2)')
    ax_comp1.set_title('Trajectory Comparison (X-Y Plane)')
    ax_comp1.set_xlabel('X Position (m)')
    ax_comp1.set_ylabel('Y Position (m)')
    ax_comp1.legend()
    ax_comp1.grid(True)

    # Comparación de Altura (Z vs Time)
    ax_comp2.plot(time_vec, pos1[:, 2], color='orange', label=f'{canales[0]} Height')
    ax_comp2.plot(time_vec, pos2[:, 2], color='green', label=f'{canales[1]} Height')
    ax_comp2.set_title('Height Comparison (Z Axis)')
    ax_comp2.set_xlabel('Time (s)')
    ax_comp2.set_ylabel('Z Position (m)')
    ax_comp2.legend()
    ax_comp2.grid(True)
    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Comparación Vista Y vs Z
    # -------------------------------------------------------------------------
    fig_yz, ax_yz = plt.subplots(1, 1, figsize=(10, 4), num='Y vs Z View')
    ax_yz.plot(pos1[:, 1], pos1[:, 2], color='orange', label=f'{canales[0]} (Sensor 1)')
    ax_yz.plot(pos2[:, 1], pos2[:, 2], color='green', label=f'{canales[1]} (Sensor 2)')
    ax_yz.set_title('Trajectory Comparison (Y-Z Plane)')
    ax_yz.set_xlabel('Y Position (m)')
    ax_yz.set_ylabel('Z Position (m)')
    ax_yz.legend()
    ax_yz.grid(True)
    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Comparación Vista X vs Z
    # -------------------------------------------------------------------------
    fig_xz, ax_xz = plt.subplots(1, 1, figsize=(10, 4), num='X vs Z View')
    ax_xz.plot(pos1[:, 0], pos1[:, 2], color='orange', label=f'{canales[0]} (Sensor 1)')
    ax_xz.plot(pos2[:, 0], pos2[:, 2], color='green', label=f'{canales[1]} (Sensor 2)')
    ax_xz.set_title('Trajectory Comparison (X-Z Plane)')
    ax_xz.set_xlabel('X Position (m)')
    ax_xz.set_ylabel('Z Position (m)')
    ax_xz.legend()
    ax_xz.grid(True)
    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Plot 3D foot trajectory

    posPlot1, quatPlot1 = pos1, quat1
    posPlot2, quatPlot2 = pos2, quat2

    extraTime = 20
    onesVector = np.ones((int(extraTime * (1.0/samplePeriod)), 1))

    # Append extra time Mov
    posPlot_append1 = np.column_stack((posPlot1[-1, 0]*onesVector, posPlot1[-1, 1]*onesVector, posPlot1[-1, 2]*onesVector))
    quatPlot_append1 = np.column_stack((quatPlot1[-1, 0]*onesVector, quatPlot1[-1, 1]*onesVector, quatPlot1[-1, 2]*onesVector, quatPlot1[-1, 3]*onesVector))
    posPlot1 = np.vstack((posPlot1, posPlot_append1))
    quatPlot1 = np.vstack((quatPlot1, quatPlot_append1))

    # Append extra time Mov2
    posPlot_append2 = np.column_stack((posPlot2[-1, 0]*onesVector, posPlot2[-1, 1]*onesVector, posPlot2[-1, 2]*onesVector))
    quatPlot_append2 = np.column_stack((quatPlot2[-1, 0]*onesVector, quatPlot2[-1, 1]*onesVector, quatPlot2[-1, 2]*onesVector, quatPlot2[-1, 3]*onesVector))
    posPlot2 = np.vstack((posPlot2, posPlot_append2))
    quatPlot2 = np.vstack((quatPlot2, quatPlot_append2))

    fs = float(freq_str)
    SamplePlotFreq = 2 if fs == 50.0 else 2
    Spin = 120
    spin_array = np.arange(100, 100+Spin + Spin/(len(posPlot1)-1), Spin/(len(posPlot1)-1))
    if len(spin_array) > len(posPlot1): spin_array = spin_array[:len(posPlot1)]

    view_angle = np.column_stack((spin_array, 10*np.ones(len(spin_array))))

    R_mats_1 = quatern2rotMat(quatPlot1)
    R_mats_2 = quatern2rotMat(quatPlot2)

    for i in range(R_mats_2.shape[2]):
        R_mats_2[:, :, i] = quatern2rotMat(quatPlot2)[..., 0]

    # Llamada a la animación
    SixDofAnimation(posPlot1, R_mats_1, 
                    posPlot2, R_mats_2, fs,
                    SamplePlotFreq=SamplePlotFreq, Trail='All',
                    View=view_angle, AxisLength=0.009, ShowArrowHead=True,
                    Xlabel='X (m)', Ylabel='Y (m)', Zlabel='Z (m)', ShowLegend=True)