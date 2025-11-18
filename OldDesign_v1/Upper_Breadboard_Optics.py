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

x1_15, x2_15, y1_15, y2_15 = table.angled_line(x=x_conv(11), y=y_conv(32), size=5.5/(50/44), angle=0, show=False, get_coords=True)
table.ax.plot([x1_15, x2_15], [y1_15, y2_15], color='k', linewidth=edge_width)

x1_16, x2_16, y1_16, y2_16 = table.angled_line(x=x_conv(11), y=y_conv(25.5), size=5.5/(50/44), angle=0, show=False, get_coords=True)
table.ax.plot([x1_16, x2_16], [y1_16, y2_16], color='k', linewidth=edge_width)

x1_17, x2_17, y1_17, y2_17 = table.angled_line(x=x_conv(8.25), y=y_conv(28.75), size=6.5/(50/44), angle=90, show=False, get_coords=True)
table.ax.plot([x1_17, x2_17], [y1_17, y2_17], color='k', linewidth=edge_width)

x1_18, x2_18, y1_18, y2_18 = table.angled_line(x=x_conv(13.75), y=y_conv(28.75), size=6.5/(50/44), angle=90, show=False, get_coords=True)
table.ax.plot([x1_18, x2_18], [y1_18, y2_18], color='k', linewidth=edge_width)

df = pd.read_csv('OpticsSetup(Breadboard).csv')


label_position = 'top'
label_color = 'dodgerblue'
laser_box_size_x = 0.5
laser_box_size_y = 1
laser_label_font_size = 20
optical_elements = {}


# Define laser beams

Dual_Color_1 = pyopt.LaserBeam(colour='violet', width=2, style='-')
Dual_Color_1_Path = []
Dual_Color_2 = pyopt.LaserBeam(colour='violet', width=2, style='-')
Dual_Color_2_Path = []
Dual_Color_1_Path.append(table.point_source(x=x_conv(13), y=y_conv(28), label='Dual Color', label_pos=label_position, labelpad=0.8, textcolour=label_color, fontsize=laser_label_font_size))

OTOP_1 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_1_Path = []
OTOP_6 = pyopt.LaserBeam(colour='crimson', width=2, style='-')
OTOP_6_Path = []
OTOP_1_Path.append(table.point_source(x=x_conv(13), y=y_conv(28.1), label='OTOP', label_pos=label_position, labelpad=1.3, textcolour=label_color, fontsize=laser_label_font_size))



for _, row in df.iterrows():

    limit = 305
    done = 150

    label = row['Label'].strip()
    i = float(label.split('-')[1])

    if i > limit:
        break
    if i not in (258, 259, 260, 261, 262, 263, 270, 277, 278, 300, 301, 302):
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

    if type_ in 'mirror' or type_ == 'quadrant mirror' or type_ == 'periscope mirror':
        optical_elements[i] = table.mirror(x=x, y=y, size=0.4, angle=minus_90_conv(angle), label=label+' '+type_,
                                           label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'dichroic mirror':
        optical_elements[i] = table.mirror(x=x, y=y, size=1, angle=minus_90_conv(angle), colour='orange', label=label + ' ' + type_,
                                           label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'dump':
        optical_elements[i] = table.beam_dump(x=x, y=y, size=0.4, angle=minus_90_conv(angle), colour='k', fillcolour='k', label=label+' '+type_,
                                              label_pos=label_position, labelpad=0.1, textcolour=label_color)
    elif type_ == 'water-cooled beam dump':
        optical_elements[i] = table.generic_circle(x=x, y=y, size=0.4, colour='blue', fill=False, fillcolour='k', label=label+' '+type_,
                                                   label_pos=label_position, labelpad=0.25, textcolour=label_color)
    elif type_ == 'iris':
        optical_elements[i] = table.box(x=x, y=y, size_x=0.1, size_y=0.5, angle=angle, linestyle='-.', standalone=True, label=label+' '+type_,
                                        label_pos=label_position, labelpad=0.3, textcolour=label_color)
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

optical_elements[277] = table.box(x=x_conv(1.5), y=y_conv(28), size_x=0.5, size_y=1, angle=0, linestyle='-.', standalone=True, label='O-277 camera',
                                 label_pos=label_position, labelpad=0.5, textcolour=label_color)
center = table.generic_circle(x=x_conv(24), y=y_conv(28), size=0.5, colour='gold', fill=True, fillcolour='gold', label='center',
                                        label_pos=label_position, labelpad=0.3, textcolour=label_color)

Dual_Color_1_Path.append(optical_elements[259])
Dual_Color_1_Path.append(optical_elements[262])
Dual_Color_1_Path.append(optical_elements[260])
Dual_Color_1.draw(table, Dual_Color_1_Path)

Dual_Color_2_Path.append(optical_elements[262])
Dual_Color_2_Path.append(optical_elements[263])
Dual_Color_2.draw(table, Dual_Color_2_Path)


# OTOP_1_Path.append(optical_elements[260])
OTOP_1_Path.append(pyopt.OpticalElement(x_conv(10), y_conv(28.1), 't', angle=0, element_type='point_source'))
OTOP_1.draw(table, OTOP_1_Path)

# OTOP_6_Path.append(optical_elements[262])
OTOP_6_Path.append(pyopt.OpticalElement(x_conv(10.9), y_conv(28.1), 'r', angle=0, element_type='point_source'))
# OTOP_6_Path.append(optical_elements[263])
OTOP_6_Path.append(pyopt.OpticalElement(x_conv(10.9), y_conv(31), 't', angle=0, element_type='point_source'))
OTOP_6.draw(table, OTOP_6_Path)



file_path = "upper_breadboard_optics.pdf"
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
