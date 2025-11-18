import pyopticaltable as pyopt
import matplotlib.pyplot as plt
import pandas as pd
import os


# Coordinate conversion functions
def x_conv(x):
    return x - 24

def y_conv(y):
    return y - 40

def minus_90_conv(angle_):
    return angle_ - 90

def plus_90_conv(angle_):
    return angle_ + 90


# Create the optical table
table = pyopt.OpticalTable(50, 82, size_factor=20, show_edge=True, show_grid=True, grid_spacing=1)
descaling_factor = 50/82

edge_width = 7

x1_1, x2_1, y1_1, y2_1 = table.angled_line(x=x_conv(13), y=y_conv(-0.5), size=27/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_1, x2_1], [y1_1, y2_1], color='blue', linewidth=edge_width)

x1_2, x2_2, y1_2, y2_2 = table.angled_line(x=x_conv(-0.5), y=y_conv(25), size=51/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_2, x2_2], [y1_2, y2_2], color='blue', linewidth=edge_width)

x1_3, x2_3, y1_3, y2_3 = table.angled_line(x=x_conv(26.5), y=y_conv(12.5), size=26/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_3, x2_3], [y1_3, y2_3], color='blue', linewidth=edge_width)

x1_4, x2_4, y1_4, y2_4 = table.angled_line(x=x_conv(23.5), y=y_conv(25.5), size=6/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_4, x2_4], [y1_4, y2_4], color='blue', linewidth=edge_width)

x1_5, x2_5, y1_5, y2_5 = table.angled_line(x=x_conv(20.5), y=y_conv(38), size=25/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_5, x2_5], [y1_5, y2_5], color='blue', linewidth=edge_width)

x1_6, x2_6, y1_6, y2_6 = table.angled_line(x=x_conv(10), y=y_conv(50.5), size=21/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_6, x2_6], [y1_6, y2_6], color='blue', linewidth=edge_width)

x1_7, x2_7, y1_7, y2_7 = table.angled_line(x=x_conv(38), y=y_conv(-0.5), size=21/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_7, x2_7], [y1_7, y2_7], color='purple', linewidth=edge_width)

x1_8, x2_8, y1_8, y2_8 = table.angled_line(x=x_conv(48.5), y=y_conv(40), size=81/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_8, x2_8], [y1_8, y2_8], color='purple', linewidth=edge_width)

x1_9, x2_9, y1_9, y2_9 = table.angled_line(x=x_conv(27.5), y=y_conv(25), size=51/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_9, x2_9], [y1_9, y2_9], color='purple', linewidth=edge_width)

x1_10, x2_10, y1_10, y2_10 = table.angled_line(x=x_conv(30.5), y=y_conv(50.5), size=6/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_10, x2_10], [y1_10, y2_10], color='purple', linewidth=edge_width)

x1_11, x2_11, y1_11, y2_11 = table.angled_line(x=x_conv(33.5), y=y_conv(58.5), size=16/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_11, x2_11], [y1_11, y2_11], color='purple', linewidth=edge_width)

x1_12, x2_12, y1_12, y2_12 = table.angled_line(x=x_conv(30.5), y=y_conv(66.5), size=6/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_12, x2_12], [y1_12, y2_12], color='purple', linewidth=edge_width)

x1_13, x2_13, y1_13, y2_13 = table.angled_line(x=x_conv(27.5), y=y_conv(73.5), size=14/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_13, x2_13], [y1_13, y2_13], color='purple', linewidth=edge_width)

x1_14, x2_14, y1_14, y2_14 = table.angled_line(x=x_conv(38), y=y_conv(80.5), size=21/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_14, x2_14], [y1_14, y2_14], color='purple', linewidth=edge_width)


x1_15, x2_15, y1_15, y2_15 = table.angled_line(x=x_conv(36), y=y_conv(40.5), size=24/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_15, x2_15], [y1_15, y2_15], color='red', linewidth=edge_width)

x1_16, x2_16, y1_16, y2_16 = table.angled_line(x=x_conv(12), y=y_conv(40.5), size=24/descaling_factor, angle=90, show=False, get_coords=True)
table.ax.plot([x1_16, x2_16], [y1_16, y2_16], color='red', linewidth=edge_width)

x1_17, x2_17, y1_17, y2_17 = table.angled_line(x=x_conv(24), y=y_conv(28.5), size=24/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_17, x2_17], [y1_17, y2_17], color='red', linewidth=edge_width)

x1_18, x2_18, y1_18, y2_18 = table.angled_line(x=x_conv(24), y=y_conv(52.5), size=24/descaling_factor, angle=0, show=False, get_coords=True)
table.ax.plot([x1_18, x2_18], [y1_18, y2_18], color='red', linewidth=edge_width)


df = pd.read_csv('OpticsSetupBreadboard_v3.csv')

x_displacement = 0
y_displacement = 0
x_displacement_2 = 0
y_displacement_2 = 0
x_displacement_3 = 0
y_displacement_3 = 0


label_position = 'top'
label_color = 'dodgerblue'
optical_elements = {}


# Define laser beams

fiber_launcher_size_x = 1.55
fiber_launcher_size_y = 2
laser_label_font_size = 17

Li_H_Imaging_1 = pyopt.LaserBeam(colour='magenta', width=2, style='-')
Li_H_Imaging_1_Path = []
Li_H_Imaging_2 = pyopt.LaserBeam(colour='magenta', width=2, style='-')
Li_H_Imaging_2_Path = []
optical_elements[37] = table.box_source(x=x_conv(4.5 + x_displacement_3), y=y_conv(17.5 + y_displacement_3), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=-45, output_side='right', label='O-37 Li H Imaging', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
Li_H_Imaging_1_Path.append(optical_elements[37])

Li_EOM_1 = pyopt.LaserBeam(colour='magenta', width=2, style='-')
Li_EOM_1_Path = []
Li_EOM_2 = pyopt.LaserBeam(colour='magenta', width=2, style='-')
Li_EOM_2_Path = []
optical_elements[27] = table.box_source(x=x_conv(4 + x_displacement_3), y=y_conv(14 + y_displacement_3), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=45, output_side='right', label='O-27 Li EOM', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
Li_EOM_1_Path.append(optical_elements[27])

Li_Repump_1 = pyopt.LaserBeam(colour='lime', width=2, style='-')
Li_Repump_1_Path = []
Li_Repump_2 = pyopt.LaserBeam(colour='lime', width=2, style='-')
Li_Repump_2_Path = []
Li_Repump_3 = pyopt.LaserBeam(colour='lime', width=2, style='-')
Li_Repump_3_Path = []
Li_Repump_4 = pyopt.LaserBeam(colour='lime', width=2, style='-')
Li_Repump_4_Path = []
optical_elements[15] = table.box_source(x=x_conv(12 + x_displacement_3), y=y_conv(12 + y_displacement_3), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=45, output_side='right', label='O-15 Li Repump', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
Li_Repump_1_Path.append(optical_elements[15])

Li_MOT_1 = pyopt.LaserBeam(colour='purple', width=2, style='-')
Li_MOT_1_Path = []
Li_MOT_2 = pyopt.LaserBeam(colour='purple', width=2, style='-')
Li_MOT_2_Path = []
Li_MOT_3 = pyopt.LaserBeam(colour='purple', width=2, style='-')
Li_MOT_3_Path = []
Li_MOT_4 = pyopt.LaserBeam(colour='purple', width=2, style='-')
Li_MOT_4_Path = []
optical_elements[16] = table.box_source(x=x_conv(9.5 + x_displacement_3), y=y_conv(11.5 + x_displacement_3), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=45, output_side='right', label='O-16 Li MOT', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
Li_MOT_1_Path.append(optical_elements[16])

Cs_MOT_1 = pyopt.LaserBeam(colour='green', width=2, style='-')
Cs_MOT_1_Path = []
Cs_MOT_2 = pyopt.LaserBeam(colour='green', width=2, style='-')
Cs_MOT_2_Path = []
Cs_MOT_3 = pyopt.LaserBeam(colour='green', width=2, style='-')
Cs_MOT_3_Path = []
Cs_MOT_4 = pyopt.LaserBeam(colour='green', width=2, style='-')
Cs_MOT_4_Path = []
optical_elements[17] = table.box_source(x=x_conv(7 + x_displacement_3), y=y_conv(11 + y_displacement_3), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=45, output_side='right', label='O-17 Cs MOT', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
Cs_MOT_1_Path.append(optical_elements[17])

Cs_H_Imaging_1 = pyopt.LaserBeam(colour='cyan', width=2, style='-')
Cs_H_Imaging_1_Path = []
Cs_H_Imaging_2 = pyopt.LaserBeam(colour='cyan', width=2, style='-')
Cs_H_Imaging_2_Path = []
optical_elements[12] = table.box_source(x=x_conv(4 + x_displacement_3), y=y_conv(20 + y_displacement_3), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=-45, output_side='right', label='O-12 Cs H Imaging', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
Cs_H_Imaging_1_Path.append(optical_elements[12])

Li_Zeeman = pyopt.LaserBeam(colour='red', width=2, style='-')  # Transmitted beam
Li_Zeeman_Path = []
optical_elements[25] = table.box_source(x=x_conv(21 + x_displacement_3), y=y_conv(2 + y_displacement_3), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=0, output_side='right', label='O-25 Li Zeeman', label_pos=label_position, labelpad=1, textcolour=label_color, fontsize=laser_label_font_size)
Li_Zeeman_Path.append(optical_elements[25])

Cs_Zeeman = pyopt.LaserBeam(colour='blue', width=2, style='-')
Cs_Zeeman_Path = []
optical_elements[48] = table.box_source(x=x_conv(17 + x_displacement_3), y=y_conv(4 + y_displacement_3), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=0, output_side='right', label='O-48 Cs Zeeman', label_pos=label_position, labelpad=1, textcolour=label_color, fontsize=laser_label_font_size)
Cs_Zeeman_Path.append(optical_elements[48])

RSC_1 = pyopt.LaserBeam(colour='coral', width=2, style='-')
RSC_1_Path = []
RSC_2 = pyopt.LaserBeam(colour='coral', width=2, style='-')
RSC_2_Path = []
RSC_3 = pyopt.LaserBeam(colour='coral', width=2, style='-')
RSC_3_Path = []
RSC_4 = pyopt.LaserBeam(colour='coral', width=2, style='-')
RSC_4_Path = []
optical_elements[110] = table.box_source(x=x_conv(14 + x_displacement), y=y_conv(10 + y_displacement), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=45, output_side='right', label='O-110 RSC', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
RSC_1_Path.append(optical_elements[110])

Cs_V_Optical_Pump_1 = pyopt.LaserBeam(colour='navy', width=2, style='-')
Cs_V_Optical_Pump_1_Path = []
Cs_V_Optical_Pump_2 = pyopt.LaserBeam(colour='navy', width=2, style='-')
Cs_V_Optical_Pump_2_Path = []
Cs_V_Optical_Pump_3 = pyopt.LaserBeam(colour='navy', width=2, style='-')
Cs_V_Optical_Pump_3_Path = []
Cs_V_Optical_Pump_4 = pyopt.LaserBeam(colour='navy', width=2, style='-')
Cs_V_Optical_Pump_4_Path = []
optical_elements[116] = table.box_source(x=x_conv(11.5 + x_displacement), y=y_conv(9.5 + y_displacement), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=45, output_side='right', label='O-116 Cs V Optical Pump', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
Cs_V_Optical_Pump_1_Path.append(optical_elements[116])

Cs_H_Optical_Pump = pyopt.LaserBeam(colour='hotpink', width=2, style='-')
Cs_H_Optical_Pump_Path = []
optical_elements[127] = table.box_source(x=x_conv(36 + x_displacement), y=y_conv(17 + y_displacement), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=90, output_side='right', label='O-127 Cs H Optical Pump', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
Cs_H_Optical_Pump_Path.append(optical_elements[127])

OTOP_1 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_1_Path = []
OTOP_2 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_2_Path = []
OTOP_3 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_3_Path = []
OTOP_4 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_4_Path = []
OTOP_5 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_5_Path = []
OTOP_6 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_6_Path = []
OTOP_7 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_7_Path = []
OTOP_8 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_8_Path = []
OTOP_9 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_9_Path = []
OTOP_10 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_10_Path = []
optical_elements[267] = table.box_source(x=x_conv(32 + x_displacement_2), y=y_conv(76 + y_displacement_2), size_x=6, size_y=3.5, angle=0, output_side='right', label='O-267 OTOP', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
OTOP_1_Path.append(optical_elements[267])

Dual_Color_1 = pyopt.LaserBeam(colour='violet', width=3, style='-')
Dual_Color_1_Path = []
Dual_Color_2 = pyopt.LaserBeam(colour='violet', width=3, style='-')
Dual_Color_2_Path = []
Dual_Color_3 = pyopt.LaserBeam(colour='violet', width=3, style='-')
Dual_Color_3_Path = []
optical_elements[148] = table.box_source(x=x_conv(36 + x_displacement), y=y_conv(55 + y_displacement), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=0, output_side='right', label='O-148 Dual Color', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
Dual_Color_1_Path.append(optical_elements[148])

BFL_1 = pyopt.LaserBeam(colour='cornflowerblue', width=2, style='-')
BFL_1_Path = []
BFL_2 = pyopt.LaserBeam(colour='cornflowerblue', width=2, style='-')
BFL_2_Path = []
optical_elements[150] = table.box_source(x=x_conv(47 + x_displacement), y=y_conv(79 + y_displacement), size_x=fiber_launcher_size_x, size_y=fiber_launcher_size_y, angle=-90, output_side='right', label='O-150 BFL', label_pos=label_position, labelpad=0.7, textcolour=label_color, fontsize=laser_label_font_size)
BFL_1_Path.append(optical_elements[150])


for _, row in df.iterrows():

    limit = 340
    done = 148

    label = str(row['Label']).strip()
    i = float(label.split('-')[1])

    if i == limit:
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
        optical_elements[i] = table.mirror(x=x, y=y, size=1 / descaling_factor, angle=minus_90_conv(angle),
                                           label=label+' '+type_, label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'large mirror':
        optical_elements[i] = table.mirror(x=x, y=y, size=2 / descaling_factor, angle=minus_90_conv(angle),
                                           label=label + ' ' + type_, label_pos=label_position, labelpad=0,
                                           textcolour=label_color)
    elif type_ == 'beam sampler':
        optical_elements[i] = table.mirror(x=x, y=y, size=1 / descaling_factor, angle=minus_90_conv(angle), colour='teal',
                                           label=label + ' ' + type_, label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'quadrant mirror' or type_ == 'small mirror':
        optical_elements[i] = table.mirror(x=x, y=y, size=0.4/descaling_factor, angle=minus_90_conv(angle),
                                           label=label+' '+type_, label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'dichroic mirror':
        optical_elements[i] = table.mirror(x=x, y=y, size=2/descaling_factor, angle=minus_90_conv(angle), colour='orange',
                                           label=label + ' ' + type_, label_pos=label_position, labelpad=0, textcolour=label_color)
    elif type_ == 'small dichroic mirror':
        optical_elements[i] = table.mirror(x=x, y=y, size=0.5 / descaling_factor, angle=minus_90_conv(angle),
                                           colour='orange',
                                           label=label + ' ' + type_, label_pos=label_position, labelpad=0,
                                           textcolour=label_color)
    elif type_ == 'dump':
        optical_elements[i] = table.beam_dump(x=x, y=y, size=0.6/descaling_factor, angle=minus_90_conv(angle), colour='k', fillcolour='k',
                                              label=label+' '+type_, label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'water-cooled beam dump':
        optical_elements[i] = table.generic_circle(x=x, y=y, size=0.5, colour='blue', fill=False, fillcolour='k',
                                                   label=label + ' ' + type_, label_pos=label_position, labelpad=0.3, textcolour=label_color)
    elif type_ == 'iris':
        optical_elements[i] = table.box(x=x, y=y, size_x=0.1, size_y=1, angle=angle, linestyle='-.', standalone=True,
                                        label=label+' '+type_, label_pos=label_position, labelpad=0.6, textcolour=label_color)
    elif type_ == 'PBS':
        optical_elements[i] = table.beamsplitter_cube(x=x, y=y, size=0.7/descaling_factor, angle=angle, direction='R',
                                                      label=label+' '+type_, label_pos=label_position, labelpad=0.2, textcolour=label_color)
    elif type_ == 'large PBS':
        optical_elements[i] = table.beamsplitter_cube(x=x, y=y, size=1 / descaling_factor, angle=angle, direction='R',
                                                      label=label + ' ' + type_, label_pos=label_position, labelpad=0.2,
                                                      textcolour=label_color)
    elif type_ == 'waveplate' or type_ == 'tall waveplate':
        optical_elements[i] = table.transmissive_plate(x=x, y=y, size=0.7/descaling_factor, angle=minus_90_conv(angle), fill=True, fillcolour='c',
                                                       label=label+' '+type_, label_pos=label_position, labelpad=0.05, textcolour=label_color)
    elif type_ == 'double waveplate':
        optical_elements[i] = table.box(x=x, y=y, size_x=1.5,
                                          size_y=1.5, angle=angle, colour='c', standalone=True,
                                          label=label+' '+type_,
                                          label_pos=label_position, labelpad=0.4, textcolour=label_color)
    elif type_ == 'lens':
        optical_elements[i] = table.convex_lens(x=x, y=y, size=1/descaling_factor, angle=plus_90_conv(angle),
                                                label=label+' '+type_, label_pos=label_position, labelpad=0, textcolour=label_color)
    elif type_ == 'PD':
        optical_elements[i] = table.box(x=x, y=y, size_x=1, size_y=2, angle=angle, linestyle='--', standalone=True,
                                        label=label+' '+type_, label_pos=label_position, labelpad=0.8, textcolour=label_color)
    elif type_ == 'small PD':
        optical_elements[i] = table.box(x=x, y=y, size_x=1, size_y=1, angle=angle, linestyle='--', standalone=True,
                                        label=label + ' ' + type_, label_pos=label_position, labelpad=0.8, textcolour=label_color)
    elif type_ == 'chamber port':
        optical_elements[i] = table.box(x=x, y=y, size_x=0.3, size_y=2, angle=angle, standalone=True,
                                        label=label+' '+type_, label_pos=label_position, labelpad=0.35, textcolour=label_color)
    elif type_ == 'post':
        optical_elements[i] = table.generic_circle(x=x, y=y, size=0.5, colour='k', fill=False, fillcolour='k',
                                                   label=label+' '+type_, label_pos=label_position, labelpad=0.35, textcolour=label_color)
    elif type_ == 'large post':
        optical_elements[i] = table.generic_circle(x=x, y=y, size=0.75, colour='k', fill=False, fillcolour='k',
                                                   label=label + ' ' + type_, label_pos=label_position, labelpad=0.35,
                                                   textcolour=label_color)
        optical_elements[i+0.1] = table.generic_circle(x=x, y=y, size=1.25, colour='k', fill=False, fillcolour='k',
                                                   label=label + ' ' + type_ + 'base', label_pos=label_position, labelpad=0.5,
                                                   textcolour=label_color)
    elif type_ == 'AOM':
        optical_elements[i] = table.box(x=x, y=y, size_x=1, size_y=2, angle=angle, colour='k', linestyle='-.', standalone=True,
                                        label=label+' '+type_, label_pos=label_position, labelpad=0.6, textcolour=label_color)
    elif type_ == '50-50 beam splitter':
        optical_elements[i] = table.mirror(x=x, y=y, size=0.5 / descaling_factor, angle=minus_90_conv(angle),
                                        label=label+' '+type_, label_pos='top', labelpad=0.1, textcolour=label_color)
    elif type_ == 'camera':
        optical_elements[i] = table.box(x=x, y=y, size_x=1, size_y=2, angle=angle, linestyle='-.', standalone=True,
                                        label=label+' '+type_, label_pos=label_position, labelpad=0.6, textcolour=label_color)
    else:
        if i > done:
            print(f"Skipping unknown element: {label + ' ' + type_}")

optical_elements[31] = table.box(x=x_conv(47 + x_displacement), y=y_conv(51 + y_displacement), size_x=1, size_y=1.5, angle=minus_90_conv(90), standalone=True,
                                 label='O-31 lens tube', label_pos='right', labelpad=0.3, textcolour=label_color)
optical_elements[36] = table.box(x=x_conv(47 + x_displacement), y=y_conv(52 + y_displacement), size_x=1.5, size_y=0.1, angle=minus_90_conv(90), colour='orange', standalone=True,
                                 label='O-36 copper plate', label_pos='top', labelpad=0.2, textcolour=label_color)
optical_elements[73] = table.box(x=x_conv(47 + x_displacement), y=y_conv(59 + y_displacement), size_x=1, size_y=9, angle=minus_90_conv(90), standalone=True,
                                 label='O-73 lens tube',label_pos='right', labelpad=0.5, textcolour=label_color)
optical_elements[103] = table.box(x=x_conv(12 + x_displacement), y=y_conv(40.5 + y_displacement), size_x=1, size_y=2, angle=minus_90_conv(160), standalone=True, label='O-103 quadrant detector sensor head',
                                  label_pos=label_position, labelpad=0.5, textcolour=label_color)
optical_elements[134] = table.box(x=x_conv(44.5 + x_displacement), y=y_conv(35.4 + y_displacement), size_x=1, size_y=0.1, angle=minus_90_conv(-135), colour='b', standalone=True, label='O-134 flat PBS',
                                           label_pos=label_position, labelpad=0.4, textcolour=label_color)
optical_elements[137] = table.box(x=x_conv(32 + x_displacement), y=y_conv(36 + y_displacement), size_x=3.5, size_y=2, angle=0, standalone=True, label='O-137 3-hole tube',
                                        label_pos=label_position, labelpad=0.25, textcolour=label_color)
three_hole_tube_lens = table.convex_lens(x=x_conv(31 + x_displacement), y=y_conv(36 + y_displacement), size=2/descaling_factor, angle=plus_90_conv(0), label='',
                                                label_pos=label_position, labelpad=0.07, textcolour=label_color)
optical_elements[138] = table.box(x=x_conv(47 + x_displacement), y=y_conv(73.75 + y_displacement), size_x=1, size_y=8, angle=minus_90_conv(90), standalone=True, label='O-138 lens tube',
                                 label_pos='right', labelpad=0.5, textcolour=label_color)
optical_elements[140] = table.convex_lens(x=x_conv(41 + x_displacement), y=y_conv(43 + y_displacement), size=0.75 / descaling_factor, angle=plus_90_conv(90),
                                        label='O-140 convex rectangular lens', label_pos=label_position, labelpad=0,
                                        textcolour=label_color)
optical_elements[143] = table.box(x=x_conv(45 + x_displacement), y=y_conv(43 + y_displacement), size_x=1, size_y=2, angle=minus_90_conv(90), standalone=True, label='O-143 lens tube',
                                 label_pos='right', labelpad=0.5, textcolour=label_color)
optical_elements[146] = table.convex_lens(x=x_conv(41 + x_displacement), y=y_conv(46 + y_displacement), size=1.5 / descaling_factor, angle=plus_90_conv(-90),
                                        label='O-146 convex rectangular lens', label_pos=label_position, labelpad=0,
                                        textcolour=label_color)
optical_elements[162] = table.box(x=x_conv(41.5 + x_displacement_2), y=y_conv(76 + y_displacement_2), size_x=1, size_y=5.5, angle=minus_90_conv(0), standalone=True, label='O-162 telescope lens tube',
                                   label_pos=label_position, labelpad=0.3, textcolour=label_color)
optical_elements[251] = table.box(x=x_conv(30 + x_displacement), y=y_conv(42 + y_displacement), size_x=0.7, size_y=6, angle=minus_90_conv(-135), standalone=True, label='O-251 waveplate & polarizer in front of camera',
                                 label_pos=label_position, labelpad=0.3, textcolour=label_color)
black_aluminum_dump_1 = table.beam_dump(x=x_conv(1 + x_displacement), y=y_conv(26 + y_displacement), size=0.5/descaling_factor, angle=minus_90_conv(90), colour='k', fillcolour='k', label='black aluminum dump',
                                              label_pos=label_position, labelpad=0.1, textcolour=label_color)
center = table.generic_circle(x=x_conv(24 + x_displacement), y=y_conv(36 + y_displacement), size=0.5, colour='gold', fill=True, fillcolour='gold', label='center',
                                        label_pos=label_position, labelpad=0.3, textcolour=label_color)
lower_hole = table.generic_circle(x=x_conv(2), y=y_conv(7), size=0.5, colour='red', fill=False, fillcolour='k', label='hole',
                                        label_pos='top', labelpad=0.35, textcolour=label_color)
upper_hole = table.generic_circle(x=x_conv(2), y=y_conv(43), size=0.5, colour='red', fill=False, fillcolour='k', label='hole',
                                        label_pos='top', labelpad=0.35, textcolour=label_color)
empty_mount_1 = table.generic_circle(x=x_conv(12), y=y_conv(20), size=0.4, colour='k', fill=False, fillcolour='k', label='empty mount',
                                        label_pos='top', labelpad=0.35, textcolour=label_color)
empty_mount_2 = table.generic_circle(x=x_conv(13), y=y_conv(19), size=0.4, colour='k', fill=False, fillcolour='k', label='empty mount',
                                        label_pos='top', labelpad=0.35, textcolour=label_color)
empty_mount_3 = table.generic_circle(x=x_conv(14), y=y_conv(18), size=0.4, colour='k', fill=False, fillcolour='k', label='empty mount',
                                        label_pos='top', labelpad=0.35, textcolour=label_color)
empty_mount_4 = table.generic_circle(x=x_conv(15), y=y_conv(17), size=0.4, colour='k', fill=False, fillcolour='k', label='empty mount',
                                        label_pos='top', labelpad=0.35, textcolour=label_color)

ion_pump_pipe = table.generic_circle(x=x_conv(24), y=y_conv(28.5), size=2, colour='k', fill=False, fillcolour='k', label='ion pump pipe',
                                        label_pos='top', labelpad=0.35, textcolour=label_color)


Li_H_Imaging_1_Path.append(optical_elements[6])
# Li_H_Imaging_1_Path.append(optical_elements[76.3])
Li_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(16 - 0.05 + x_displacement_3), y_conv(22 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_H_Imaging_1_Path.append(optical_elements[60])
Li_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(13 + x_displacement_3), y_conv(25 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_H_Imaging_1_Path.append(optical_elements[251])
Li_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(30 + 2 + x_displacement_3), y_conv(42 + 2 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Li_H_Imaging_1.draw(table, Li_H_Imaging_1_Path)

Li_H_Imaging_2_Path.append(optical_elements[305])
Li_H_Imaging_2_Path.append(optical_elements[30])
Li_H_Imaging_2_Path.append(optical_elements[325])
Li_H_Imaging_2.draw(table, Li_H_Imaging_2_Path)

Li_EOM_1_Path.append(optical_elements[38])
# Li_EOM_1_Path.append(optical_elements[50])
Li_EOM_1_Path.append(pyopt.OpticalElement(x_conv(9.9 - 0.1 + x_displacement_3), y_conv(15.63 + 0.02 + y_displacement_3), 't', angle=0, element_type='point_source'))
# Li_EOM_1_Path.append(optical_elements[76.3])
Li_EOM_1_Path.append(pyopt.OpticalElement(x_conv(16 - 0.05 + x_displacement_3), y_conv(22 - 0.15 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_EOM_1_Path.append(optical_elements[60])
Li_EOM_1_Path.append(pyopt.OpticalElement(x_conv(13 + x_displacement_3), y_conv(25 - 0.2 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_EOM_1_Path.append(optical_elements[251])
Li_EOM_1_Path.append(pyopt.OpticalElement(x_conv(30 + 2 + x_displacement_3), y_conv(42 + 2 - 0.2 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Li_EOM_1.draw(table, Li_EOM_1_Path)

# Li_EOM_2_Path.append(optical_elements[305])
Li_EOM_2_Path.append(pyopt.OpticalElement(x_conv(12 + x_displacement_3), y_conv(18 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_EOM_2_Path.append(optical_elements[30])
Li_EOM_2_Path.append(pyopt.OpticalElement(x_conv(8.5 - 0.1 + x_displacement_3), y_conv(21.5 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_EOM_2_Path.append(optical_elements[325])
Li_EOM_2_Path.append(pyopt.OpticalElement(x_conv(7 - 0.05 + x_displacement_3), y_conv(20 + 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Li_EOM_2.draw(table, Li_EOM_2_Path)

Li_Repump_1_Path.append(optical_elements[307])
# Li_Repump_1_Path.append(optical_elements[63])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(15 - 0.05 + x_displacement_3), y_conv(15 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[40])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(14 + x_displacement_3), y_conv(16 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[185])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(19.8 + 0.05 + x_displacement_3), y_conv(21.8 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[13])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(19.6 + 0.2 + 0.05 + x_displacement), y_conv(7 + 0.2 + 0.05 + y_displacement), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[250])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(2 + x_displacement), y_conv(7 + 0.05 + y_displacement), 'r', angle=0, element_type='point_source'))
Li_Repump_1.draw(table, Li_Repump_1_Path)

# Li_Repump_2_Path.append(optical_elements[78.2])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(18 + x_displacement_3), y_conv(20 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_2_Path.append(optical_elements[76.3])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(16 + x_displacement_3), y_conv(22 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_2_Path.append(optical_elements[91])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(19 + 0.05 + x_displacement_3), y_conv(25 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_2_Path.append(optical_elements[87])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(29 + 0.05 + x_displacement_3), y_conv(15 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_2_Path.append(optical_elements[107])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(37 + x_displacement_3), y_conv(23 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_2_Path.append(optical_elements[70])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(14 + x_displacement_3), y_conv(46 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Li_Repump_2.draw(table, Li_Repump_2_Path)

# Li_Repump_3_Path.append(optical_elements[76.3])
Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(16 + x_displacement_3), y_conv(22 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_3_Path.append(optical_elements[60])
Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(13 + x_displacement_3), y_conv(25 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_3_Path.append(optical_elements[251])
Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(30 + 2 + x_displacement_3), y_conv(42 + 2 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Li_Repump_3.draw(table, Li_Repump_3_Path)

Li_Repump_4_Path.append(optical_elements[307])
Li_Repump_4_Path.append(optical_elements[90])
Li_Repump_4_Path.append(optical_elements[84])
Li_Repump_4.draw(table, Li_Repump_4_Path)


Li_MOT_1_Path.append(optical_elements[320])
Li_MOT_1_Path.append(optical_elements[40])
# Li_MOT_1_Path.append(optical_elements[78.1])
Li_MOT_1_Path.append(optical_elements[78.2])
# Li_MOT_1_Path.append(optical_elements[78.3])
Li_MOT_1_Path.append(optical_elements[185])
# Li_MOT_1_Path.append(optical_elements[13])
Li_MOT_1_Path.append(pyopt.OpticalElement(x_conv(19.6 + 0.2 + x_displacement), y_conv(7 + 0.2 + y_displacement), 'r', angle=0, element_type='point_source'))
Li_MOT_1_Path.append(optical_elements[250])
Li_MOT_1.draw(table, Li_MOT_1_Path)

Li_MOT_2_Path.append(optical_elements[320])
Li_MOT_2_Path.append(optical_elements[105])
Li_MOT_2_Path.append(optical_elements[313])
Li_MOT_2.draw(table, Li_MOT_2_Path)

Li_MOT_3_Path.append(optical_elements[78.2])
# Li_MOT_3_Path.append(optical_elements[65])
Li_MOT_3_Path.append(optical_elements[76.3])
# Li_MOT_3_Path.append(optical_elements[76.2])
# Li_MOT_3_Path.append(optical_elements[76.1])
# Li_MOT_3_Path.append(optical_elements[83])
Li_MOT_3_Path.append(optical_elements[91])
# Li_MOT_3_Path.append(optical_elements[186])
# Li_MOT_3_Path.append(optical_elements[106])
Li_MOT_3_Path.append(optical_elements[87])
Li_MOT_3_Path.append(optical_elements[107])
Li_MOT_3_Path.append(optical_elements[69])
Li_MOT_3_Path.append(optical_elements[70])
Li_MOT_3.draw(table, Li_MOT_3_Path)

Li_MOT_4_Path.append(optical_elements[76.3])
Li_MOT_4_Path.append(optical_elements[60])
Li_MOT_4_Path.append(optical_elements[251])
Li_MOT_4.draw(table, Li_MOT_4_Path)

Cs_MOT_1_Path.append(optical_elements[98])
# Cs_MOT_1_Path.append(optical_elements[13])
Cs_MOT_1_Path.append(pyopt.OpticalElement(x_conv(19.6 - 0.1 + x_displacement_3), y_conv(7 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Cs_MOT_1_Path.append(optical_elements[250])
Cs_MOT_1.draw(table, Cs_MOT_1_Path)

Cs_MOT_2_Path.append(optical_elements[79.1])
Cs_MOT_2_Path.append(optical_elements[34])
# Cs_MOT_2_Path.append(optical_elements[251])
Cs_MOT_2_Path.append(pyopt.OpticalElement(x_conv(30 - 0.05 + x_displacement_3), y_conv(42 + 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Cs_MOT_2.draw(table, Cs_MOT_2_Path)

Cs_MOT_3_Path.append(optical_elements[64.1])
Cs_MOT_3_Path.append(optical_elements[93])
# Cs_MOT_3_Path.append(optical_elements[87])
Cs_MOT_3_Path.append(pyopt.OpticalElement(x_conv(29 + 0.1 + x_displacement_3), y_conv(15 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Cs_MOT_3_Path.append(optical_elements[107])
Cs_MOT_3_Path.append(pyopt.OpticalElement(x_conv(37 + x_displacement_3), y_conv(23 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Cs_MOT_3_Path.append(optical_elements[70])
Cs_MOT_3_Path.append(pyopt.OpticalElement(x_conv(14 + x_displacement_3), y_conv(46 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Cs_MOT_3.draw(table, Cs_MOT_3_Path)

Cs_MOT_4_Path.append(optical_elements[306])
Cs_MOT_4_Path.append(optical_elements[104])
Cs_MOT_4_Path.append(optical_elements[315])
Cs_MOT_4.draw(table, Cs_MOT_4_Path)

Cs_H_Imaging_1_Path.append(optical_elements[4])
# Cs_H_Imaging_1_Path.append(optical_elements[64.1])
Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(13 + x_displacement_3), y_conv(21 - 0.05 + y_displacement_3), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_1_Path.append(optical_elements[34])
Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(10.95 + x_displacement_3), y_conv(23.05 - 0.05 + y_displacement_3), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_1_Path.append(optical_elements[251])
Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(30 + 2 - 0.05 + x_displacement_3), y_conv(42 + 2 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Cs_H_Imaging_1.draw(table, Cs_H_Imaging_1_Path)

Cs_H_Imaging_2_Path.append(optical_elements[304])
Cs_H_Imaging_2_Path.append(optical_elements[82])
Cs_H_Imaging_2_Path.append(optical_elements[314])
Cs_H_Imaging_2.draw(table, Cs_H_Imaging_2_Path)

# Li_Zeeman_Path.append(optical_elements[21])
Li_Zeeman_Path.append(optical_elements[23])
# Li_Zeeman_Path.append(optical_elements[328])
# Li_Zeeman_Path.append(optical_elements[24])
Li_Zeeman_Path.append(optical_elements[2])
Li_Zeeman_Path.append(optical_elements[22])
Li_Zeeman_Path.append(optical_elements[20])
Li_Zeeman_Path.append(optical_elements[19])
# Li_Zeeman_Path.append(optical_elements[58])
Li_Zeeman_Path.append(pyopt.OpticalElement(x_conv(24 + 0.1 + x_displacement_3), y_conv(16 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Li_Zeeman_Path.append(pyopt.OpticalElement(x_conv(24 + 0.1 + x_displacement_3), y_conv(45 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Li_Zeeman.draw(table, Li_Zeeman_Path)

# Cs_Zeeman_Path.append(optical_elements[44])
Cs_Zeeman_Path.append(optical_elements[47])
# Cs_Zeeman_Path.append(optical_elements[327])
# Cs_Zeeman_Path.append(optical_elements[45])
Cs_Zeeman_Path.append(optical_elements[3])
Cs_Zeeman_Path.append(optical_elements[46])
Cs_Zeeman_Path.append(optical_elements[43])
Cs_Zeeman_Path.append(optical_elements[67])
Cs_Zeeman_Path.append(optical_elements[35])
Cs_Zeeman_Path.append(optical_elements[58])
Cs_Zeeman_Path.append(pyopt.OpticalElement(x_conv(24 + x_displacement_3), y_conv(45 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Cs_Zeeman.draw(table, Cs_Zeeman_Path)

RSC_1_Path.append(optical_elements[95])
RSC_1_Path.append(optical_elements[149])
RSC_1_Path.append(optical_elements[120])
RSC_1_Path.append(optical_elements[5])
RSC_1.draw(table, RSC_1_Path)

RSC_2_Path.append(optical_elements[298])
RSC_2_Path.append(optical_elements[121])
RSC_2_Path.append(optical_elements[288])
RSC_2.draw(table, RSC_2_Path)

RSC_3_Path.append(optical_elements[114.1])
RSC_3_Path.append(optical_elements[99])
RSC_3_Path.append(optical_elements[109])
RSC_3_Path.append(optical_elements[188])
RSC_3_Path.append(optical_elements[250])
RSC_3.draw(table, RSC_3_Path)

RSC_4_Path.append(optical_elements[322])
RSC_4_Path.append(optical_elements[308])
RSC_4_Path.append(optical_elements[323])
RSC_4.draw(table, RSC_4_Path)

Cs_V_Optical_Pump_1_Path.append(optical_elements[119])
# Cs_V_Optical_Pump_1_Path.append(optical_elements[114.1])
Cs_V_Optical_Pump_1_Path.append(pyopt.OpticalElement(x_conv(21.3 - 0.05 + x_displacement), y_conv(17.3 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_1_Path.append(optical_elements[298])
Cs_V_Optical_Pump_1_Path.append(pyopt.OpticalElement(x_conv(22.5 + x_displacement), y_conv(18.5 + 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_1_Path.append(optical_elements[121])
Cs_V_Optical_Pump_1_Path.append(pyopt.OpticalElement(x_conv(15.5 + x_displacement), y_conv(25.5 + 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_1_Path.append(optical_elements[288])
Cs_V_Optical_Pump_1_Path.append(pyopt.OpticalElement(x_conv(31 - 0.05 + x_displacement), y_conv(45 + y_displacement), 't', angle=0, element_type='point_source'))
Cs_V_Optical_Pump_1.draw(table, Cs_V_Optical_Pump_1_Path)

# Cs_V_Optical_Pump_2_Path.append(optical_elements[114.1])
Cs_V_Optical_Pump_2_Path.append(pyopt.OpticalElement(x_conv(21.3 - 0.05 + x_displacement), y_conv(17.3 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_2_Path.append(optical_elements[99])
Cs_V_Optical_Pump_2_Path.append(pyopt.OpticalElement(x_conv(22.3 + x_displacement), y_conv(16.3 - 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_2_Path.append(optical_elements[109])
Cs_V_Optical_Pump_2_Path.append(pyopt.OpticalElement(x_conv(14 + x_displacement), y_conv(8 - 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_2_Path.append(optical_elements[188])
Cs_V_Optical_Pump_2_Path.append(pyopt.OpticalElement(x_conv(15.4 + x_displacement), y_conv(6.6 - 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_2_Path.append(optical_elements[250])
Cs_V_Optical_Pump_2_Path.append(pyopt.OpticalElement(x_conv(2 + x_displacement_3), y_conv(7 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
Cs_V_Optical_Pump_2.draw(table, Cs_V_Optical_Pump_2_Path)

Cs_V_Optical_Pump_3_Path.append(optical_elements[321])
Cs_V_Optical_Pump_3_Path.append(optical_elements[309])
Cs_V_Optical_Pump_3_Path.append(optical_elements[324])
Cs_V_Optical_Pump_3.draw(table, Cs_V_Optical_Pump_3_Path)

# Cs_V_Optical_Pump_4_Path.append(optical_elements[298])
Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(22.5 + x_displacement), y_conv(18.5 + 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_4_Path.append(optical_elements[95])
Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(26 - 0.05 + x_displacement), y_conv(22 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_4_Path.append(optical_elements[149])
Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(30 - 0.05 + x_displacement), y_conv(18 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_4_Path.append(optical_elements[120])
Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(37 + x_displacement), y_conv(24.5 + 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_4_Path.append(optical_elements[5])
Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(13.3 + x_displacement), y_conv(45.3 + 0.05 + y_displacement), 't', angle=0, element_type='point_source'))

Cs_V_Optical_Pump_4.draw(table, Cs_V_Optical_Pump_4_Path)

OTOP_1_Path.append(optical_elements[167])
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
# OTOP_1_Path.append(optical_elements[135])
OTOP_1_Path.append(pyopt.OpticalElement(x_conv(41 + x_displacement), y_conv(36.1 + y_displacement), 'r', angle=0, element_type='point_source'))
# OTOP_1_Path.append(optical_elements[136])
# OTOP_1_Path.append(optical_elements[137])
# OTOP_1_Path.append(optical_elements[94.5])
OTOP_1_Path.append(pyopt.OpticalElement(x_conv(28 + x_displacement), y_conv(36.1 + y_displacement), 't', angle=0, element_type='point_source'))
# OTOP_1_Path.append(optical_elements[257])
OTOP_1_Path.append(pyopt.OpticalElement(x_conv(13 + x_displacement), y_conv(36.1 + y_displacement), 'r', angle=0, element_type='point_source'))
OTOP_1_Path.append(optical_elements[97])
# OTOP_1_Path.append(optical_elements[92])
OTOP_1_Path.append(optical_elements[86])
OTOP_1_Path.append(optical_elements[85])
OTOP_1_Path.append(optical_elements[80])
OTOP_1_Path.append(optical_elements[81])
OTOP_1_Path.append(optical_elements[89])
OTOP_1.draw(table, OTOP_1_Path)

OTOP_2_Path.append(pyopt.OpticalElement(x_conv(41 + x_displacement), y_conv(36.1 + y_displacement), 'r', angle=0, element_type='point_source'))
OTOP_2_Path.append(optical_elements[128])
OTOP_2.draw(table, OTOP_2_Path)

OTOP_3_Path.append(optical_elements[80])
OTOP_3_Path.append(optical_elements[74])
OTOP_3_Path.append(optical_elements[75])
OTOP_3.draw(table, OTOP_3_Path)

# OTOP_4_Path.append(optical_elements[97])
OTOP_4_Path.append(pyopt.OpticalElement(x_conv(5 + x_displacement), y_conv(36.1 + y_displacement), 't', angle=0, element_type='point_source'))
# OTOP_4_Path.append(optical_elements[96])
OTOP_4_Path.append(pyopt.OpticalElement(x_conv(1.5 + x_displacement), y_conv(36.1 + y_displacement), 'r', angle=0, element_type='point_source'))
OTOP_4.draw(table, OTOP_4_Path)

OTOP_5_Path.append(optical_elements[74])
OTOP_5_Path.append(black_aluminum_dump_1)
OTOP_5.draw(table, OTOP_5_Path)

OTOP_6_Path.append(optical_elements[153])
OTOP_6_Path.append(optical_elements[156])
OTOP_6_Path.append(optical_elements[159])
OTOP_6_Path.append(optical_elements[155])
OTOP_6_Path.append(optical_elements[269])
OTOP_6_Path.append(optical_elements[270])
OTOP_6.draw(table, OTOP_6_Path)

OTOP_7_Path.append(optical_elements[167])
OTOP_7_Path.append(optical_elements[160])
OTOP_7_Path.append(optical_elements[165])
OTOP_7_Path.append(optical_elements[164])
OTOP_7_Path.append(optical_elements[268])
OTOP_7.draw(table, OTOP_7_Path)

OTOP_8_Path.append(optical_elements[165])
OTOP_8_Path.append(pyopt.OpticalElement(x_conv(41 + x_displacement_2), y_conv(80 + y_displacement_2), 't', angle=0, element_type='point_source'))
OTOP_8.draw(table, OTOP_8_Path)

# OTOP_9_Path.append(optical_elements[257])
OTOP_9_Path.append(pyopt.OpticalElement(x_conv(13 + 0.1), y_conv(36 + 0.1), 'r', angle=0, element_type='point_source'))
# OTOP_9_Path.append(optical_elements[258])
OTOP_9_Path.append(pyopt.OpticalElement(x_conv(13 + 0.1), y_conv(28 + 0.1), 'r', angle=0, element_type='point_source'))
# OTOP_9_Path.append(optical_elements[262])
OTOP_9_Path.append(pyopt.OpticalElement(x_conv(11 - 0.1), y_conv(28 + 0.1), 'r', angle=0, element_type='point_source'))
# OTOP_9_Path.append(optical_elements[263])
OTOP_9_Path.append(pyopt.OpticalElement(x_conv(11 - 0.1), y_conv(31), 't', angle=0, element_type='point_source'))
OTOP_9.draw(table, OTOP_9_Path)

# OTOP_10_Path.append(optical_elements[262])
OTOP_10_Path.append(pyopt.OpticalElement(x_conv(11 - 0.1), y_conv(28 + 0.1), 't', angle=0, element_type='point_source'))
# OTOP_10_Path.append(optical_elements[260])
OTOP_10_Path.append(pyopt.OpticalElement(x_conv(10), y_conv(28 + 0.1), 'r', angle=0, element_type='point_source'))
OTOP_10.draw(table, OTOP_10_Path)

Dual_Color_1_Path.append(optical_elements[129])
Dual_Color_1_Path.append(optical_elements[145])
# Dual_Color_1_Path.append(optical_elements[144])
Dual_Color_1_Path.append(optical_elements[142])
Dual_Color_1_Path.append(optical_elements[266])
Dual_Color_1_Path.append(optical_elements[135])
Dual_Color_1_Path.append(optical_elements[257])
Dual_Color_1_Path.append(optical_elements[258])
# Dual_Color_1_Path.append(optical_elements[259])
Dual_Color_1_Path.append(optical_elements[262])
Dual_Color_1_Path.append(optical_elements[263])
Dual_Color_1.draw(table, Dual_Color_1_Path)

Dual_Color_2_Path.append(optical_elements[129])
Dual_Color_2_Path.append(optical_elements[71])
Dual_Color_2.draw(table, Dual_Color_2_Path)

Dual_Color_3_Path.append(optical_elements[262])
Dual_Color_3_Path.append(optical_elements[260])
Dual_Color_3.draw(table, Dual_Color_3_Path)


# BFL_1_Path.append(optical_elements[141])
BFL_1_Path.append(optical_elements[138])
# BFL_1_Path.append(optical_elements[133])
# BFL_1_Path.append(optical_elements[130])
# BFL_1_Path.append(optical_elements[73])
# BFL_1_Path.append(optical_elements[49])
# BFL_1_Path.append(optical_elements[31])
# BFL_1_Path.append(optical_elements[26])
BFL_1_Path.append(optical_elements[11])
BFL_1_Path.append(optical_elements[7])
BFL_1_Path.append(optical_elements[122])
BFL_1_Path.append(optical_elements[134])
BFL_1_Path.append(optical_elements[139])
# BFL_1_Path.append(optical_elements[137])
BFL_1_Path.append(pyopt.OpticalElement(x_conv(30.88 + x_displacement), y_conv(36.6 + y_displacement), 't', angle=0, element_type='point_source'))
BFL_1_Path.append(optical_elements[189])
BFL_1.draw(table, BFL_1_Path)

BFL_2_Path.append(optical_elements[134])
# BFL_2_Path.append(optical_elements[137])
BFL_2_Path.append(pyopt.OpticalElement(x_conv(30.88 + x_displacement), y_conv(35.4 + y_displacement), 't', angle=0, element_type='point_source'))
BFL_2_Path.append(optical_elements[190])
BFL_2.draw(table, BFL_2_Path)


Cs_H_Optical_Pump_Path.append(optical_elements[124])
Cs_H_Optical_Pump_Path.append(optical_elements[126])
Cs_H_Optical_Pump_Path.append(optical_elements[123])
Cs_H_Optical_Pump_Path.append(optical_elements[9])
Cs_H_Optical_Pump_Path.append(optical_elements[68])
Cs_H_Optical_Pump_Path.append(optical_elements[41])
Cs_H_Optical_Pump.draw(table, Cs_H_Optical_Pump_Path)



file_path = "breadboard_optics_v3.pdf"
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
