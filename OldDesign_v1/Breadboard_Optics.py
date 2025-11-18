import pyopticaltable as pyopt
import matplotlib.pyplot as plt
import pandas as pd
import os


# Coordinate conversion functions
def x_conv(x):
    return x - 24

def y_conv(y):
    return y - 21

def minus_90_conv(angle_):
    return angle_ - 90

def plus_90_conv(angle_):
    return angle_ + 90


# Create the optical table
table = pyopt.OpticalTable(50, 44, size_factor=20, show_edge=True, show_grid=True, grid_spacing=1)

edge_width = 7

x1_1, x2_1, y1_1, y2_1 = table.angled_line(x=x_conv(-0.5), y=y_conv(21), size=37.8, angle=90, show=False, get_coords=True)
table.ax.plot([x1_1, x2_1], [y1_1, y2_1], color='blue', linewidth=edge_width)

x1_2, x2_2, y1_2, y2_2 = table.angled_line(x=x_conv(24), y=y_conv(-0.5), size=43, angle=0, show=False, get_coords=True)
table.ax.plot([x1_2, x2_2], [y1_2, y2_2], color='blue', linewidth=edge_width)

x1_3, x2_3, y1_3, y2_3 = table.angled_line(x=x_conv(48.5), y=y_conv(8.5), size=15.8, angle=90, show=False, get_coords=True)
table.ax.plot([x1_3, x2_3], [y1_3, y2_3], color='blue', linewidth=edge_width)

x1_4, x2_4, y1_4, y2_4 = table.angled_line(x=x_conv(10), y=y_conv(42.5), size=18.5, angle=0, show=False, get_coords=True)
table.ax.plot([x1_4, x2_4], [y1_4, y2_4], color='blue', linewidth=edge_width)

x1_5, x2_5, y1_5, y2_5 = table.angled_line(x=x_conv(20.5), y=y_conv(30), size=21.8, angle=90, show=False, get_coords=True)
table.ax.plot([x1_5, x2_5], [y1_5, y2_5], color='blue', linewidth=edge_width)

x1_6, x2_6, y1_6, y2_6 = table.angled_line(x=x_conv(34.5), y=y_conv(17.5), size=24.6, angle=0, show=False, get_coords=True)
table.ax.plot([x1_6, x2_6], [y1_6, y2_6], color='blue', linewidth=edge_width)

x1_7, x2_7, y1_7, y2_7 = table.angled_line(x=x_conv(48.5), y=y_conv(30.5), size=21, angle=90, show=False, get_coords=True)
table.ax.plot([x1_7, x2_7], [y1_7, y2_7], color='purple', linewidth=edge_width)

x1_8, x2_8, y1_8, y2_8 = table.angled_line(x=x_conv(41.5), y=y_conv(18.5), size=12.3, angle=0, show=False, get_coords=True)
table.ax.plot([x1_8, x2_8], [y1_8, y2_8], color='purple', linewidth=edge_width)

x1_9, x2_9, y1_9, y2_9 = table.angled_line(x=x_conv(34.5), y=y_conv(22), size=6.2, angle=90, show=False, get_coords=True)
table.ax.plot([x1_9, x2_9], [y1_9, y2_9], color='purple', linewidth=edge_width)

x1_10, x2_10, y1_10, y2_10 = table.angled_line(x=x_conv(31), y=y_conv(25.5), size=6.1, angle=0, show=False, get_coords=True)
table.ax.plot([x1_10, x2_10], [y1_10, y2_10], color='purple', linewidth=edge_width)

x1_11, x2_11, y1_11, y2_11 = table.angled_line(x=x_conv(27.5), y=y_conv(34), size=15, angle=90, show=False, get_coords=True)
table.ax.plot([x1_11, x2_11], [y1_11, y2_11], color='purple', linewidth=edge_width)

x1_12, x2_12, y1_12, y2_12 = table.angled_line(x=x_conv(38), y=y_conv(42.5), size=18.2, angle=0, show=False, get_coords=True)
table.ax.plot([x1_12, x2_12], [y1_12, y2_12], color='purple', linewidth=edge_width)

df = pd.read_csv('OpticsSetup(Breadboard).csv')


label_position = 'top'
label_color = 'dodgerblue'
laser_box_size_x = 0.5
laser_box_size_y = 1
laser_label_font_size = 20
optical_elements = {}


# Define laser beams


Li_H_Imaging = pyopt.LaserBeam(colour='magenta', width=1, style='-')
Li_H_Imaging_Path = []
optical_elements[37] = table.box_source(x=x_conv(2), y=y_conv(11), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=45, output_side='right', label='O-37 Li H Imaging', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Li_H_Imaging_Path.append(optical_elements[37])

Li_EOM = pyopt.LaserBeam(colour='magenta', width=1, style='-')
Li_EOM_Path = []
optical_elements[27] = table.box_source(x=x_conv(2), y=y_conv(8), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=45, output_side='right', label='O-27 Li EOM', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Li_EOM_Path.append(optical_elements[27])

Li_Repump_1 = pyopt.LaserBeam(colour='lime', width=2, style='-')
Li_Repump_1_Path = []
Li_Repump_2 = pyopt.LaserBeam(colour='lime', width=2, style='-')
Li_Repump_2_Path = []
Li_Repump_3 = pyopt.LaserBeam(colour='lime', width=2, style='-')
Li_Repump_3_Path = []
Li_Repump_4 = pyopt.LaserBeam(colour='lime', width=2, style='-')
Li_Repump_4_Path = []
optical_elements[15] = table.box_source(x=x_conv(8.5), y=y_conv(7.5), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=45, output_side='right', label='O-15 Li Repump', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Li_Repump_1_Path.append(optical_elements[15])

Li_MOT_1 = pyopt.LaserBeam(colour='purple', width=1, style='-')
Li_MOT_1_Path = []
Li_MOT_2 = pyopt.LaserBeam(colour='purple', width=1, style='-')
Li_MOT_2_Path = []
Li_MOT_3 = pyopt.LaserBeam(colour='purple', width=1, style='-')
Li_MOT_3_Path = []
Li_MOT_4 = pyopt.LaserBeam(colour='purple', width=1, style='-')
Li_MOT_4_Path = []
optical_elements[16] = table.box_source(x=x_conv(11.25), y=y_conv(6.75), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=45, output_side='right', label='O-16 Li MOT', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Li_MOT_1_Path.append(optical_elements[16])

Cs_MOT_1 = pyopt.LaserBeam(colour='green', width=1, style='-')
Cs_MOT_1_Path = []
Cs_MOT_2 = pyopt.LaserBeam(colour='green', width=1, style='-')
Cs_MOT_2_Path = []
Cs_MOT_3 = pyopt.LaserBeam(colour='green', width=1, style='-')
Cs_MOT_3_Path = []
Cs_MOT_4 = pyopt.LaserBeam(colour='green', width=1, style='--')
Cs_MOT_4_Path = []
optical_elements[17] = table.box_source(x=x_conv(15), y=y_conv(7), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=45, output_side='right', label='O-17 Cs MOT', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Cs_MOT_1_Path.append(optical_elements[17])

Cs_H_Imaging_1 = pyopt.LaserBeam(colour='cyan', width=1, style='-')
Cs_H_Imaging_1_Path = []
Cs_H_Imaging_2 = pyopt.LaserBeam(colour='cyan', width=1, style='--')
Cs_H_Imaging_2_Path = []
Cs_H_Imaging_3 = pyopt.LaserBeam(colour='cyan', width=1, style='-')
Cs_H_Imaging_3_Path = []
optical_elements[12] = table.box_source(x=x_conv(17), y=y_conv(5), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=45, output_side='right', label='O-12 Cs H Imaging', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Cs_H_Imaging_1_Path.append(optical_elements[12])

Li_Zeeman = pyopt.LaserBeam(colour='red', width=1, style='-')  # Transmitted beam
Li_Zeeman_Path = []
optical_elements[25] = table.box_source(x=x_conv(39), y=y_conv(7), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=180, output_side='right', label='O-25 Li Zeeman', label_pos='right', labelpad=2, textcolour=label_color, fontsize=laser_label_font_size)
Li_Zeeman_Path.append(optical_elements[25])

Cs_Zeeman = pyopt.LaserBeam(colour='blue', width=1, style='-')
Cs_Zeeman_Path = []
optical_elements[48] = table.box_source(x=x_conv(37), y=y_conv(11), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=180, output_side='right', label='O-48 Cs Zeeman', label_pos='right', labelpad=2, textcolour=label_color, fontsize=laser_label_font_size)
Cs_Zeeman_Path.append(optical_elements[48])

Cs_V_Optical_Pump_1 = pyopt.LaserBeam(colour='navy', width=1, style='-')
Cs_V_Optical_Pump_1_Path = []
Cs_V_Optical_Pump_2 = pyopt.LaserBeam(colour='navy', width=1, style='-')
Cs_V_Optical_Pump_2_Path = []
Cs_V_Optical_Pump_3 = pyopt.LaserBeam(colour='navy', width=1, style='-')
Cs_V_Optical_Pump_3_Path = []
optical_elements[116] = table.box_source(x=x_conv(5), y=y_conv(41), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=0, output_side='right', label='O-116 Cs V Optical Pump', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Cs_V_Optical_Pump_1_Path.append(optical_elements[116])

RSC_1 = pyopt.LaserBeam(colour='coral', width=1, style='-')
RSC_1_Path = []
RSC_2 = pyopt.LaserBeam(colour='coral', width=1, style='-')
RSC_2_Path = []
RSC_3 = pyopt.LaserBeam(colour='coral', width=1, style='-')
RSC_3_Path = []
optical_elements[110] = table.box_source(x=x_conv(5), y=y_conv(38.9), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=0, output_side='right', label='O-110 RSC', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
RSC_1_Path.append(optical_elements[110])

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
OTOP_1_Path.append(table.point_source(x=x_conv(41), y=y_conv(46), label='OTOP', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size))

Dual_Color_1 = pyopt.LaserBeam(colour='violet', width=3, style='-')
Dual_Color_1_Path = []
Dual_Color_2 = pyopt.LaserBeam(colour='violet', width=3, style='-')
Dual_Color_2_Path = []
optical_elements[148] = table.box_source(x=x_conv(43), y=y_conv(44), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=-90, output_side='right', label='O-148 Dual Color', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Dual_Color_1_Path.append(optical_elements[148])

BFL_1 = pyopt.LaserBeam(colour='cornflowerblue', width=3, style='-')
BFL_1_Path = []
BFL_2 = pyopt.LaserBeam(colour='cornflowerblue', width=3, style='-')
BFL_2_Path = []
optical_elements[150] = table.box_source(x=x_conv(47), y=y_conv(37), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=-90, output_side='right', label='O-150 BFL', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
BFL_1_Path.append(optical_elements[150])

Cs_H_Optical_Pump = pyopt.LaserBeam(colour='hotpink', width=2, style='-')
Cs_H_Optical_Pump_Path = []
optical_elements[127] = table.box_source(x=x_conv(37), y=y_conv(24), size_x=laser_box_size_x, size_y=laser_box_size_y, angle=-45, output_side='right', label='O-127 Cs H Optical Pump', label_pos=label_position, labelpad=0.6, textcolour=label_color, fontsize=laser_label_font_size)
Cs_H_Optical_Pump_Path.append(optical_elements[127])


for _, row in df.iterrows():

    limit = 305
    done = 148

    label = str(row['Label']).strip()
    i = float(label.split('-')[1])

    if i == limit:
        break
    if i in (258, 259, 260, 261, 262, 263, 270, 277, 278, 300, 301, 302):
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

    if type_ in 'mirror' or type_ == 'periscope mirror':
        optical_elements[i] = table.mirror(x=x, y=y, size=0.4, angle=minus_90_conv(angle), label=label+' '+type_,
                                           label_pos=label_position, labelpad=0.1, textcolour=label_color)
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
    elif type_ == 'waveplate':
        optical_elements[i] = table.transmissive_plate(x=x, y=y, size=0.4, angle=minus_90_conv(angle), fill=True, fillcolour='c', label=label+' '+type_,
                                                       label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'lens' or type_ == 'convex rectangular lens':
        optical_elements[i] = table.convex_lens(x=x, y=y, size=0.5, angle=plus_90_conv(angle), label=label+' '+type_,
                                                label_pos=label_position, labelpad=0.07, textcolour=label_color)
    elif type_ == 'PD':
        optical_elements[i] = table.box(x=x, y=y, size_x=0.3, size_y=0.7, angle=angle, linestyle='--', standalone=True, label=label+' '+type_,
                                        label_pos=label_position, labelpad=0.5, textcolour=label_color)
    elif type_ == 'chamber port':
        optical_elements[i] = table.box(x=x, y=y, size_x=0.3, size_y=2, angle=angle, standalone=True, label=label+' '+type_,
                                        label_pos=label_position, labelpad=0.35, textcolour=label_color)
    elif type_ == 'post':
        optical_elements[i] = table.generic_circle(x=x, y=y, size=0.25, colour='k', fill=False, fillcolour='k', label=label+' '+type_,
                                        label_pos=label_position, labelpad=0.35, textcolour=label_color)
    else:
        if i > done:
            print(f"Skipping unknown element: {label + ' ' + type_}")


optical_elements[31] = table.box(x=x_conv(47), y=y_conv(9), size_x=0.3, size_y=1.5, angle=minus_90_conv(90), standalone=True, label='O-31 lens tube', label_pos='right', labelpad=0.3, textcolour=label_color)
optical_elements[36] = table.box(x=x_conv(47), y=y_conv(10), size_x=1.7, size_y=0.1, angle=minus_90_conv(90), colour='orange', standalone=True, label='O-36 copper plate',
                                 label_pos='top', labelpad=0.2, textcolour=label_color)
optical_elements[72.1] = table.box(x=x_conv(43), y=y_conv(16.5), size_x=0.3, size_y=2.7, angle=minus_90_conv(90), standalone=True, label='O-72.1 lens tube',
                                   label_pos='right', labelpad=0.6, textcolour=label_color)
optical_elements[72.3] = table.box(x=x_conv(41.65), y=y_conv(15), size_x=0.3, size_y=3, angle=minus_90_conv(0), standalone=True, label='',
                                      label_pos='right', labelpad=0.3, textcolour=label_color)
optical_elements[73] = table.box(x=x_conv(47), y=y_conv(17), size_x=0.3, size_y=9, angle=minus_90_conv(90), standalone=True, label='O-73 lens tube',
                                 label_pos='right', labelpad=0.5, textcolour=label_color)
optical_elements[80] = table.mirror(x=x_conv(0.5), y=y_conv(18), size=0.4, angle=minus_90_conv(50), label='O-80 50-50 beam splitter',
                                           label_pos='top', labelpad=0.1, textcolour=label_color)
optical_elements[89] = table.box(x=x_conv(2.5), y=y_conv(21), size_x=0.3, size_y=0.7, angle=-50, standalone=True, label='O-89 OTOP monitor camera',
                                 label_pos=label_position, labelpad=0.4, textcolour=label_color)
optical_elements[103] = table.box(x=x_conv(12), y=y_conv(32.5), size_x=0.3, size_y=1.3, angle=minus_90_conv(160), standalone=True, label='O-103 quadrant detector sensor head',
                                  label_pos=label_position, labelpad=0.5, textcolour=label_color)
optical_elements[130] = table.box(x=x_conv(47), y=y_conv(24), size_x=1, size_y=0.5, angle=minus_90_conv(90), standalone=True, label='O-130 BFL AOM',
                                  label_pos=label_position, labelpad=0.4, textcolour=label_color)
optical_elements[134] = table.box(x=x_conv(44.5), y=y_conv(27.5), size_x=0.5, size_y=0.1, angle=minus_90_conv(-135), colour='b', standalone=True, label='O-134 flat PBS',
                                           label_pos=label_position, labelpad=0.4, textcolour=label_color)
optical_elements[137] = table.box(x=x_conv(32), y=y_conv(28), size_x=3.5, size_y=2, angle=0, standalone=True, label='O-137 3-hole tube',
                                        label_pos=label_position, labelpad=0.25, textcolour=label_color)
three_hole_tube_lens = table.convex_lens(x=x_conv(31), y=y_conv(28), size=1.3, angle=plus_90_conv(0), label='',
                                                label_pos=label_position, labelpad=0.07, textcolour=label_color)
optical_elements[138] = table.box(x=x_conv(47), y=y_conv(31.75), size_x=0.3, size_y=8, angle=minus_90_conv(90), standalone=True, label='O-138 lens tube',
                                 label_pos='right', labelpad=0.5, textcolour=label_color)
optical_elements[143] = table.box(x=x_conv(45), y=y_conv(35), size_x=0.3, size_y=1.7, angle=minus_90_conv(90), standalone=True, label='O-143 lens tube',
                                 label_pos='right', labelpad=0.5, textcolour=label_color)
optical_elements[251] = table.box(x=x_conv(30), y=y_conv(34), size_x=0.6, size_y=6, angle=minus_90_conv(-135), standalone=True, label='O-251 waveplate & polarizer in front of camera',
                                 label_pos=label_position, labelpad=0.3, textcolour=label_color)
optical_elements[279] = table.box(x=x_conv(10.5), y=y_conv(30), size_x=0.3, size_y=0.7, angle=-10, standalone=True, label='O-279 monitor camera',
                                 label_pos=label_position, labelpad=0.5, textcolour=label_color)
black_aluminum_dump_1 = table.beam_dump(x=x_conv(0.5), y=y_conv(15), size=0.4, angle=minus_90_conv(90), colour='k', fillcolour='k', label='black aluminum dump',
                                              label_pos=label_position, labelpad=0.1, textcolour=label_color)
center = table.generic_circle(x=x_conv(24), y=y_conv(28), size=0.5, colour='gold', fill=True, fillcolour='gold', label='center',
                                        label_pos=label_position, labelpad=0.3, textcolour=label_color)


Li_H_Imaging_Path.append(optical_elements[51])
# Li_H_Imaging_Path.append(optical_elements[59])
Li_H_Imaging_Path.append(optical_elements[82])
# Li_H_Imaging_Path.append(optical_elements[39])
Li_H_Imaging_Path.append(pyopt.OpticalElement(x_conv(14.35), y_conv(11.65), 't', angle=0, element_type='point_source'))
Li_H_Imaging_Path.append(optical_elements[34])
Li_H_Imaging_Path.append(optical_elements[60])
# Li_H_Imaging_Path.append(optical_elements[94.2])
# Li_H_Imaging_Path.append(optical_elements[251])
Li_H_Imaging_Path.append(pyopt.OpticalElement(x_conv(32), y_conv(36.2), 't', angle=0, element_type='point_source'))
Li_H_Imaging.draw(table, Li_H_Imaging_Path)

Li_EOM_Path.append(optical_elements[32])
Li_EOM_Path.append(optical_elements[38])
# Li_EOM_Path.append(optical_elements[50])
Li_EOM_Path.append(pyopt.OpticalElement(x_conv(3.45), y_conv(12.55), 't', angle=0, element_type='point_source'))
# Li_EOM_Path.append(optical_elements[51])
Li_EOM_Path.append(pyopt.OpticalElement(x_conv(3.95), y_conv(13.05), 't', angle=0, element_type='point_source'))
# Li_EOM_Path.append(optical_elements[59])
# Li_EOM_Path.append(optical_elements[82])
Li_EOM_Path.append(pyopt.OpticalElement(x_conv(8.9), y_conv(18), 't', angle=0, element_type='point_source'))
# Li_EOM_Path.append(optical_elements[39])
Li_EOM_Path.append(pyopt.OpticalElement(x_conv(14.35), y_conv(11.53), 't', angle=0, element_type='point_source'))
# Li_EOM_Path.append(optical_elements[34])
Li_EOM_Path.append(pyopt.OpticalElement(x_conv(12.6), y_conv(10), 'r', angle=0, element_type='point_source'))
# Li_EOM_Path.append(optical_elements[60])
Li_EOM_Path.append(pyopt.OpticalElement(x_conv(9.4), y_conv(13.7), 't', angle=0, element_type='point_source'))
# Li_EOM_Path.append(optical_elements[61])
# Li_EOM_Path.append(optical_elements[184])
# Li_EOM_Path.append(optical_elements[94.2])
# Li_EOM_Path.append(optical_elements[251])
Li_EOM_Path.append(pyopt.OpticalElement(x_conv(32), y_conv(36.3), 't', angle=0, element_type='point_source'))
Li_EOM.draw(table, Li_EOM_Path)


Li_Repump_1_Path.append(optical_elements[28])
# Li_Repump_1_Path.append(optical_elements[63])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(13.9), y_conv(13), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[40])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(15.65), y_conv(11.25), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[66])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(20.5), y_conv(16.1), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[78.2])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(19.6), y_conv(17), 't', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[99])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(3.5), y_conv(33.1), 'r', angle=0, element_type='point_source'))
# Li_Repump_1_Path.append(optical_elements[250])
Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(17.9), y_conv(44), 'r', angle=0, element_type='point_source'))
Li_Repump_1.draw(table, Li_Repump_1_Path)

# Li_Repump_2_Path.append(optical_elements[40])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(15.65), y_conv(11.25), 'r', angle=0, element_type='point_source'))
# Li_Repump_2_Path.append(optical_elements[13])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(22.5), y_conv(4.4), 'r', angle=0, element_type='point_source'))
# Li_Repump_2_Path.append(optical_elements[5])
Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(13), y_conv(0.9), 'r', angle=0, element_type='point_source'))
Li_Repump_2.draw(table, Li_Repump_2_Path)

# Li_Repump_3_Path.append(optical_elements[78.2])
Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(19.6), y_conv(17), 't', angle=0, element_type='point_source'))
# Li_Repump_3_Path.append(optical_elements[34])
Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(12.57), y_conv(9.98), 'r', angle=0, element_type='point_source'))
# Li_Repump_3_Path.append(optical_elements[60])
Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(9.4), y_conv(13.65), 'r', angle=0, element_type='point_source'))
# Li_Repump_3_Path.append(optical_elements[94.2])
Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(21), y_conv(25.25), 't', angle=0, element_type='point_source'))
# Li_Repump_3_Path.append(optical_elements[94.6])
# Li_Repump_3_Path.append(optical_elements[251])
Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(32), y_conv(36.25), 't', angle=0, element_type='point_source'))
Li_Repump_3.draw(table, Li_Repump_3_Path)

# Li_Repump_4_Path.append(optical_elements[64.1])
Li_Repump_4_Path.append(pyopt.OpticalElement(x_conv(16.85), y_conv(14.25), 't', angle=0, element_type='point_source'))
# Li_Repump_4_Path.append(optical_elements[91])
Li_Repump_4_Path.append(pyopt.OpticalElement(x_conv(8.47), y_conv(22.63), 't', angle=0, element_type='point_source'))
# Li_Repump_4_Path.append(optical_elements[107])
Li_Repump_4_Path.append(pyopt.OpticalElement(x_conv(18.848), y_conv(33), 't', angle=0, element_type='point_source'))
# Li_Repump_4_Path.append(optical_elements[70])
Li_Repump_4_Path.append(pyopt.OpticalElement(x_conv(36.925), y_conv(14.925), 't', angle=0, element_type='point_source'))
Li_Repump_4.draw(table, Li_Repump_4_Path)


Li_MOT_1_Path.append(optical_elements[255])
Li_MOT_1_Path.append(optical_elements[40])
Li_MOT_1_Path.append(optical_elements[66])
# Li_MOT_1_Path.append(optical_elements[78.3])
# Li_MOT_1_Path.append(optical_elements[78.2])
Li_MOT_1_Path.append(optical_elements[78.1])
Li_MOT_1_Path.append(optical_elements[99])
Li_MOT_1_Path.append(optical_elements[250])
Li_MOT_1.draw(table, Li_MOT_1_Path)

Li_MOT_2_Path.append(optical_elements[40])
Li_MOT_2_Path.append(optical_elements[13])
Li_MOT_2_Path.append(optical_elements[5])
Li_MOT_2.draw(table, Li_MOT_2_Path)

Li_MOT_3_Path.append(optical_elements[78.2])
# Li_MOT_3_Path.append(optical_elements[65.3])
# Li_MOT_3_Path.append(optical_elements[65.2])
# Li_MOT_3_Path.append(optical_elements[65.1])
Li_MOT_3_Path.append(optical_elements[64.1])
# Li_MOT_3_Path.append(optical_elements[55.3])
# Li_MOT_3_Path.append(optical_elements[55.2])
# Li_MOT_3_Path.append(optical_elements[55.1])
# Li_MOT_3_Path.append(optical_elements[34])
Li_MOT_3_Path.append(pyopt.OpticalElement(x_conv(12.47), y_conv(9.97), 'r', angle=0, element_type='point_source'))
# Li_MOT_3_Path.append(optical_elements[60])
Li_MOT_3_Path.append(pyopt.OpticalElement(x_conv(9.44), y_conv(13.49), 'r', angle=0, element_type='point_source'))
# Li_MOT_3_Path.append(optical_elements[61])
# Li_MOT_3_Path.append(optical_elements[184])
# Li_MOT_3_Path.append(optical_elements[94.2])
# Li_MOT_3_Path.append(optical_elements[251])
Li_MOT_3_Path.append(pyopt.OpticalElement(x_conv(32), y_conv(36.045), 't', angle=0, element_type='point_source'))
Li_MOT_3.draw(table, Li_MOT_3_Path)

Li_MOT_4_Path.append(optical_elements[64.1])
Li_MOT_4_Path.append(optical_elements[64.2])
Li_MOT_4_Path.append(optical_elements[64.3])
Li_MOT_4_Path.append(optical_elements[83])
# Li_MOT_4_Path.append(optical_elements[91])
Li_MOT_4_Path.append(pyopt.OpticalElement(x_conv(8.45), y_conv(22.55), 'r', angle=0, element_type='point_source'))
# Li_MOT_4_Path.append(optical_elements[107])
Li_MOT_4_Path.append(pyopt.OpticalElement(x_conv(18.9), y_conv(33), 'r', angle=0, element_type='point_source'))
# Li_MOT_4_Path.append(optical_elements[94.4])
Li_MOT_4_Path.append(pyopt.OpticalElement(x_conv(21), y_conv(30.9), 't', angle=0, element_type='point_source'))
# Li_MOT_4_Path.append(optical_elements[94.7])
# Li_MOT_4_Path.append(optical_elements[69])
# Li_MOT_4_Path.append(optical_elements[70])
Li_MOT_4_Path.append(pyopt.OpticalElement(x_conv(36.95), y_conv(14.95), 't', angle=0, element_type='point_source'))
Li_MOT_4.draw(table, Li_MOT_4_Path)


Cs_MOT_1_Path.append(optical_elements[29])
Cs_MOT_1_Path.append(optical_elements[57])
# Cs_MOT_1_Path.append(optical_elements[56])
# Cs_MOT_1_Path.append(optical_elements[79.1])
# Cs_MOT_1_Path.append(optical_elements[79.2])
Cs_MOT_1_Path.append(optical_elements[98])
# Cs_MOT_1_Path.append(optical_elements[250])
Cs_MOT_1_Path.append(pyopt.OpticalElement(x_conv(18.2), y_conv(44), 'r', angle=0, element_type='point_source'))
Cs_MOT_1.draw(table, Cs_MOT_1_Path)

Cs_MOT_2_Path.append(optical_elements[79.1])
Cs_MOT_2_Path.append(optical_elements[77])
Cs_MOT_2_Path.append(optical_elements[76.3])
Cs_MOT_2_Path.append(optical_elements[62])
Cs_MOT_2_Path.append(optical_elements[54])
Cs_MOT_2_Path.append(optical_elements[33])
# Cs_MOT_2_Path.append(optical_elements[53])
Cs_MOT_2_Path.append(optical_elements[52])
# Cs_MOT_2_Path.append(optical_elements[60])
# Cs_MOT_2_Path.append(optical_elements[61])
# Cs_MOT_2_Path.append(optical_elements[184])
Cs_MOT_2_Path.append(optical_elements[94.2])
# Cs_MOT_2_Path.append(optical_elements[251])
Cs_MOT_2_Path.append(pyopt.OpticalElement(x_conv(32), y_conv(36), 't', angle=0, element_type='point_source'))
Cs_MOT_2.draw(table, Cs_MOT_2_Path)

Cs_MOT_3_Path.append(optical_elements[76.3])
# Cs_MOT_3_Path.append(optical_elements[76.2])
# Cs_MOT_3_Path.append(optical_elements[76.1])
# Cs_MOT_3_Path.append(optical_elements[88])
Cs_MOT_3_Path.append(optical_elements[93])
Cs_MOT_3_Path.append(optical_elements[87])
# Cs_MOT_3_Path.append(optical_elements[91])
# Cs_MOT_3_Path.append(optical_elements[186])
# Cs_MOT_3_Path.append(optical_elements[106])
Cs_MOT_3_Path.append(optical_elements[107])
# Cs_MOT_3_Path.append(optical_elements[94.4])
Cs_MOT_3_Path.append(pyopt.OpticalElement(x_conv(21), y_conv(31), 't', angle=0, element_type='point_source'))
# Cs_MOT_3_Path.append(optical_elements[69])
Cs_MOT_3_Path.append(optical_elements[70])
Cs_MOT_3.draw(table, Cs_MOT_3_Path)

Cs_MOT_4_Path.append(optical_elements[79.1])
Cs_MOT_4_Path.append(optical_elements[84])
Cs_MOT_4.draw(table, Cs_MOT_4_Path)

Cs_H_Imaging_1_Path.append(optical_elements[18])
# Cs_H_Imaging_1_Path.append(optical_elements[30])
Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(20.75), y_conv(8.65), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_1_Path.append(optical_elements[55.3])
# Cs_H_Imaging_1_Path.append(optical_elements[76.3])
Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(14), y_conv(15.4), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_1_Path.append(optical_elements[62])
Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(13.05), y_conv(14.45), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_1_Path.append(optical_elements[54])
Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(10.05), y_conv(11.45), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_1_Path.append(optical_elements[33])
Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(9.1), y_conv(10.5), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_1_Path.append(optical_elements[53])
# Cs_H_Imaging_1_Path.append(optical_elements[52])
Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(7.75), y_conv(11.85), 'r', angle=0, element_type='point_source'))
# Cs_H_Imaging_1_Path.append(optical_elements[60])
# Cs_H_Imaging_1_Path.append(optical_elements[61])
# Cs_H_Imaging_1_Path.append(optical_elements[184])
# Cs_H_Imaging_1_Path.append(optical_elements[94.2])
# Cs_H_Imaging_1_Path.append(optical_elements[251])
Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(32), y_conv(36.09), 't', angle=0, element_type='point_source'))
Cs_H_Imaging_1.draw(table, Cs_H_Imaging_1_Path)

# Cs_H_Imaging_2_Path.append(optical_elements[76.3])
Cs_H_Imaging_2_Path.append(pyopt.OpticalElement(x_conv(14), y_conv(15.4), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_2_Path.append(optical_elements[76.2])
# Cs_H_Imaging_2_Path.append(optical_elements[76.1])
# Cs_H_Imaging_2_Path.append(optical_elements[88])
# Cs_H_Imaging_2_Path.append(optical_elements[93])
Cs_H_Imaging_2_Path.append(pyopt.OpticalElement(x_conv(6), y_conv(23.4), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_2_Path.append(optical_elements[87])
Cs_H_Imaging_2_Path.append(pyopt.OpticalElement(x_conv(7), y_conv(20.9), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_2_Path.append(optical_elements[91])
# Cs_H_Imaging_2_Path.append(optical_elements[186])
# Cs_H_Imaging_2_Path.append(optical_elements[106])
# Cs_H_Imaging_2_Path.append(optical_elements[107])
Cs_H_Imaging_2_Path.append(pyopt.OpticalElement(x_conv(19.1), y_conv(33), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_2_Path.append(optical_elements[94.4])
Cs_H_Imaging_2_Path.append(pyopt.OpticalElement(x_conv(21), y_conv(31.1), 't', angle=0, element_type='point_source'))
Cs_H_Imaging_2.draw(table, Cs_H_Imaging_2_Path)

# Cs_H_Imaging_3_Path.append(optical_elements[55.3])
Cs_H_Imaging_3_Path.append(pyopt.OpticalElement(x_conv(16.035), y_conv(13.365), 't', angle=0, element_type='point_source'))
# Cs_H_Imaging_3_Path.append(optical_elements[64.1])
Cs_H_Imaging_3_Path.append(pyopt.OpticalElement(x_conv(16.91), y_conv(14.25), 'r', angle=0, element_type='point_source'))
Cs_H_Imaging_3_Path.append(optical_elements[41])
Cs_H_Imaging_3.draw(table, Cs_H_Imaging_3_Path)


Li_Zeeman_Path.append(optical_elements[24])
Li_Zeeman_Path.append(optical_elements[23])
Li_Zeeman_Path.append(optical_elements[22])
Li_Zeeman_Path.append(optical_elements[21])
Li_Zeeman_Path.append(optical_elements[20])
Li_Zeeman_Path.append(optical_elements[19])
Li_Zeeman_Path.append(optical_elements[67])
# Li_Zeeman_Path.append(optical_elements[58])
Li_Zeeman_Path.append(pyopt.OpticalElement(x_conv(24), y_conv(13), 'r', angle=0, element_type='point_source'))
Li_Zeeman_Path.append(optical_elements[94.1])
Li_Zeeman_Path.append(pyopt.OpticalElement(x_conv(24), y_conv(34), 'r', angle=0, element_type='point_source'))
Li_Zeeman.draw(table, Li_Zeeman_Path)

Cs_Zeeman_Path.append(optical_elements[47])
Cs_Zeeman_Path.append(optical_elements[46])
Cs_Zeeman_Path.append(optical_elements[45])
Cs_Zeeman_Path.append(optical_elements[44])
Cs_Zeeman_Path.append(optical_elements[43])
# Cs_Zeeman_Path.append(optical_elements[42])
Cs_Zeeman_Path.append(optical_elements[35])
# Cs_Zeeman_Path.append(optical_elements[58])
# Cs_Zeeman_Path.append(optical_elements[94.1])
Cs_Zeeman_Path.append(pyopt.OpticalElement(x_conv(23.5), y_conv(16), 't', angle=0, element_type='point_source'))
Cs_Zeeman_Path.append(pyopt.OpticalElement(x_conv(23.5), y_conv(34), 'r', angle=0, element_type='point_source'))
Cs_Zeeman.draw(table, Cs_Zeeman_Path)


# RSC_1_Path.append(optical_elements[111])
RSC_1_Path.append(pyopt.OpticalElement(x_conv(7), y_conv(38.9), 't', angle=0, element_type='point_source'))
# RSC_1_Path.append(optical_elements[112])
RSC_1_Path.append(pyopt.OpticalElement(x_conv(9), y_conv(38.9), 't', angle=0, element_type='point_source'))
# RSC_1_Path.append(optical_elements[121])
RSC_1_Path.append(pyopt.OpticalElement(x_conv(20), y_conv(38.9), 'r', angle=0, element_type='point_source'))
# RSC_1_Path.append(optical_elements[105])
RSC_1_Path.append(pyopt.OpticalElement(x_conv(17), y_conv(33.9), 'r', angle=0, element_type='point_source'))
# center
RSC_1_Path.append(pyopt.OpticalElement(x_conv(24), y_conv(27.9), 't', angle=0, element_type='point_source'))
RSC_1.draw(table, RSC_1_Path)

# RSC_2_Path.append(optical_elements[298])
RSC_2_Path.append(pyopt.OpticalElement(x_conv(15.6), y_conv(38.9), 't', angle=0, element_type='point_source'))
# RSC_2_Path.append(optical_elements[113])
# RSC_2_Path.append(optical_elements[185])
RSC_2_Path.append(pyopt.OpticalElement(x_conv(15.6), y_conv(24.9), 'r', angle=0, element_type='point_source'))
# RSC_2_Path.append(optical_elements[188])
RSC_2_Path.append(pyopt.OpticalElement(x_conv(19.9), y_conv(23.47), 'r', angle=0, element_type='point_source'))
# RSC_2_Path.append(optical_elements[298.5])
# RSC_2_Path.append(optical_elements[287])
# RSC_2_Path.append(optical_elements[288])
RSC_2_Path.append(pyopt.OpticalElement(x_conv(31.45), y_conv(37.02), 'r', angle=0, element_type='point_source'))
RSC_2.draw(table, RSC_2_Path)

# RSC_3_Path.append(optical_elements[114.1])
RSC_3_Path.append(pyopt.OpticalElement(x_conv(13.6), y_conv(38.9), 't', angle=0, element_type='point_source'))
# RSC_3_Path.append(optical_elements[109])
RSC_3_Path.append(pyopt.OpticalElement(x_conv(13.6), y_conv(36.1), 't', angle=0, element_type='point_source'))
# RSC_3_Path.append(optical_elements[231])
RSC_3_Path.append(pyopt.OpticalElement(x_conv(-3), y_conv(34.6), 't', angle=0, element_type='point_source'))
RSC_3.draw(table, RSC_3_Path)


Cs_V_Optical_Pump_1_Path.append(optical_elements[117])
Cs_V_Optical_Pump_1_Path.append(optical_elements[118])
Cs_V_Optical_Pump_1_Path.append(optical_elements[119])
Cs_V_Optical_Pump_1_Path.append(optical_elements[114.1])
Cs_V_Optical_Pump_1_Path.append(optical_elements[114.2])
Cs_V_Optical_Pump_1_Path.append(optical_elements[298])
Cs_V_Optical_Pump_1_Path.append(optical_elements[115])
Cs_V_Optical_Pump_1_Path.append(optical_elements[121])
Cs_V_Optical_Pump_1_Path.append(optical_elements[105])
# center
Cs_V_Optical_Pump_1_Path.append(pyopt.OpticalElement(x_conv(24), y_conv(28), 't', angle=0, element_type='point_source'))
Cs_V_Optical_Pump_1.draw(table, Cs_V_Optical_Pump_1_Path)

Cs_V_Optical_Pump_2_Path.append(optical_elements[298])
Cs_V_Optical_Pump_2_Path.append(optical_elements[113])
Cs_V_Optical_Pump_2_Path.append(optical_elements[185])
Cs_V_Optical_Pump_2_Path.append(optical_elements[188])
# Cs_V_Optical_Pump_2_Path.append(optical_elements[298.5])
# Cs_V_Optical_Pump_2_Path.append(optical_elements[94.2])
# Cs_V_Optical_Pump_2_Path.append(optical_elements[287])
Cs_V_Optical_Pump_2_Path.append(optical_elements[288])
Cs_V_Optical_Pump_2.draw(table, Cs_V_Optical_Pump_2_Path)

Cs_V_Optical_Pump_3_Path.append(optical_elements[114.1])
Cs_V_Optical_Pump_3_Path.append(optical_elements[109])
# Cs_V_Optical_Pump_3_Path.append(optical_elements[108])
# Cs_V_Optical_Pump_3_Path.append(optical_elements[100])
Cs_V_Optical_Pump_3_Path.append(optical_elements[231])
Cs_V_Optical_Pump_3.draw(table, Cs_V_Optical_Pump_3_Path)


OTOP_1_Path.append(optical_elements[149])
# OTOP_1_Path.append(optical_elements[135])
OTOP_1_Path.append(pyopt.OpticalElement(x_conv(41), y_conv(28.1), 'r', angle=0, element_type='point_source'))
# OTOP_1_Path.append(optical_elements[136])
# OTOP_1_Path.append(optical_elements[137])
# OTOP_1_Path.append(optical_elements[94.5])
OTOP_1_Path.append(pyopt.OpticalElement(x_conv(28), y_conv(28.1), 't', angle=0, element_type='point_source'))
# OTOP_1_Path.append(optical_elements[257])
OTOP_1_Path.append(pyopt.OpticalElement(x_conv(13), y_conv(28.1), 'r', angle=0, element_type='point_source'))
# OTOP_1_Path.append(optical_elements[97])
OTOP_1_Path.append(pyopt.OpticalElement(x_conv(4.1), y_conv(28.1), 'r', angle=0, element_type='point_source'))
# OTOP_1_Path.append(optical_elements[92])
OTOP_1_Path.append(optical_elements[86])
OTOP_1_Path.append(optical_elements[85])
OTOP_1_Path.append(optical_elements[80])
OTOP_1_Path.append(optical_elements[81])
OTOP_1_Path.append(optical_elements[89])
OTOP_1.draw(table, OTOP_1_Path)

OTOP_3_Path.append(optical_elements[80])
OTOP_3_Path.append(optical_elements[74])
OTOP_3_Path.append(optical_elements[75])
OTOP_3.draw(table, OTOP_3_Path)

# OTOP_4_Path.append(optical_elements[97])
OTOP_4_Path.append(pyopt.OpticalElement(x_conv(4.1), y_conv(28.1), 't', angle=0, element_type='point_source'))
# OTOP_4_Path.append(optical_elements[96])
OTOP_4_Path.append(pyopt.OpticalElement(x_conv(1.5), y_conv(28.1), 'r', angle=0, element_type='point_source'))
OTOP_4.draw(table, OTOP_4_Path)

OTOP_5_Path.append(optical_elements[74])
OTOP_5_Path.append(black_aluminum_dump_1)
OTOP_5.draw(table, OTOP_5_Path)

OTOP_2_Path.append(pyopt.OpticalElement(x_conv(41), y_conv(28.1), 'r', angle=0, element_type='point_source'))
OTOP_2_Path.append(optical_elements[128])
OTOP_2.draw(table, OTOP_2_Path)


Dual_Color_1_Path.append(optical_elements[145])
# Dual_Color_1_Path.append(optical_elements[144])
Dual_Color_1_Path.append(optical_elements[142])
Dual_Color_1_Path.append(optical_elements[129])
Dual_Color_1_Path.append(optical_elements[131])
Dual_Color_1_Path.append(optical_elements[266])
Dual_Color_1_Path.append(optical_elements[135])
Dual_Color_1_Path.append(optical_elements[257])
Dual_Color_1.draw(table, Dual_Color_1_Path)

Dual_Color_2_Path.append(optical_elements[129])
Dual_Color_2_Path.append(optical_elements[72.2])
Dual_Color_2_Path.append(pyopt.OpticalElement(x_conv(43), y_conv(15), 't', angle=0, element_type='point_source'))
Dual_Color_2_Path.append(optical_elements[71])
Dual_Color_2.draw(table, Dual_Color_2_Path)


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
BFL_1_Path.append(pyopt.OpticalElement(x_conv(30.85), y_conv(28.5), 't', angle=0, element_type='point_source'))
BFL_1_Path.append(optical_elements[189])
BFL_1.draw(table, BFL_1_Path)

BFL_2_Path.append(optical_elements[134])
# BFL_2_Path.append(optical_elements[137])
BFL_2_Path.append(pyopt.OpticalElement(x_conv(30.85), y_conv(27.5), 't', angle=0, element_type='point_source'))
BFL_2_Path.append(optical_elements[190])
BFL_2.draw(table, BFL_2_Path)


Cs_H_Optical_Pump_Path.append(optical_elements[124])
Cs_H_Optical_Pump_Path.append(optical_elements[126])
Cs_H_Optical_Pump_Path.append(optical_elements[125])
Cs_H_Optical_Pump_Path.append(optical_elements[123])
Cs_H_Optical_Pump_Path.append(optical_elements[68])
Cs_H_Optical_Pump_Path.append(pyopt.OpticalElement(x_conv(24), y_conv(28), 't', angle=0, element_type='point_source'))
Cs_H_Optical_Pump.draw(table, Cs_H_Optical_Pump_Path)



file_path = "breadboard_optics.pdf"
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
