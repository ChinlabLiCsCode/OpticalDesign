import pyopticaltable as pyopt
import matplotlib.pyplot as plt
import pandas as pd
import os


# Coordinate conversion functions
def x_conv(x):
    return x - 29

def y_conv(y):
    return y - 38

def minus_90_conv(angle_):
    return angle_ - 90

def plus_90_conv(angle_):
    return angle_ + 90


# Create the optical table
table = pyopt.OpticalTable(60, 78, size_factor=20, show_edge=True, show_grid=True, grid_spacing=1)

edge_width = 7

x1_1, x2_1, y1_1, y2_1 = table.angled_line(x=x_conv(-0.5), y=y_conv(38), size=100, angle=90, show=False, get_coords=True)
table.ax.plot([x1_1, x2_1], [y1_1, y2_1], color='blue', linewidth=edge_width)

x1_2, x2_2, y1_2, y2_2 = table.angled_line(x=x_conv(29), y=y_conv(-0.5), size=76.5, angle=0, show=False, get_coords=True)
table.ax.plot([x1_2, x2_2], [y1_2, y2_2], color='blue', linewidth=edge_width)

x1_3, x2_3, y1_3, y2_3 = table.angled_line(x=x_conv(58.5), y=y_conv(38), size=100, angle=90, show=False, get_coords=True)
table.ax.plot([x1_3, x2_3], [y1_3, y2_3], color='blue', linewidth=edge_width)

x1_4, x2_4, y1_4, y2_4 = table.angled_line(x=x_conv(29), y=y_conv(76.5), size=76.5, angle=0, show=False, get_coords=True)
table.ax.plot([x1_4, x2_4], [y1_4, y2_4], color='blue', linewidth=edge_width)


df = pd.read_csv('OpticsSetup(OpticsTable).csv')


label_position = 'top'
label_color = 'dodgerblue'
laser_box_size_x = 0.5
laser_box_size_y = 1
laser_label_font_size = 20
optical_elements = {}


# Define laser beams

Li_MOT_1 = pyopt.LaserBeam(colour='purple', width=2, style='-')
Li_MOT_1_Path = []
Li_MOT_2 = pyopt.LaserBeam(colour='purple', width=2, style='-')
Li_MOT_2_Path = []
Li_MOT_1_Path.append(table.point_source(x=x_conv(27), y=y_conv(48.6), label='Li MOT', label_pos=label_position, labelpad=1.5, textcolour=label_color, fontsize=laser_label_font_size))

Cs_MOT_1 = pyopt.LaserBeam(colour='green', width=2, style='-')
Cs_MOT_1_Path = []
Cs_MOT_2 = pyopt.LaserBeam(colour='green', width=2, style='-')
Cs_MOT_2_Path = []
Cs_MOT_1_Path.append(table.point_source(x=x_conv(27), y=y_conv(48.4), label='Cs MOT', label_pos=label_position, labelpad=1, textcolour=label_color, fontsize=laser_label_font_size))

Li_Repump_1 = pyopt.LaserBeam(colour='lime', width=2, style='-')
Li_Repump_1_Path = []
Li_Repump_2 = pyopt.LaserBeam(colour='lime', width=2, style='-')
Li_Repump_2_Path = []
Li_Repump_1_Path.append(table.point_source(x=x_conv(27), y=y_conv(48.65), label='Li Repump', label_pos=label_position, labelpad=2, textcolour=label_color, fontsize=laser_label_font_size))

Cs_V_Imaging_1 = pyopt.LaserBeam(colour='orchid', width=2, style='-')
Cs_V_Imaging_1_Path = []
Cs_V_Imaging_2 = pyopt.LaserBeam(colour='orchid', width=2, style='-')
Cs_V_Imaging_2_Path = []
optical_elements[203] = table.box_source(x=x_conv(8.5), y=y_conv(41.9), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=0, output_side='right', label='O-203 Cs V Imaging', label_pos=label_position, labelpad=1, textcolour=label_color, fontsize=laser_label_font_size)
Cs_V_Imaging_1_Path.append(optical_elements[203])

Li_V_Imaging_1 = pyopt.LaserBeam(colour='deepskyblue', width=2, style='-')
Li_V_Imaging_1_Path = []
Li_V_Imaging_2 = pyopt.LaserBeam(colour='deepskyblue', width=2, style='-')
Li_V_Imaging_2_Path = []
optical_elements[225] = table.box_source(x=x_conv(24), y=y_conv(45.5), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=180, output_side='right', label='O-225 Li V Imaging', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Li_V_Imaging_1_Path.append(optical_elements[225])

Cs_V_Optical_Pump_3 = pyopt.LaserBeam(colour='navy', width=2, style='-')
Cs_V_Optical_Pump_3_Path = []
Cs_V_Optical_Pump_4 = pyopt.LaserBeam(colour='navy', width=2, style='-')
Cs_V_Optical_Pump_4_Path = []
Cs_V_Optical_Pump_3_Path.append(table.point_source(x=x_conv(6), y=y_conv(39), label='O-116 Cs V Optical Pump', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size))

RSC_3 = pyopt.LaserBeam(colour='coral', width=2, style='-')
RSC_3_Path = []
RSC_4 = pyopt.LaserBeam(colour='coral', width=2, style='-')
RSC_4_Path = []
RSC_3_Path.append(table.point_source(x=x_conv(6.05), y=y_conv(39), label='O-110 RSC', label_pos=label_position, labelpad=1.2, textcolour=label_color, fontsize=laser_label_font_size))

OTOP_1 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_1_Path = []
OTOP_2 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_2_Path = []
OTOP_3 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_3_Path = []
OTOP_4 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_4_Path = []
optical_elements[267] = table.box_source(x=x_conv(44.5), y=y_conv(68), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=-90, output_side='right', label='O-267 OTOP', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
OTOP_1_Path.append(optical_elements[267])


for _, row in df.iterrows():

    limit = 305
    done = 0

    label = row['Label'].strip()
    i = float(label.split('-')[1])

    if i > limit:
        break

    if i in [212, 217, 230, 293, 300]:
        continue

    type_ = row['Type'].strip()
    try:
        x = x_conv(float(row['Position x']))
        y = y_conv(float(row['Position y']))
        angle = float(row['Orientation'])

    except:
        x = 0
        y = 0
        angle = 0


    if i in optical_elements:
        optical_elements[i] = [optical_elements[i]]

    if type_ in 'mirror' or type_ == 'periscope mirror' or type_ == 'tall mirror':
        optical_elements[i] = table.mirror(x=x, y=y, size=0.4, angle=minus_90_conv(angle), label=label+' '+type_,
                                           label_pos=label_position, labelpad=0.02, textcolour=label_color)
    elif type_ == 'quadrant mirror':
        optical_elements[i] = table.mirror(x=x, y=y, size=0.3, angle=minus_90_conv(angle), label=label + ' ' + type_,
                                           label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'dichroic mirror':
        optical_elements[i] = table.mirror(x=x, y=y, size=1, angle=minus_90_conv(angle), colour='orange', label=label + ' ' + type_,
                                           label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'dump':
        optical_elements[i] = table.beam_dump(x=x, y=y, size=0.4, angle=minus_90_conv(angle), colour='k', fillcolour='k', label=label+' '+type_,
                                              label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'water-cooled beam dump':
        optical_elements[i] = table.generic_circle(x=x, y=y, size=0.4, colour='blue', fill=False, fillcolour='k', label=label + ' ' + type_,
                                                   label_pos=label_position, labelpad=0.25, textcolour=label_color)
    elif type_ == 'iris':
        optical_elements[i] = table.box(x=x, y=y, size_x=0.1, size_y=0.5, angle=angle, linestyle='-.', standalone=True, label=label+' '+type_,
                                        label_pos=label_position, labelpad=0.4, textcolour=label_color)
    elif type_ == 'PBS':
        optical_elements[i] = table.beamsplitter_cube(x=x, y=y, size=0.3, angle=angle, direction='R', label=label+' '+type_,
                                                      label_pos=label_position, labelpad=0.25, textcolour=label_color)
    elif type_ == 'waveplate' or type_ == 'tall waveplate':
        optical_elements[i] = table.transmissive_plate(x=x, y=y, size=0.4, angle=minus_90_conv(angle), fill=True, fillcolour='c', label=label+' '+type_,
                                                       label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'lens' or type_ == 'convex rectangular lens':
        optical_elements[i] = table.convex_lens(x=x, y=y, size=0.5, angle=plus_90_conv(angle), label=label+' '+type_,
                                                label_pos=label_position, labelpad=0.07, textcolour=label_color)
    elif type_ == 'PD':
        optical_elements[i] = table.box(x=x, y=y, size_x=0.3, size_y=0.7, angle=angle, linestyle='--', standalone=True, label=label+' '+type_,
                                        label_pos=label_position, labelpad=0.4, textcolour=label_color)
    elif type_ == 'chamber port':
        optical_elements[i] = table.box(x=x, y=y, size_x=0.3, size_y=2, angle=angle, standalone=True, label=label+' '+type_,
                                        label_pos=label_position, labelpad=0.35, textcolour=label_color)
    elif type_ == 'post':
        optical_elements[i] = table.generic_circle(x=x, y=y, size=0.2, colour='k', fill=False, fillcolour='k', label=label+' '+type_,
                                        label_pos=label_position, labelpad=0.35, textcolour=label_color)
    else:
        if i > done:
            print(f"Skipping unknown element: {label + ' ' + type_}")


optical_elements[152] = table.box(x=x_conv(51), y=y_conv(61), size_x=0.3, size_y=0.5, angle=0, colour='c', standalone=True, label='O-152 double waveplate',
                                  label_pos=label_position, labelpad=0.4, textcolour=label_color)
optical_elements[153] = table.box(x=x_conv(49.5), y=y_conv(61), size_x=0.4, size_y=0.8, angle=180, colour='k', linestyle='-.', standalone=True, label='O-153 AOM',
                                  label_pos=label_position, labelpad=0.5, textcolour=label_color)
optical_elements[162] = table.box(x=x_conv(50), y=y_conv(66), size_x=0.3, size_y=4, angle=minus_90_conv(0), standalone=True, label='O-162 telescope lens tube',
                                   label_pos=label_position, labelpad=0.3, textcolour=label_color)
optical_elements[176] = table.mirror(x=x_conv(50), y=y_conv(21.5), size=0.4, angle=minus_90_conv(-45), label='O-176 50-50 beam splitter',
                                           label_pos='top', labelpad=0.1, textcolour=label_color)
optical_elements[212] = table.mirror(x=x_conv(21), y=y_conv(28), size=1, angle=minus_90_conv(45), colour='orange', label='O-212 dichroic mirror',
                                   label_pos=label_position, labelpad=0.1, textcolour=label_color)
optical_elements[217] = table.mirror(x=x_conv(29), y=y_conv(28), size=0.9, angle=minus_90_conv(140), label='O-217 mirror',
                                           label_pos=label_position, labelpad=0.1, textcolour=label_color)
optical_elements[230] = table.mirror(x=x_conv(28), y=y_conv(32), size=0.9, angle=minus_90_conv(-40), label='O-230 mirror',
                                           label_pos=label_position, labelpad=0.1, textcolour=label_color)
optical_elements[293] = table.beam_dump(x=x_conv(21), y=y_conv(21), size=0.6, angle=minus_90_conv(90), colour='k', fillcolour='k', label='O-293 dump',
                                      label_pos=label_position, labelpad=0.1, textcolour=label_color)
center = table.generic_circle(x=x_conv(33), y=y_conv(32), size=0.5, colour='gold', fill=True, fillcolour='gold', label='center',
                                        label_pos=label_position, labelpad=0.5, textcolour=label_color)

# Li_MOT_1_Path.append(optical_elements[228])
Li_MOT_1_Path.append(optical_elements[222])
Li_MOT_1_Path.append(optical_elements[221])
Li_MOT_1_Path.append(optical_elements[220])
Li_MOT_1_Path.append(optical_elements[256])
Li_MOT_1_Path.append(optical_elements[211])
Li_MOT_1_Path.append(optical_elements[210])
Li_MOT_1_Path.append(optical_elements[210])
Li_MOT_1_Path.append(optical_elements[215])
Li_MOT_1_Path.append(optical_elements[216])
Li_MOT_1_Path.append(optical_elements[212])
Li_MOT_1_Path.append(optical_elements[217])
Li_MOT_1_Path.append(optical_elements[230])
Li_MOT_1_Path.append(optical_elements[303])
Li_MOT_1.draw(table, Li_MOT_1_Path)

Li_MOT_2_Path.append(optical_elements[212])
Li_MOT_2_Path.append(optical_elements[293])
Li_MOT_2.draw(table, Li_MOT_2_Path)

# Cs_MOT_1_Path.append(optical_elements[228])
Cs_MOT_1_Path.append(optical_elements[219])
Cs_MOT_1_Path.append(optical_elements[218])
Cs_MOT_1_Path.append(optical_elements[199])
Cs_MOT_1_Path.append(optical_elements[198])
Cs_MOT_1_Path.append(optical_elements[197])
Cs_MOT_1_Path.append(optical_elements[196])
# Cs_MOT_1_Path.append(optical_elements[209])
Cs_MOT_1_Path.append(pyopt.OpticalElement(x_conv(14), y_conv(32), 't', angle=0, element_type='point_source'))
# Cs_MOT_1_Path.append(optical_elements[208])
# Cs_MOT_1_Path.append(optical_elements[206])
Cs_MOT_1_Path.append(pyopt.OpticalElement(x_conv(14), y_conv(28.05), 't', angle=0, element_type='point_source'))
# Cs_MOT_1_Path.append(optical_elements[207])
# Cs_MOT_1_Path.append(optical_elements[212])
# Cs_MOT_1_Path.append(optical_elements[217])
Cs_MOT_1_Path.append(pyopt.OpticalElement(x_conv(29.05), y_conv(28.05), 'r', angle=0, element_type='point_source'))
# Cs_MOT_1_Path.append(optical_elements[230])
Cs_MOT_1_Path.append(pyopt.OpticalElement(x_conv(28.05), y_conv(32.05), 'r', angle=0, element_type='point_source'))
# Cs_MOT_1_Path.append(optical_elements[300])
Cs_MOT_1_Path.append(pyopt.OpticalElement(x_conv(33), y_conv(32.05), 'r', angle=0, element_type='point_source'))
Cs_MOT_1.draw(table, Cs_MOT_1_Path)

# Cs_MOT_2_Path.append(optical_elements[212])
Cs_MOT_2_Path.append(pyopt.OpticalElement(x_conv(20.95), y_conv(28.05), 'r', angle=0, element_type='point_source'))
# Cs_MOT_2_Path.append(optical_elements[293])
Cs_MOT_2_Path.append(pyopt.OpticalElement(x_conv(20.95), y_conv(21), 't', angle=0, element_type='point_source'))
Cs_MOT_2.draw(table, Cs_MOT_2_Path)

# Li_Repump_1_Path.append(optical_elements[228])
# Li_Repump_1_Path.append(optical_elements[222])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(18.05), y_conv(48.65), 't', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[221])
# Li_Repump_1_Path.append(optical_elements[220])
# Li_Repump_1_Path.append(optical_elements[256])
# Li_Repump_1_Path.append(optical_elements[211])
# Li_Repump_1_Path.append(optical_elements[210])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(18.05), y_conv(34.95), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[215])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(21.05), y_conv(34.95), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[216])
# Li_Repump_1_Path.append(optical_elements[212])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(21.05), y_conv(27.95), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[217])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(28.95), y_conv(27.95), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[230])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(27.95), y_conv(31.95), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[300])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(33), y_conv(31.95), 'r', angle=0, element_type='point_source'))
Li_Repump_1.draw(table, Li_Repump_1_Path)

# Li_Repump_2_Path.append(optical_elements[212])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(21.05), y_conv(27.95), 't', angle=0, element_type='point_source'))
# Li_Repump_2_Path.append(optical_elements[293])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(21.05), y_conv(21), 't', angle=0, element_type='point_source'))
Li_Repump_2.draw(table, Li_Repump_2_Path)

# Cs_V_Imaging_1_Path.append(optical_elements[204])
# Cs_V_Imaging_1_Path.append(optical_elements[205])
# Cs_V_Imaging_1_Path.append(optical_elements[202])
Cs_V_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(14.1), y_conv(41.9), 'r', angle=0, element_type='point_source'))
# Cs_V_Imaging_1_Path.append(optical_elements[201])
# Cs_V_Imaging_1_Path.append(optical_elements[200])
# Cs_V_Imaging_1_Path.append(optical_elements[209])
# Cs_V_Imaging_1_Path.append(optical_elements[208])
# Cs_V_Imaging_1_Path.append(optical_elements[206])
Cs_V_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(14.1), y_conv(27.9), 'r', angle=0, element_type='point_source'))
# Cs_V_Imaging_1_Path.append(optical_elements[217])
Cs_V_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(28.9), y_conv(27.9), 'r', angle=0, element_type='point_source'))
# Cs_V_Imaging_1_Path.append(optical_elements[230])
Cs_V_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(27.9), y_conv(31.9), 'r', angle=0, element_type='point_source'))
# Cs_V_Imaging_1_Path.append(optical_elements[300])
Cs_V_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(33), y_conv(31.9), 'r', angle=0, element_type='point_source'))
Cs_V_Imaging_1.draw(table, Cs_V_Imaging_1_Path)

# Cs_V_Imaging_2_Path.append(optical_elements[212])
Cs_V_Imaging_2_Path.append(pyopt.OpticalElement(x_conv(21.1), y_conv(27.9), 't', angle=0, element_type='point_source'))
# Cs_V_Imaging_2_Path.append(optical_elements[293])
Cs_V_Imaging_2_Path.append(pyopt.OpticalElement(x_conv(21.1), y_conv(21), 't', angle=0, element_type='point_source'))
Cs_V_Imaging_2.draw(table, Cs_V_Imaging_2_Path)

Li_V_Imaging_1_Path.append(optical_elements[224])
Li_V_Imaging_1_Path.append(optical_elements[223])
Li_V_Imaging_1_Path.append(optical_elements[229])
# Li_V_Imaging_1_Path.append(optical_elements[212])
Li_V_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(20.9), y_conv(28.1), 'r', angle=0, element_type='point_source'))
# Li_V_Imaging_1_Path.append(optical_elements[217])
Li_V_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(29.1), y_conv(28.1), 'r', angle=0, element_type='point_source'))
# Li_V_Imaging_1_Path.append(optical_elements[230])
Li_V_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(28.1), y_conv(32.1), 'r', angle=0, element_type='point_source'))
# Li_V_Imaging_1_Path.append(optical_elements[300])
Li_V_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(33), y_conv(32.1), 'r', angle=0, element_type='point_source'))
Li_V_Imaging_1.draw(table, Li_V_Imaging_1_Path)

# Li_V_Imaging_2_Path.append(optical_elements[212])
Li_V_Imaging_2_Path.append(pyopt.OpticalElement(x_conv(20.9), y_conv(28.1), 't', angle=0, element_type='point_source'))
# Li_V_Imaging_2_Path.append(optical_elements[293])
Li_V_Imaging_2_Path.append(pyopt.OpticalElement(x_conv(20.9), y_conv(21), 't', angle=0, element_type='point_source'))
Li_V_Imaging_2.draw(table, Li_V_Imaging_2_Path)

Cs_V_Optical_Pump_3_Path.append(optical_elements[191])
Cs_V_Optical_Pump_3_Path.append(optical_elements[213])
# Cs_V_Optical_Pump_3_Path.append(optical_elements[214])
Cs_V_Optical_Pump_3_Path.append(pyopt.OpticalElement(x_conv(18), y_conv(27.85), 'r', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_3_Path.append(optical_elements[217])
Cs_V_Optical_Pump_3_Path.append(pyopt.OpticalElement(x_conv(28.85), y_conv(27.85), 'r', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_3_Path.append(optical_elements[230])
Cs_V_Optical_Pump_3_Path.append(pyopt.OpticalElement(x_conv(27.85), y_conv(31.85), 'r', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_3_Path.append(optical_elements[300])
Cs_V_Optical_Pump_3_Path.append(pyopt.OpticalElement(x_conv(33), y_conv(31.85), 'r', angle=0, element_type='point_source'))
Cs_V_Optical_Pump_3.draw(table, Cs_V_Optical_Pump_3_Path)

# Cs_V_Optical_Pump_4_Path.append(optical_elements[212])
Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(21.15), y_conv(27.85), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_4_Path.append(optical_elements[293])
Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(21.15), y_conv(21), 't', angle=0, element_type='point_source'))
Cs_V_Optical_Pump_4.draw(table, Cs_V_Optical_Pump_4_Path)

# RSC_3_Path.append(optical_elements[191])
RSC_3_Path.append(pyopt.OpticalElement(x_conv(6.05), y_conv(29.95), 'r', angle=0, element_type='point_source'))
# RSC_3_Path.append(optical_elements[213])
RSC_3_Path.append(pyopt.OpticalElement(x_conv(18.05), y_conv(29.95), 'r', angle=0, element_type='point_source'))
# RSC_3_Path.append(optical_elements[214])
RSC_3_Path.append(pyopt.OpticalElement(x_conv(18.05), y_conv(27.80), 'r', angle=0, element_type='point_source'))
# RSC_3_Path.append(optical_elements[217])
RSC_3_Path.append(pyopt.OpticalElement(x_conv(28.80), y_conv(27.80), 'r', angle=0, element_type='point_source'))
# RSC_3_Path.append(optical_elements[230])
RSC_3_Path.append(pyopt.OpticalElement(x_conv(27.80), y_conv(31.80), 'r', angle=0, element_type='point_source'))
# RSC_3_Path.append(optical_elements[300])
RSC_3_Path.append(pyopt.OpticalElement(x_conv(33), y_conv(31.80), 'r', angle=0, element_type='point_source'))
RSC_3.draw(table, RSC_3_Path)

# RSC_4_Path.append(optical_elements[212])
RSC_4_Path.append(pyopt.OpticalElement(x_conv(21.2), y_conv(27.8), 't', angle=0, element_type='point_source'))
# RSC_4_Path.append(optical_elements[293])
RSC_4_Path.append(pyopt.OpticalElement(x_conv(21.2), y_conv(21), 't', angle=0, element_type='point_source'))
RSC_4.draw(table, RSC_4_Path)

OTOP_1_Path.append(optical_elements[167])
OTOP_1_Path.append(optical_elements[160])
OTOP_1_Path.append(optical_elements[162])
OTOP_1_Path.append(optical_elements[163])
OTOP_1_Path.append(optical_elements[151])
OTOP_1_Path.append(optical_elements[151])
OTOP_1_Path.append(optical_elements[152])
OTOP_1_Path.append(optical_elements[153])
# OTOP_1_Path.append(optical_elements[154])
OTOP_1_Path.append(optical_elements[158])
OTOP_1_Path.append(optical_elements[273])
OTOP_1_Path.append(optical_elements[274])
OTOP_1.draw(table, OTOP_1_Path)

OTOP_2_Path.append(optical_elements[153])
# OTOP_2_Path.append(optical_elements[156])
OTOP_2_Path.append(pyopt.OpticalElement(x_conv(45.75), y_conv(61), 'r', angle=0, element_type='point_source'))
OTOP_2_Path.append(optical_elements[159])
OTOP_2_Path.append(optical_elements[155])
OTOP_2_Path.append(optical_elements[269])
OTOP_2_Path.append(optical_elements[270])
OTOP_2.draw(table, OTOP_2_Path)

OTOP_3_Path.append(optical_elements[167])
OTOP_3_Path.append(optical_elements[164])
OTOP_3_Path.append(optical_elements[268])
OTOP_3.draw(table, OTOP_3_Path)

OTOP_4_Path.append(optical_elements[165])
OTOP_4_Path.append(pyopt.OpticalElement(x_conv(50), y_conv(71), 't', angle=0, element_type='point_source'))
OTOP_4.draw(table, OTOP_4_Path)



file_path = "lower_opticaltable_optics.pdf"
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
