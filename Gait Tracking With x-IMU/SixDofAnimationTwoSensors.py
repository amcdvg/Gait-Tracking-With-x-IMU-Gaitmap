import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.lines import Line2D  # Necesario para el estilo de las líneas

def SixDofAnimation(p1, R1, p2, R2, fs, **kwargs):
    numSamples = min(p1.shape[0], p2.shape[0])
    
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
    
    for k, v in kwargs.items():
        if k == 'SamplePlotFreq': SamplePlotFreq = v
        elif k == 'Trail':
            Trail = v
            if Trail not in ['Off', 'DotsOnly', 'All']: raise Exception("Invalid argument")
        elif k == 'View': View = np.array(v)
        elif k == 'AxisLength': AxisLength = v
        elif k == 'Xlabel': Xlabel = v
        elif k == 'Ylabel': Ylabel = v
        elif k == 'Zlabel': Zlabel = v
        elif k == 'Title': Title = v
        elif k == 'ShowLegend': ShowLegend = v
        
    p1 = p1[0:numSamples:SamplePlotFreq, :]
    p2 = p2[0:numSamples:SamplePlotFreq, :]
    R1 = R1[:, :, 0:numSamples:SamplePlotFreq] * AxisLength
    R2 = R2[:, :, 0:numSamples:SamplePlotFreq] * AxisLength
        
    if View.ndim > 1 and len(View) > 2:
        View = View[0:numSamples:SamplePlotFreq, :]
        
    numPlotSamples = p1.shape[0]
    
    fig = plt.figure(num='6DOF Animation', figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    ax.set_xlabel(Xlabel)
    ax.set_ylabel(Ylabel)
    ax.set_zlabel(Zlabel)
    
    if View.ndim == 1:
        ax.view_init(elev=View[1], azim=View[0])
        
    # Inicializar límites dinámicos (UNA sola vez fuera del loop)
    x_min = min(p1[0, 0], p2[0, 0])
    x_max = max(p1[0, 0], p2[0, 0])
    y_min = min(p1[0, 1], p2[0, 1])
    y_max = max(p1[0, 1], p2[0, 1])
    z_min = min(p1[0, 2], p2[0, 2])
    z_max = max(p1[0, 2], p2[0, 2])
    
    # --- CREAR LEYENDA EN LA FIGURA (A prueba de ax.clear) ---
    if ShowLegend:
        custom_lines = [Line2D([0], [0], color='orange', lw=2),
                        Line2D([0], [0], color='cornflowerblue', lw=2)]
        # Se ancla a la figura, por lo que no parpadea ni desaparece
        fig.legend(custom_lines, ['Sensor 1', 'Sensor 2'], 
                   loc='upper right', bbox_to_anchor=(0.95, 0.95), fontsize=12)
    # ---------------------------------------------------------
    
    plt.ion()
    
    for i in range(numPlotSamples):
        ax.clear()
        ax.set_xlabel(Xlabel)
        ax.set_ylabel(Ylabel)
        ax.set_zlabel(Zlabel)
        
        if Title == '':
            ax.set_title(f'Sample {1 + i * SamplePlotFreq} of {numSamples}')
        else:
            ax.set_title(f'{Title} (Sample {1 + i * SamplePlotFreq} of {numSamples})')
            
        if Trail in ['DotsOnly', 'All']:
            #if fs == 50.0:
            ax.plot(p1[0:i+1, 0], p1[0:i+1, 1], p1[0:i+1, 2], color='gray', linewidth=0.5, linestyle='-')
            ax.plot(p2[0:i+1, 0], p2[0:i+1, 1], p2[0:i+1, 2], color='brown', linewidth=0.5, linestyle='-')
            
            # Mov en Naranja, Mov2 en Verde
            ax.plot(p1[0:i+1, 0], p1[0:i+1, 1], p1[0:i+1, 2], color='orange', marker='.', linestyle='None', markersize=5)
            ax.plot(p2[0:i+1, 0], p2[0:i+1, 1], p2[0:i+1, 2], color='cornflowerblue', marker='.', linestyle='None', markersize=5)
        else:
            ax.plot([p1[i, 0]], [p1[i, 1]], [p1[i, 2]], color='orange', marker='.', linestyle='None', markersize=5)
            ax.plot([p2[i, 0]], [p2[i, 1]], [p2[i, 2]], color='cornflowerblue', marker='.', linestyle='None', markersize=5)
            
        # Current origin and axes Mov
        ox1, oy1, oz1 = p1[i, 0], p1[i, 1], p1[i, 2]
        ux1, vx1, wx1 = R1[0, 0, i], R1[1, 0, i], R1[2, 0, i]
        uy1, vy1, wy1 = R1[0, 1, i], R1[1, 1, i], R1[2, 1, i]
        uz1, vz1, wz1 = R1[0, 2, i], R1[1, 2, i], R1[2, 2, i]

        # Current origin and axes Mov2
        ox2, oy2, oz2 = p2[i, 0], p2[i, 1], p2[i, 2]
        ux2, vx2, wx2 = R2[0, 0, i], R2[1, 0, i], R2[2, 0, i]
        uy2, vy2, wy2 = R2[0, 1, i], R2[1, 1, i], R2[2, 1, i]
        uz2, vz2, wz2 = R2[0, 2, i], R2[1, 2, i], R2[2, 2, i]
        
        escala = 0.25 if fs == 50.0 else 1.0

        if Trail == 'All':
            for j in range(i+1):
                # Ejes Mov
                ax.plot([p1[j, 0], p1[j, 0] + R1[0, 0, j] * escala], [p1[j, 1], p1[j, 1] + R1[1, 0, j] * escala], [p1[j, 2], p1[j, 2] + R1[2, 0, j] * escala], color='r', linewidth=0.3, alpha=0.5)
                ax.plot([p1[j, 0], p1[j, 0] + R1[0, 1, j] * escala], [p1[j, 1], p1[j, 1] + R1[1, 1, j] * escala], [p1[j, 2], p1[j, 2] + R1[2, 1, j] * escala], color='g', linewidth=0.3, alpha=0.5)
                ax.plot([p1[j, 0], p1[j, 0] + R1[0, 2, j] * escala], [p1[j, 1], p1[j, 1] + R1[1, 2, j] * escala], [p1[j, 2], p1[j, 2] + R1[2, 2, j] * escala], color='b', linewidth=0.3, alpha=0.5)
                
                # Ejes Mov2
                ax.plot([p2[j, 0], p2[j, 0] + R2[0, 0, j] * escala], [p2[j, 1], p2[j, 1] + R2[1, 0, j] * escala], [p2[j, 2], p2[j, 2] + R2[2, 0, j] * escala], color='r', linewidth=0.3, alpha=0.5)
                ax.plot([p2[j, 0], p2[j, 0] + R2[0, 1, j] * escala], [p2[j, 1], p2[j, 1] + R2[1, 1, j] * escala], [p2[j, 2], p2[j, 2] + R2[2, 1, j] * escala], color='g', linewidth=0.3, alpha=0.5)
                ax.plot([p2[j, 0], p2[j, 0] + R2[0, 2, j] * escala], [p2[j, 1], p2[j, 1] + R2[1, 2, j] * escala], [p2[j, 2], p2[j, 2] + R2[2, 2, j] * escala], color='b', linewidth=0.3, alpha=0.5)
        else:
            # Frame actual Mov
            ax.plot([ox1, ox1 + ux1 * escala], [oy1, oy1 + vx1 * escala], [oz1, oz1 + wx1 * escala], color='r', linewidth=0.3)
            ax.plot([ox1, ox1 + uy1 * escala], [oy1, oy1 + vy1 * escala], [oz1, oz1 + wy1 * escala], color='g', linewidth=0.3)
            ax.plot([ox1, ox1 + uz1 * escala], [oy1, oy1 + vz1 * escala], [oz1, oz1 + wz1 * escala], color='b', linewidth=0.3)
            
            # Frame actual Mov2
            ax.plot([ox2, ox2 + ux2 * escala], [oy2, oy2 + vx2 * escala], [oz2, oz2 + wx2 * escala], color='r', linewidth=0.3)
            ax.plot([ox2, ox2 + uy2 * escala], [oy2, oy2 + vy2 * escala], [oz2, oz2 + wy2 * escala], color='g', linewidth=0.3)
            ax.plot([ox2, ox2 + uz2 * escala], [oy2, oy2 + vz2 * escala], [oz2, oz2 + wz2 * escala], color='b', linewidth=0.3)
        
        # Calcular extremos de los vectores para ambos sensores
        ve_x1 = max(abs(ux1), abs(uy1), abs(uz1))
        ve_y1 = max(abs(vx1), abs(vy1), abs(vz1))
        ve_z1 = max(abs(wx1), abs(wy1), abs(wz1))
        
        ve_x2 = max(abs(ux2), abs(uy2), abs(uz2))
        ve_y2 = max(abs(vx2), abs(vy2), abs(vz2))
        ve_z2 = max(abs(wx2), abs(wy2), abs(wz2))
        
        # Actualizar límites dinámicos acumulados (la corrección del desbordamiento)
        x_min = min(x_min, ox1, ox1 - ve_x1, ox1 + ve_x1, ox2, ox2 - ve_x2, ox2 + ve_x2)
        x_max = max(x_max, ox1, ox1 - ve_x1, ox1 + ve_x1, ox2, ox2 - ve_x2, ox2 + ve_x2)
        y_min = min(y_min, oy1, oy1 - ve_y1, oy1 + ve_y1, oy2, oy2 - ve_y2, oy2 + ve_y2)
        y_max = max(y_max, oy1, oy1 - ve_y1, oy1 + ve_y1, oy2, oy2 - ve_y2, oy2 + ve_y2)
        z_min = min(z_min, oz1, oz1 - ve_z1, oz1 + ve_z1, oz2, oz2 - ve_z1, oz2 + ve_z2)
        z_max = max(z_max, oz1, oz1 - ve_z1, oz1 + ve_z1, oz2, oz2 - ve_z2, oz2 + ve_z2)
        
        margin = 0.2 
        x_range = x_max - x_min if (x_max - x_min) != 0 else 1
        y_range = y_max - y_min if (y_max - y_min) != 0 else 1
        z_range = z_max - z_min if (z_max - z_min) != 0 else 1
            
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