# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

# def SixDofAnimation(p, R, **kwargs):
#     numSamples = p.shape[0]
    
#     # Default values of optional arguments
#     SamplePlotFreq = 1
#     Trail = 'Off'
#     LimitRatio = 1
#     Position = None
#     FullScreen = False
#     View = np.array([30, 20])
#     AxisLength = 1
#     ShowArrowHead = 'on'
#     Xlabel = 'X'
#     Ylabel = 'Y'
#     Zlabel = 'Z'
#     Title = '6DOF Animation'
#     ShowLegend = True
#     CreateAVI = False
#     AVIfileName = '6DOF Animation'
#     AVIfileNameEnum = True
#     AVIfps = 30
    
#     for k, v in kwargs.items():
#         if k == 'SamplePlotFreq': SamplePlotFreq = v
#         elif k == 'Trail':
#             Trail = v
#             if Trail not in ['Off', 'DotsOnly', 'All']:
#                 raise Exception("Invalid argument. Trail must be 'Off', 'DotsOnly' or 'All'.")
#         elif k == 'LimitRatio': LimitRatio = v
#         elif k == 'Position': Position = v
#         elif k == 'FullScreen': FullScreen = v
#         elif k == 'View': View = np.array(v)
#         elif k == 'AxisLength': AxisLength = v
#         elif k == 'ShowArrowHead': ShowArrowHead = v
#         elif k == 'Xlabel': Xlabel = v
#         elif k == 'Ylabel': Ylabel = v
#         elif k == 'Zlabel': Zlabel = v
#         elif k == 'Title': Title = v
#         elif k == 'ShowLegend': ShowLegend = v
#         elif k == 'CreateAVI': CreateAVI = v
#         elif k == 'AVIfileName': AVIfileName = v
#         elif k == 'AVIfileNameEnum': AVIfileNameEnum = v
#         elif k == 'AVIfps': AVIfps = v
#         else: raise Exception('Invalid argument.')
        
#     p = p[0:numSamples:SamplePlotFreq, :]
#     R = R[:, :, 0:numSamples:SamplePlotFreq] * AxisLength
#     if View.ndim > 1 and len(View) > 2:
#         View = View[0:numSamples:SamplePlotFreq, :]
        
#     numPlotSamples = p.shape[0]
    
#     fig = plt.figure(num='6DOF Animation')
#     ax = fig.add_subplot(111, projection='3d')
#     ax.set_xlabel(Xlabel)
#     ax.set_ylabel(Ylabel)
#     ax.set_zlabel(Zlabel)
    
#     if View.ndim == 1:
#         ax.view_init(elev=View[1], azim=View[0])
        
#     x = p[0, 0]
#     y = p[0, 1]
#     z = p[0, 2]
    
#     # Animation loops in matplotlib can be complex, doing a fast static plot placeholder
#     # because 'drawnow' loop inside a function restricts interaction. For literal translation:
#     plt.ion()
    
#     for i in range(numPlotSamples):
#         ax.clear()
#         ax.set_xlabel(Xlabel)
#         ax.set_ylabel(Ylabel)
#         ax.set_zlabel(Zlabel)
        
#         if Title == '':
#             ax.set_title(f'Sample {1 + i * SamplePlotFreq} of {numSamples}')
#         else:
#             ax.set_title(f'{Title} (Sample {1 + i * SamplePlotFreq} of {numSamples})')
            
#         if Trail in ['DotsOnly', 'All']:
#             ax.plot(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], 'k.')
#         else:
#             ax.plot([p[i, 0]], [p[i, 1]], [p[i, 2]], 'k.')
            
#         # Current origin and axes
#         ox, oy, oz = p[i, 0], p[i, 1], p[i, 2]
#         ux, vx, wx = R[0, 0, i], R[1, 0, i], R[2, 0, i]
#         uy, vy, wy = R[0, 1, i], R[1, 1, i], R[2, 1, i]
#         uz, vz, wz = R[0, 2, i], R[1, 2, i], R[2, 2, i]
        
#         if Trail == 'All':
#             ax.quiver(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], R[0, 0, 0:i+1], R[1, 0, 0:i+1], R[2, 0, 0:i+1], color='r')
#             ax.quiver(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], R[0, 1, 0:i+1], R[1, 1, 0:i+1], R[2, 1, 0:i+1], color='g')
#             ax.quiver(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], R[0, 2, 0:i+1], R[1, 2, 0:i+1], R[2, 2, 0:i+1], color='b')
#         else:
#             ax.quiver(ox, oy, oz, ux, vx, wx, color='r')
#             ax.quiver(ox, oy, oz, uy, vy, wy, color='g')
#             ax.quiver(ox, oy, oz, uz, vz, wz, color='b')
            
#         axis_lims = AxisLength * LimitRatio
#         ax.set_xlim([ox - axis_lims, ox + axis_lims])
#         ax.set_ylim([oy - axis_lims, oy + axis_lims])
#         ax.set_zlim([oz - axis_lims, oz + axis_lims])
        
#         if View.ndim > 1:
#             ax.view_init(elev=View[i, 1], azim=View[i, 0])
            
#         plt.draw()
#         plt.pause(0.001)
        
#     plt.ioff()
#     plt.show()
#     return fig
#===================================================
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def SixDofAnimation(p, R, fs, **kwargs):
    numSamples = p.shape[0]
    
    # Default values of optional arguments
    SamplePlotFreq = 1
    Trail = 'Off'
    LimitRatio = 1
    Position = None
    FullScreen = False
    View = np.array([30, 20])
    AxisLength = 1
    ShowArrowHead = 'on'
    Xlabel = 'X'
    Ylabel = 'Y'
    Zlabel = 'Z'
    Title = '6DOF Animation'
    ShowLegend = True
    CreateAVI = False
    AVIfileName = '6DOF Animation'
    AVIfileNameEnum = True
    AVIfps = 30
    
    for k, v in kwargs.items():
        if k == 'SamplePlotFreq': SamplePlotFreq = v
        elif k == 'Trail':
            Trail = v
            if Trail not in ['Off', 'DotsOnly', 'All']:
                raise Exception("Invalid argument. Trail must be 'Off', 'DotsOnly' or 'All'.")
        elif k == 'LimitRatio': LimitRatio = v
        elif k == 'Position': Position = v
        elif k == 'FullScreen': FullScreen = v
        elif k == 'View': View = np.array(v)
        elif k == 'AxisLength': AxisLength = v
        elif k == 'ShowArrowHead': ShowArrowHead = v
        elif k == 'Xlabel': Xlabel = v
        elif k == 'Ylabel': Ylabel = v
        elif k == 'Zlabel': Zlabel = v
        elif k == 'Title': Title = v
        elif k == 'ShowLegend': ShowLegend = v
        elif k == 'CreateAVI': CreateAVI = v
        elif k == 'AVIfileName': AVIfileName = v
        elif k == 'AVIfileNameEnum': AVIfileNameEnum = v
        elif k == 'AVIfps': AVIfps = v
        else: raise Exception('Invalid argument.')
        
    p = p[0:numSamples:SamplePlotFreq, :]
    R = R[:, :, 0:numSamples:SamplePlotFreq] * AxisLength
    if View.ndim > 1 and len(View) > 2:
        View = View[0:numSamples:SamplePlotFreq, :]
        
    numPlotSamples = p.shape[0]
    
    #fig = plt.figure(num='6DOF Animation')
    fig = plt.figure(num='6DOF Animation', figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    ax.set_xlabel(Xlabel)
    ax.set_ylabel(Ylabel)
    ax.set_zlabel(Zlabel)
    
    if View.ndim == 1:
        ax.view_init(elev=View[1], azim=View[0])
        
    x = p[0, 0]
    y = p[0, 1]
    z = p[0, 2]
    
    # Inicializar límites dinámicos
    x_min, x_max = p[0, 0], p[0, 0]
    y_min, y_max = p[0, 1], p[0, 1]
    z_min, z_max = p[0, 2], p[0, 2]
    
    # Animation loops in matplotlib can be complex, doing a fast static plot placeholder
    # because 'drawnow' loop inside a function restricts interaction. For literal translation:
    plt.ion()
    
    for i in range(numPlotSamples):
        ax.clear()
        ax.set_xlabel(Xlabel)
        ax.set_ylabel(Ylabel)
        ax.set_zlabel(Zlabel)
        
        # if Title == '':
        #     ax.set_title(f'Sample {1 + i * SamplePlotFreq} of {numSamples}')
        # else:
        #     ax.set_title(f'{Title} (Sample {1 + i * SamplePlotFreq} of {numSamples})')
            
        # if Trail in ['DotsOnly', 'All']:
        #     #ax.plot(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], 'k.')
        #     ax.plot(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], 'y.', markersize=5)
        # else:
        #     #ax.plot([p[i, 0]], [p[i, 1]], [p[i, 2]], 'k.')
        #     ax.plot([p[i, 0]], [p[i, 1]], [p[i, 2]], 'y.', markersize=5)
        if Title == '':
            ax.set_title(f'Sample {1 + i * SamplePlotFreq} of {numSamples}')
        else:
            ax.set_title(f'{Title} (Sample {1 + i * SamplePlotFreq} of {numSamples})')
            
        if Trail in ['DotsOnly', 'All']:
            # Dibuja una línea continua gris clara para unir la trayectoria
            if fs == 50.0:
                ax.plot(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], color='gray', linewidth=0.5, linestyle='-')
            # Dibuja los puntos de muestreo encima
            ax.plot(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], 'y.', markersize=5)
        else:
            ax.plot([p[i, 0]], [p[i, 1]], [p[i, 2]], 'y.', markersize=5)
            
        # Current origin and axes
        ox, oy, oz = p[i, 0], p[i, 1], p[i, 2]
        ux, vx, wx = R[0, 0, i], R[1, 0, i], R[2, 0, i]
        uy, vy, wy = R[0, 1, i], R[1, 1, i], R[2, 1, i]
        uz, vz, wz = R[0, 2, i], R[1, 2, i], R[2, 2, i]
        
        # if Trail == 'All':
        #     # ax.quiver(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], R[0, 0, 0:i+1], R[1, 0, 0:i+1], R[2, 0, 0:i+1], color='r', linewidth=0.5)
        #     # ax.quiver(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], R[0, 1, 0:i+1], R[1, 1, 0:i+1], R[2, 1, 0:i+1], color='g', linewidth=0.5)
        #     # ax.quiver(p[0:i+1, 0], p[0:i+1, 1], p[0:i+1, 2], R[0, 2, 0:i+1], R[1, 2, 0:i+1], R[2, 2, 0:i+1], color='b', linewidth=0.5)
        #     for j in range(i+1):
        #         ax.plot([p[j, 0], p[j, 0] + R[0, 0, j]], [p[j, 1], p[j, 1] + R[1, 0, j]], [p[j, 2], p[j, 2] + R[2, 0, j]], color='r', linewidth=0.3, alpha=0.5)
        #         ax.plot([p[j, 0], p[j, 0] + R[0, 1, j]], [p[j, 1], p[j, 1] + R[1, 1, j]], [p[j, 2], p[j, 2] + R[2, 1, j]], color='g', linewidth=0.3, alpha=0.5)
        #         ax.plot([p[j, 0], p[j, 0] + R[0, 2, j]], [p[j, 1], p[j, 1] + R[1, 2, j]], [p[j, 2], p[j, 2] + R[2, 2, j]], color='b', linewidth=0.3, alpha=0.5)
        # else:
        #     # ax.quiver(ox, oy, oz, ux, vx, wx, color='r', linewidth=0.5)
        #     # ax.quiver(ox, oy, oz, uy, vy, wy, color='g', linewidth=0.5)
        #     # ax.quiver(ox, oy, oz, uz, vz, wz, color='b', linewidth=0.5)
        #     ax.plot([ox, ox + ux], [oy, oy + vx], [oz, oz + wx], color='r', linewidth=0.3)
        #     ax.plot([ox, ox + uy], [oy, oy + vy], [oz, oz + wy], color='g', linewidth=0.3)
        #     ax.plot([ox, ox + uz], [oy, oy + vz], [oz, oz + wz], color='b', linewidth=0.3)

        # Cambia este valor para estirar o encoger las líneas (ejemplo: 2.0 es el doble de largo)
        if fs == 50.0:
            escala = 0.25 
        else:
            escala = 1.0

        if Trail == 'All':
            for j in range(i+1):
                # Eje X (Rojo) - Multiplicamos cada componente de R por la escala
                ax.plot([p[j, 0], p[j, 0] + R[0, 0, j] * escala], 
                        [p[j, 1], p[j, 1] + R[1, 0, j] * escala], 
                        [p[j, 2], p[j, 2] + R[2, 0, j] * escala], 
                        color='r', linewidth=0.3, alpha=0.5)
                
                # Eje Y (Verde)
                ax.plot([p[j, 0], p[j, 0] + R[0, 1, j] * escala], 
                        [p[j, 1], p[j, 1] + R[1, 1, j] * escala], 
                        [p[j, 2], p[j, 2] + R[2, 1, j] * escala], 
                        color='g', linewidth=0.3, alpha=0.5)
                
                # Eje Z (Azul)
                ax.plot([p[j, 0], p[j, 0] + R[0, 2, j] * escala], 
                        [p[j, 1], p[j, 1] + R[1, 2, j] * escala], 
                        [p[j, 2], p[j, 2] + R[2, 2, j] * escala], 
                        color='b', linewidth=0.3, alpha=0.5)
        else:
            # Caso para el frame actual (ox, oy, oz son el origen; ux, vx, wx son el vector X, etc.)
            ax.plot([ox, ox + ux * escala], [oy, oy + vx * escala], [oz, oz + wx * escala], color='r', linewidth=0.3)
            ax.plot([ox, ox + uy * escala], [oy, oy + vy * escala], [oz, oz + wy * escala], color='g', linewidth=0.3)
            ax.plot([ox, ox + uz * escala], [oy, oy + vz * escala], [oz, oz + wz * escala], color='b', linewidth=0.3)
        
        # Actualizar límites dinámicos incluyendo también los extremos de los vectores
        # Calcular extremos de los vectores para incluir en los límites
        vector_end_x = max(abs(ux), abs(uy), abs(uz))
        vector_end_y = max(abs(vx), abs(vy), abs(vz))
        vector_end_z = max(abs(wx), abs(wy), abs(wz))
        
        x_min = min(x_min, ox, ox - vector_end_x, ox + vector_end_x)
        x_max = max(x_max, ox, ox - vector_end_x, ox + vector_end_x)
        y_min = min(y_min, oy, oy - vector_end_y, oy + vector_end_y)
        y_max = max(y_max, oy, oy - vector_end_y, oy + vector_end_y)
        z_min = min(z_min, oz, oz - vector_end_z, oz + vector_end_z)
        z_max = max(z_max, oz, oz - vector_end_z, oz + vector_end_z)
        
        # Aplicar límites dinámicos con margen
        margin = 0.2  # 20% de margen
        x_range = x_max - x_min
        y_range = y_max - y_min
        z_range = z_max - z_min
        
        if x_range == 0:
            x_range = 1
        if y_range == 0:
            y_range = 1
        if z_range == 0:
            z_range = 1
            
        ax.set_xlim([x_min - x_range * margin, x_max + x_range * margin])
        ax.set_ylim([y_min - y_range * margin, y_max + y_range * margin])
        ax.set_zlim([z_min - z_range * margin, z_max + z_range * margin])
        
        if View.ndim > 1:
            ax.view_init(elev=View[i, 1], azim=View[i, 0])
            
        plt.draw()
        plt.pause(0.001)
        
    plt.ioff()
    plt.show()
    return fig
