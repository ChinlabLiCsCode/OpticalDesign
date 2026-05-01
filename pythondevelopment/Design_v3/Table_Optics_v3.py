import pyopticaltable as pyopt
import matplotlib.pyplot as plt
import pandas as pd
import os


# Coordinate conversion functions
def x_conv(x):
    return x - 29

def y_conv(y):
    return y - 45

def minus_90_conv(angle_):
    return angle_ - 90

def plus_90_conv(angle_):
    return angle_ + 90

# Displacement and label settings
x_displacement = 0
y_displacement = 0
label_position = 'top'
label_color = 'dodgerblue'
edge_width = 7

# Create the optical table
table = pyopt.OpticalTable(60, 92, size_factor=20, show_edge=True, show_grid=True, grid_spacing=1)
descaling_factor = 60/92



x_displacement_2 = 5
y_displacement_2 = 4
linestyle = '--'
transparency = 0.5
edge_width_2 = 3

# Draw outer table edges
x1_15, x2_15, y1_15, y2_15 = table.angled_line(x=x_conv(-0.5), y=y_conv(45), size=91/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_15, x2_15], [y1_15, y2_15], color='darkblue', linewidth=edge_width)
x1_16, x2_16, y1_16, y2_16 = table.angled_line(x=x_conv(29), y=y_conv(-0.5), size=59/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_16, x2_16], [y1_16, y2_16], color='darkblue', linewidth=edge_width)
x1_17, x2_17, y1_17, y2_17 = table.angled_line(x=x_conv(58.5), y=y_conv(45), size=91/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_17, x2_17], [y1_17, y2_17], color='darkblue', linewidth=edge_width)
x1_18, x2_18, y1_18, y2_18 = table.angled_line(x=x_conv(29), y=y_conv(90.5), size=59/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_18, x2_18], [y1_18, y2_18], color='darkblue', linewidth=edge_width)

# Draw left breadboard
x1_1, x2_1, y1_1, y2_1 = table.angled_line(x=x_conv(13 + x_displacement_2), y=y_conv(-0.5 + y_displacement_2), size=27/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_1, x2_1], [y1_1, y2_1], color='blue', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_2, x2_2, y1_2, y2_2 = table.angled_line(x=x_conv(-0.5 + x_displacement_2), y=y_conv(25 + y_displacement_2), size=51/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_2, x2_2], [y1_2, y2_2], color='blue', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_3, x2_3, y1_3, y2_3 = table.angled_line(x=x_conv(26.5 + x_displacement_2), y=y_conv(12.5 + y_displacement_2), size=26/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_3, x2_3], [y1_3, y2_3], color='blue', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_4, x2_4, y1_4, y2_4 = table.angled_line(x=x_conv(23.5 + x_displacement_2), y=y_conv(25.5 + y_displacement_2), size=6/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_4, x2_4], [y1_4, y2_4], color='blue', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_5, x2_5, y1_5, y2_5 = table.angled_line(x=x_conv(20.5 + x_displacement_2), y=y_conv(38 + y_displacement_2), size=25/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_5, x2_5], [y1_5, y2_5], color='blue', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_6, x2_6, y1_6, y2_6 = table.angled_line(x=x_conv(10 + x_displacement_2), y=y_conv(50.5 + y_displacement_2), size=21/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_6, x2_6], [y1_6, y2_6], color='blue', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)

# Draw right breadboard
x1_7, x2_7, y1_7, y2_7 = table.angled_line(x=x_conv(38 + x_displacement_2), y=y_conv(-0.5 + y_displacement_2), size=21/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_7, x2_7], [y1_7, y2_7], color='purple', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_8, x2_8, y1_8, y2_8 = table.angled_line(x=x_conv(48.5 + x_displacement_2), y=y_conv(40 + y_displacement_2), size=81/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_8, x2_8], [y1_8, y2_8], color='purple', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_9, x2_9, y1_9, y2_9 = table.angled_line(x=x_conv(27.5 + x_displacement_2), y=y_conv(25 + y_displacement_2), size=51/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_9, x2_9], [y1_9, y2_9], color='purple', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_10, x2_10, y1_10, y2_10 = table.angled_line(x=x_conv(30.5 + x_displacement_2), y=y_conv(50.5 + y_displacement_2), size=6/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_10, x2_10], [y1_10, y2_10], color='purple', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_11, x2_11, y1_11, y2_11 = table.angled_line(x=x_conv(33.5 + x_displacement_2), y=y_conv(58.5 + y_displacement_2), size=16/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_11, x2_11], [y1_11, y2_11], color='purple', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_12, x2_12, y1_12, y2_12 = table.angled_line(x=x_conv(30.5 + x_displacement_2), y=y_conv(66.5 + y_displacement_2), size=6/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_12, x2_12], [y1_12, y2_12], color='purple', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_13, x2_13, y1_13, y2_13 = table.angled_line(x=x_conv(27.5 + x_displacement_2), y=y_conv(73.5 + y_displacement_2), size=14/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_13, x2_13], [y1_13, y2_13], color='purple', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)
x1_14, x2_14, y1_14, y2_14 = table.angled_line(x=x_conv(38 + x_displacement_2), y=y_conv(80.5 + y_displacement_2), size=21/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_14, x2_14], [y1_14, y2_14], color='purple', linewidth=edge_width_2, linestyle=linestyle, alpha=transparency)

# Draw other features
center = table.generic_circle(x=x_conv(29), y=y_conv(40), size=0.5, colour='gold', fill=True, fillcolour='gold', label='center',
                                        label_pos=label_position, labelpad=0.5, textcolour=label_color)
lower_hole = table.generic_circle(x=x_conv(7), y=y_conv(11), size=0.5, colour='red', fill=False, fillcolour='k', label='hole',
                                        label_pos='bottom', labelpad=0.35, textcolour=label_color)
upper_hole = table.generic_circle(x=x_conv(7), y=y_conv(47), size=0.5, colour='red', fill=False, fillcolour='k', label='hole',
                                        label_pos='bottom', labelpad=0.35, textcolour=label_color)
ion_pump_1 = table.box(x=x_conv(29), y=y_conv(32.5), size_x=6.5, size_y=12.5, angle=-45, linestyle='-', standalone=True,
                                        label='ion pump', label_pos=label_position, labelpad=0, textcolour=label_color)
ion_pump_2 = table.box(x=x_conv(22), y=y_conv(25.5), size_x=2, size_y=7.5, angle=-45, linestyle='-', standalone=True,
                                        label='', label_pos=label_position, labelpad=0, textcolour=label_color)

df = pd.read_csv('OpticsSetupTable_v3.csv')
optical_elements = {}


# Define laser beams

fiber_launcher_size_x = 1.55
fiber_launcher_size_y = 2
laser_label_font_size = 17

Li_MOT_1 = pyopt.LaserBeam(colour='purple', width=1, style='-')
Li_MOT_1_Path = []
Li_MOT_2 = pyopt.LaserBeam(colour='purple', width=1, style='-')
Li_MOT_2_Path = []
Li_MOT_1_Path.append(table.point_source(x=x_conv(7 + x_displacement), y=y_conv(11 + y_displacement), label='Li MOT', label_pos=label_position, labelpad=2.2, textcolour=label_color, fontsize=laser_label_font_size))

Cs_MOT_1 = pyopt.LaserBeam(colour='green', width=1, style='-')
Cs_MOT_1_Path = []
Cs_MOT_2 = pyopt.LaserBeam(colour='green', width=1, style='-')
Cs_MOT_2_Path = []
Cs_MOT_1_Path.append(table.point_source(x=x_conv(7 + x_displacement), y=y_conv(11 + y_displacement), label='Cs MOT', label_pos=label_position, labelpad=1, textcolour=label_color, fontsize=laser_label_font_size))

Cs_V_Imaging_1 = pyopt.LaserBeam(colour='orchid', width=1, style='-')
Cs_V_Imaging_1_Path = []
Cs_V_Imaging_2 = pyopt.LaserBeam(colour='orchid', width=1, style='-')
Cs_V_Imaging_2_Path = []
optical_elements[203] = table.box_source(x=x_conv(4 + x_displacement), y=y_conv(19 + y_displacement), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=0, output_side='right', label='O-203 Cs V Imaging', label_pos=label_position, labelpad=1, textcolour=label_color, fontsize=laser_label_font_size)
Cs_V_Imaging_1_Path.append(optical_elements[203])

Li_V_Imaging_1 = pyopt.LaserBeam(colour='deepskyblue', width=1, style='-')
Li_V_Imaging_1_Path = []
Li_V_Imaging_2 = pyopt.LaserBeam(colour='deepskyblue', width=1, style='-')
Li_V_Imaging_2_Path = []
optical_elements[225] = table.box_source(x=x_conv(4 + x_displacement), y=y_conv(30 + y_displacement), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=0, output_side='right', label='O-225 Li V Imaging', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Li_V_Imaging_1_Path.append(optical_elements[225])

Cs_V_Optical_Pump_3 = pyopt.LaserBeam(colour='navy', width=1, style='-')
Cs_V_Optical_Pump_3_Path = []
Cs_V_Optical_Pump_4 = pyopt.LaserBeam(colour='navy', width=1, style='-')
Cs_V_Optical_Pump_4_Path = []
Cs_V_Optical_Pump_3_Path.append(table.point_source(x=x_conv(7 + x_displacement), y=y_conv(11 + y_displacement), label='O-116 Cs V Optical Pump', label_pos=label_position, labelpad=1.4, textcolour=label_color, fontsize=laser_label_font_size))

RSC_3 = pyopt.LaserBeam(colour='coral', width=1, style='-')
RSC_3_Path = []
RSC_4 = pyopt.LaserBeam(colour='coral', width=1, style='-')
RSC_4_Path = []
RSC_3_Path.append(table.point_source(x=x_conv(7 + x_displacement), y=y_conv(11 + y_displacement), label='O-110 RSC', label_pos=label_position, labelpad=1.8, textcolour=label_color, fontsize=laser_label_font_size))


for _, row in df.iterrows():

    limit = 340
    done = 0

    label = row['Label'].strip()
    i = float(label.split('-')[1])

    if i > limit:
        break

    type_ = row['Type'].strip()
    try:
        x = x_conv(float(row['Position x']))
        y = y_conv(float(row['Position y']))
        angle = float(row['Orientation'])

    except:
        x = 0
        y = 0
        angle = 0


    if type_ == 'mirror' or type_ == 'tall mirror' or type_ == 'periscope mirror':
        optical_elements[i] = table.mirror(x=x + x_displacement, y=y + y_displacement, size=1 / descaling_factor, angle=minus_90_conv(angle),
                                           label=label+' '+type_, label_pos=label_position, labelpad=0, textcolour=label_color)
    elif type_ == 'large mirror':
        optical_elements[i] = table.mirror(x=x + x_displacement, y=y + y_displacement, size=2 / descaling_factor, angle=minus_90_conv(angle),
                                           label=label + ' ' + type_, label_pos=label_position, labelpad=0,
                                           textcolour=label_color)
    elif type_ == 'beam sampler':
        optical_elements[i] = table.mirror(x=x + x_displacement, y=y + y_displacement, size=1 / descaling_factor, angle=minus_90_conv(angle), colour='teal',
                                           label=label + ' ' + type_, label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'quadrant mirror' or type_ == 'small mirror':
        optical_elements[i] = table.mirror(x=x + x_displacement, y=y + y_displacement, size=0.4/descaling_factor, angle=minus_90_conv(angle),
                                           label=label+' '+type_, label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'dichroic mirror':
        optical_elements[i] = table.mirror(x=x + x_displacement, y=y + y_displacement, size=2/descaling_factor, angle=minus_90_conv(angle), colour='orange',
                                           label=label + ' ' + type_, label_pos=label_position, labelpad=0, textcolour=label_color)
    elif type_ == 'small dichroic mirror':
        optical_elements[i] = table.mirror(x=x + x_displacement, y=y + y_displacement, size=0.5 / descaling_factor, angle=minus_90_conv(angle),
                                           colour='orange',
                                           label=label + ' ' + type_, label_pos=label_position, labelpad=0,
                                           textcolour=label_color)
    elif type_ == 'dump':
        optical_elements[i] = table.beam_dump(x=x + x_displacement, y=y + y_displacement, size=0.6/descaling_factor, angle=minus_90_conv(angle), colour='k', fillcolour='k',
                                              label=label+' '+type_, label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'water-cooled beam dump':
        optical_elements[i] = table.generic_circle(x=x + x_displacement, y=y + y_displacement, size=0.5, colour='blue', fill=False, fillcolour='k',
                                                   label=label + ' ' + type_, label_pos=label_position, labelpad=0.3, textcolour=label_color)
    elif type_ == 'iris':
        optical_elements[i] = table.box(x=x + x_displacement, y=y + y_displacement, size_x=0.1, size_y=1, angle=angle, linestyle='-.', standalone=True,
                                        label=label+' '+type_, label_pos=label_position, labelpad=0.6, textcolour=label_color)
    elif type_ == 'PBS':
        optical_elements[i] = table.beamsplitter_cube(x=x + x_displacement, y=y + y_displacement, size=0.7/descaling_factor, angle=angle, direction='R',
                                                      label=label+' '+type_, label_pos=label_position, labelpad=0.2, textcolour=label_color)
    elif type_ == 'large PBS':
        optical_elements[i] = table.beamsplitter_cube(x=x + x_displacement, y=y + y_displacement, size=1 / descaling_factor, angle=angle, direction='R',
                                                      label=label + ' ' + type_, label_pos=label_position, labelpad=0.2,
                                                      textcolour=label_color)
    elif type_ == 'waveplate' or type_ == 'tall waveplate':
        optical_elements[i] = table.transmissive_plate(x=x + x_displacement, y=y + y_displacement, size=0.7/descaling_factor, angle=minus_90_conv(angle), fill=True, fillcolour='c',
                                                       label=label+' '+type_, label_pos=label_position, labelpad=0.05, textcolour=label_color)
    elif type_ == 'double waveplate':
        optical_elements[i] = table.box(x=x + x_displacement, y=y + y_displacement, size_x=1.5,
                                          size_y=1.5, angle=angle, colour='c', standalone=True,
                                          label=label+' '+type_,
                                          label_pos=label_position, labelpad=0.4, textcolour=label_color)
    elif type_ == 'lens':
        optical_elements[i] = table.convex_lens(x=x + x_displacement, y=y + y_displacement, size=1/descaling_factor, angle=plus_90_conv(angle),
                                                label=label+' '+type_, label_pos=label_position, labelpad=0, textcolour=label_color)
    elif type_ == 'PD':
        optical_elements[i] = table.box(x=x + x_displacement, y=y + y_displacement, size_x=1, size_y=2, angle=angle, linestyle='--', standalone=True,
                                        label=label+' '+type_, label_pos=label_position, labelpad=0.8, textcolour=label_color)
    elif type_ == 'small PD':
        optical_elements[i] = table.box(x=x + x_displacement, y=y + y_displacement, size_x=1, size_y=1, angle=angle, linestyle='--', standalone=True,
                                        label=label + ' ' + type_, label_pos=label_position, labelpad=0.8, textcolour=label_color)
    elif type_ == 'chamber port':
        optical_elements[i] = table.box(x=x + x_displacement, y=y + y_displacement, size_x=0.3, size_y=2, angle=angle, standalone=True,
                                        label=label+' '+type_, label_pos=label_position, labelpad=0.35, textcolour=label_color)
    elif type_ == 'post':
        optical_elements[i] = table.generic_circle(x=x + x_displacement, y=y + y_displacement, size=0.5, colour='k', fill=False, fillcolour='k',
                                                   label=label+' '+type_, label_pos=label_position, labelpad=0.35, textcolour=label_color)
    elif type_ == 'AOM':
        optical_elements[i] = table.box(x=x + x_displacement, y=y + y_displacement, size_x=1, size_y=2, angle=angle, colour='k', linestyle='-.', standalone=True,
                                        label=label+' '+type_, label_pos=label_position, labelpad=0.6, textcolour=label_color)
    elif type_ == '50-50 beam splitter':
        optical_elements[i] = table.mirror(x=x + x_displacement, y=y + y_displacement, size=0.5 / descaling_factor, angle=minus_90_conv(angle),
                                        label=label+' '+type_, label_pos='top', labelpad=0.1, textcolour=label_color)
    elif type_ == 'camera':
        optical_elements[i] = table.box(x=x + x_displacement, y=y + y_displacement, size_x=1, size_y=2, angle=angle, linestyle='-.', standalone=True,
                                        label=label+' '+type_, label_pos=label_position, labelpad=0.6, textcolour=label_color)
    else:
        if i > done:
            print(f"Skipping unknown element: {label + ' ' + type_}")





def draw_beam(beam, path, list):
    for l in list:
        path.append(optical_elements[l])
    beam.draw(table, path)

draw_beam(Li_MOT_1, Li_MOT_1_Path, 
          [228, 222, 221, 220, 211, 210, 215, 216, 212, 217, 230, 303])

draw_beam(Cs_MOT_1, Cs_MOT_1_Path, 
          [228, 200, 197, 218, 199, 196, 209, 208, 207, 206, 212, 217, 230, 303])

draw_beam(Cs_V_Imaging_1, Cs_V_Imaging_1_Path,
          [205, 331, 202, 209, 208, 207, 206, 212, 217, 230, 303])

draw_beam(Li_V_Imaging_1, Li_V_Imaging_1_Path,
          [224, 223, 212, 217, 230, 303])

draw_beam(Cs_V_Optical_Pump_3, Cs_V_Optical_Pump_3_Path,
          [228, 219, 192, 193, 214, 217, 230, 303])

draw_beam(RSC_3, RSC_3_Path,
          [228, 219, 192, 193, 214, 217, 230, 303])


file_path = "table_optics_v3.pdf"
try:
    os.remove(file_path)
    print(f"File {file_path} deleted successfully")
except FileNotFoundError:
    print(f"File {file_path} not found")
except PermissionError:
    print(f"Permission denied to delete {file_path}")
except Exception as e:
    print(f"Error deleting file: {e}")

# Save the plot
plt.savefig(file_path, dpi=100, bbox_inches="tight", facecolor="white", transparent=False)

# Optionally display the plot
# plt.show()
