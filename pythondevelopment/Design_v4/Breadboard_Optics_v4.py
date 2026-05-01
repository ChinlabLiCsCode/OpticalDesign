import pyopticaltable as pyopt
import matplotlib.pyplot as plt
import pandas as pd
import os


# ---------------------------------------------------------------------------
# Table configuration
# ---------------------------------------------------------------------------

TABLE_LENGTH     = 50    # x dimension of optical table (internal coords)
TABLE_WIDTH      = 82    # y dimension of optical table (internal coords)
TABLE_ORIGIN_X   = 24   # physical x coordinate that maps to the table centre
TABLE_ORIGIN_Y   = 40   # physical y coordinate that maps to the table centre

CSV_PATH         = 'LiCs Optical Design - OpticsSetupBreadboard_v3.csv'
SHEET_ID         = '1mzK37AdseAbvQxTp3GW4Nsm7sQxGh-2In53QMjHEb7w'   # set to the Google Sheet ID to load from the web instead of CSV_PATH
OUTPUT_PATH      = 'breadboard_optics_v4.pdf'

LABEL_POSITION   = 'top'
LABEL_COLOR      = 'dodgerblue'

# Fiber-launcher box dimensions (used for all standard sources)
FIBER_SZ_X       = 1.55
FIBER_SZ_Y       = 2.0
LASER_FONT_SIZE  = 17

EDGE_WIDTH       = 7     # linewidth for zone-boundary lines

# ---------------------------------------------------------------------------
# Coordinate conversion helpers
# ---------------------------------------------------------------------------

def x_conv(x):
    """Convert physical x coordinate to table coordinate."""
    return x - TABLE_ORIGIN_X

def y_conv(y):
    """Convert physical y coordinate to table coordinate."""
    return y - TABLE_ORIGIN_Y

def minus_90_conv(angle_):
    return angle_ - 90

def plus_90_conv(angle_):
    return angle_ + 90


# ---------------------------------------------------------------------------
# Create the optical table
# ---------------------------------------------------------------------------

table = pyopt.OpticalTable(
    TABLE_LENGTH, TABLE_WIDTH,
    size_factor=20, show_edge=True, show_grid=True, grid_spacing=1
)
# Ratio used to scale optic sizes to keep them visually correct when the
# table is not square.  Derived automatically from the table dimensions.
descaling_factor = TABLE_LENGTH / TABLE_WIDTH


# ---------------------------------------------------------------------------
# Zone-boundary edges
# Each entry: (x_phys, y_phys, size_physical, angle_deg, colour)
# size_physical is in the same units as the physical coordinates; it is
# divided by descaling_factor internally (matching the original code).
# ---------------------------------------------------------------------------

ZONE_EDGES = [
    # Blue zone
    (13,    -0.5,  27, 0,   'blue'),
    (-0.5,  25,    51, 90,  'blue'),
    (26.5,  12.5,  26, 90,  'blue'),
    (23.5,  25.5,  6,  0,   'blue'),
    (20.5,  38,    25, 90,  'blue'),
    (10,    50.5,  21, 0,   'blue'),
    # Purple zone
    (38,    -0.5,  21, 0,   'purple'),
    (48.5,  40,    81, 90,  'purple'),
    (27.5,  25,    51, 90,  'purple'),
    (30.5,  50.5,  6,  0,   'purple'),
    (33.5,  58.5,  16, 90,  'purple'),
    (30.5,  66.5,  6,  0,   'purple'),
    (27.5,  73.5,  14, 90,  'purple'),
    (38,    80.5,  21, 0,   'purple'),
    # Red zone
    (36,    40.5,  24, 90,  'red'),
    (12,    40.5,  24, 90,  'red'),
    (24,    28.5,  24, 0,   'red'),
    (24,    52.5,  24, 0,   'red'),
]

for (xp, yp, sz, ang, col) in ZONE_EDGES:
    x1, x2, y1, y2 = table.angled_line(
        x=x_conv(xp), y=y_conv(yp),
        size=sz / descaling_factor,
        angle=ang, show=False, get_coords=True
    )
    table.ax.plot([x1, x2], [y1, y2], color=col, linewidth=EDGE_WIDTH)


# ---------------------------------------------------------------------------
# Load optics CSV
# ---------------------------------------------------------------------------

if SHEET_ID:
    _url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'
    df = pd.read_csv(_url)
    df = df[df['Setup Location'].str.strip() == 'Breadboard'].copy()
    df = df.dropna(subset=['O-number'])
    _num = df['O-number'].astype(str).str.replace(r'\.0$', '', regex=True)
    df['Label']      = _num.where(_num.str.startswith('O-'), 'O-' + _num)
    df['Position x'] = df['Position X']
    df['Position y'] = df['Position Y']
else:
    df = pd.read_csv(CSV_PATH)

# Displacement offsets - kept as named variables so they remain easy to tweak.
# Three groups (matching the original _2 / _3 suffixes) are preserved; set
# them all to zero to reproduce the original layout.
x_displacement   = 0
y_displacement   = 0
x_displacement_2 = 0
y_displacement_2 = 0
x_displacement_3 = 0
y_displacement_3 = 0

optical_elements = {}


# ---------------------------------------------------------------------------
# Laser-source definitions
# Each source is a row in SOURCE_DEFS with the fields needed to call
# table.box_source(), plus metadata for the LaserBeam objects.
#
# Columns (positional tuple)
# --------------------------
#   element_id  : key used in optical_elements dict
#   label       : text label drawn on the diagram
#   colour      : colour of all LaserBeam segments from this source
#   beam_width  : linewidth of the LaserBeam
#   x, y        : physical coordinates (before x_conv / y_conv)
#   angle       : box rotation angle in degrees
#   output_side : which side the beam exits
#   labelpad    : gap between box and label
#   dx_grp      : displacement group index for x (1, 2, or 3)
#   dy_grp      : displacement group index for y (1, 2, or 3)
#   n_paths     : how many separate LaserBeam path lists to initialise
#   size_x/y    : box dimensions (use FIBER_SZ_X/Y or custom values)
# ---------------------------------------------------------------------------

SOURCE_DEFS = [
    # id,   label,                      colour,           bw, x,    y,    ang,  side,    lpad, dxg, dyg, np, sx,         sy
    (37,  'O-37 Li H Imaging',          'magenta',         2, 4.5,  17.5, -45, 'right', 0.7,  3,   3,   2, FIBER_SZ_X, FIBER_SZ_Y),
    (27,  'O-27 Li EOM',                'magenta',         2, 4.0,  14.0,  45, 'right', 0.7,  3,   3,   2, FIBER_SZ_X, FIBER_SZ_Y),
    (15,  'O-15 Li Repump',             'lime',            2, 12.0, 12.0,  45, 'right', 0.7,  3,   3,   4, FIBER_SZ_X, FIBER_SZ_Y),
    (16,  'O-16 Li MOT',                'purple',          2, 9.5,  11.5,  45, 'right', 0.7,  3,   3,   4, FIBER_SZ_X, FIBER_SZ_Y),
    (17,  'O-17 Cs MOT',                'green',           2, 7.0,  11.0,  45, 'right', 0.7,  3,   3,   4, FIBER_SZ_X, FIBER_SZ_Y),
    (12,  'O-12 Cs H Imaging',          'cyan',            2, 4.0,  20.0, -45, 'right', 0.7,  3,   3,   2, FIBER_SZ_X, FIBER_SZ_Y),
    (25,  'O-25 Li Zeeman',             'red',             2, 21.0,  2.0,   0, 'right', 1.0,  3,   3,   1, FIBER_SZ_X, FIBER_SZ_Y),
    (48,  'O-48 Cs Zeeman',             'blue',            2, 17.0,  4.0,   0, 'right', 1.0,  3,   3,   1, FIBER_SZ_X, FIBER_SZ_Y),
    (110, 'O-110 RSC',                  'coral',           2, 14.0, 10.0,  45, 'right', 0.7,  1,   1,   4, FIBER_SZ_X, FIBER_SZ_Y),
    (116, 'O-116 Cs V Optical Pump',    'navy',            2, 11.5,  9.5,  45, 'right', 0.7,  1,   1,   4, FIBER_SZ_X, FIBER_SZ_Y),
    (127, 'O-127 Cs H Optical Pump',    'hotpink',         2, 36.0, 17.0,  90, 'right', 0.7,  1,   1,   1, FIBER_SZ_X, FIBER_SZ_Y),
    (267, 'O-267 OTOP',                 'crimson',         2, 32.0, 76.0,   0, 'right', 0.7,  2,   2,  10, 6.0,        3.5),
    (148, 'O-148 Dual Color',           'violet',          3, 36.0, 55.0,   0, 'right', 0.7,  1,   1,   3, FIBER_SZ_X, FIBER_SZ_Y),
    (150, 'O-150 BFL',                  'cornflowerblue',  2, 47.0, 79.0, -90, 'right', 0.7,  1,   1,   2, FIBER_SZ_X, FIBER_SZ_Y),
]

# Colour for each laser type — used when placing 'Fiber: ...' elements from the
# CSV and when assigning colours to sheet-driven beam paths.
LASER_COLORS = {
    'li h imaging':      'magenta',
    'li eom':            'magenta',
    'li repump':         'lime',
    'li mot':            'purple',
    'cs h imaging':      'cyan',
    'cs h img':          'cyan',
    'li zeeman':         'red',
    'cs zeeman':         'blue',
    'cs mot':            'green',
    'cs v optical pump': 'navy',
    'cs h optical pump': 'hotpink',
    'rsc':               'coral',
    'otop':              'crimson',
    'dual color':        'violet',
    'bfl':               'cornflowerblue',
}

# Map displacement-group number to runtime dx/dy values
_dx_map = {1: x_displacement, 2: x_displacement_2, 3: x_displacement_3}
_dy_map = {1: y_displacement, 2: y_displacement_2, 3: y_displacement_3}

# Containers populated below
laser_beams      = {}   # element_id -> list of LaserBeam objects
laser_beam_paths = {}   # element_id -> list of path lists

for (eid, lbl, col, bw, xp, yp, ang, side, lpad, dxg, dyg, n_paths, sx, sy) in SOURCE_DEFS:
    dx = _dx_map[dxg]
    dy = _dy_map[dyg]
    element = table.box_source(
        x=x_conv(xp + dx), y=y_conv(yp + dy),
        size_x=sx, size_y=sy,
        angle=ang, output_side=side,
        label=lbl, label_pos=LABEL_POSITION,
        labelpad=lpad, textcolour=LABEL_COLOR,
        fontsize=LASER_FONT_SIZE,
    )
    optical_elements[eid] = element

    beams = [pyopt.LaserBeam(colour=col, width=bw, style='-') for _ in range(n_paths)]
    paths = [[] for _ in range(n_paths)]
    laser_beams[eid]      = beams
    laser_beam_paths[eid] = paths

# Seed each source's first path with the source element itself
for eid, paths in laser_beam_paths.items():
    paths[0].append(optical_elements[eid])

# Convenience aliases so the beam-path section is identical to the original
Li_H_Imaging_1,  Li_H_Imaging_2  = laser_beams[37]
Li_H_Imaging_1_Path, Li_H_Imaging_2_Path = laser_beam_paths[37]

Li_EOM_1,  Li_EOM_2  = laser_beams[27]
Li_EOM_1_Path, Li_EOM_2_Path = laser_beam_paths[27]

Li_Repump_1, Li_Repump_2, Li_Repump_3, Li_Repump_4 = laser_beams[15]
Li_Repump_1_Path, Li_Repump_2_Path, Li_Repump_3_Path, Li_Repump_4_Path = laser_beam_paths[15]

Li_MOT_1, Li_MOT_2, Li_MOT_3, Li_MOT_4 = laser_beams[16]
Li_MOT_1_Path, Li_MOT_2_Path, Li_MOT_3_Path, Li_MOT_4_Path = laser_beam_paths[16]

Cs_MOT_1, Cs_MOT_2, Cs_MOT_3, Cs_MOT_4 = laser_beams[17]
Cs_MOT_1_Path, Cs_MOT_2_Path, Cs_MOT_3_Path, Cs_MOT_4_Path = laser_beam_paths[17]

Cs_H_Imaging_1, Cs_H_Imaging_2 = laser_beams[12]
Cs_H_Imaging_1_Path, Cs_H_Imaging_2_Path = laser_beam_paths[12]

Li_Zeeman,      = laser_beams[25]
Li_Zeeman_Path, = laser_beam_paths[25]

Cs_Zeeman,      = laser_beams[48]
Cs_Zeeman_Path, = laser_beam_paths[48]

RSC_1, RSC_2, RSC_3, RSC_4 = laser_beams[110]
RSC_1_Path, RSC_2_Path, RSC_3_Path, RSC_4_Path = laser_beam_paths[110]

Cs_V_Optical_Pump_1, Cs_V_Optical_Pump_2, Cs_V_Optical_Pump_3, Cs_V_Optical_Pump_4 = laser_beams[116]
Cs_V_Optical_Pump_1_Path, Cs_V_Optical_Pump_2_Path, Cs_V_Optical_Pump_3_Path, Cs_V_Optical_Pump_4_Path = laser_beam_paths[116]

Cs_H_Optical_Pump,  = laser_beams[127]
Cs_H_Optical_Pump_Path, = laser_beam_paths[127]

(OTOP_1, OTOP_2, OTOP_3, OTOP_4, OTOP_5,
 OTOP_6, OTOP_7, OTOP_8, OTOP_9, OTOP_10) = laser_beams[267]
(OTOP_1_Path, OTOP_2_Path, OTOP_3_Path, OTOP_4_Path, OTOP_5_Path,
 OTOP_6_Path, OTOP_7_Path, OTOP_8_Path, OTOP_9_Path, OTOP_10_Path) = laser_beam_paths[267]

Dual_Color_1, Dual_Color_2, Dual_Color_3 = laser_beams[148]
Dual_Color_1_Path, Dual_Color_2_Path, Dual_Color_3_Path = laser_beam_paths[148]

BFL_1, BFL_2 = laser_beams[150]
BFL_1_Path, BFL_2_Path = laser_beam_paths[150]


# ---------------------------------------------------------------------------
# Element-type -> drawing configuration
#
# Each key is a type string from the CSV.  The value is a dict with:
#   method      : OpticalTable method name to call
#   size        : the 'size' positional arg (None if the method uses size_x/y)
#   angle_conv  : function applied to the CSV angle before passing it in
#   extra       : additional keyword arguments
#   labelpad    : default label padding
#   label_pos_override : (optional) overrides LABEL_POSITION for this type
#
# Types that require custom multi-element logic (e.g. 'large post') are
# handled explicitly in the SPECIAL_ELEMENT_TYPES block inside the loop.
# ---------------------------------------------------------------------------

# Maps sheet type names that differ from the ELEMENT_CONFIG keys to their
# canonical equivalents.  Extend as the sheet evolves.
# All keys are lowercase — lookup is done with type_.lower() so capitalisation
# in the sheet never matters.
TYPE_ALIASES = {
    'eo2 mirror':                       'mirror',
    'eo3 mirror':                       'mirror',
    'silver mirror':                    'mirror',
    '1064 mirror':                      'mirror',
    '2 inch eo2 mirror':                'large mirror',
    'beam sampler':                     'beam sampler',
    'iris':                             'iris',
    'polarizing beam spliter (pbs122)': 'PBS',
    'flat lens-like pbs':               'PBS',
    '1/2 waveplate':                    'waveplate',
    'half waveplate':                   'waveplate',
    'hwp':                              'waveplate',
    '671 half waveplate':               'waveplate',
    '671 nm half waveplate':            'waveplate',
    '671 hwp':                          'waveplate',
    '850 half waveplate':               'waveplate',
    '852 half waveplate':               'waveplate',
    '852 hwp':                          'waveplate',
    '671 qwp':                          'waveplate',
    'quarter waveplate':                'waveplate',
    'convex rectangular lens':          'lens',
}


def _mirror_cfg(size, colour='k', labelpad=0.1):
    return dict(method='mirror', size=size, angle_conv=minus_90_conv,
                extra=dict(colour=colour), labelpad=labelpad)

def _box_cfg(sx, sy, linestyle='-', colour='k', labelpad=0.6):
    return dict(method='box', size=None, angle_conv=lambda a: a,
                extra=dict(size_x=sx, size_y=sy, linestyle=linestyle,
                           colour=colour, standalone=True),
                labelpad=labelpad)

def _waveplate_cfg(size):
    return dict(method='transmissive_plate', size=size,
                angle_conv=minus_90_conv,
                extra=dict(fill=True, fillcolour='c'),
                labelpad=0.05)

ELEMENT_CONFIG = {
    'mirror':                _mirror_cfg(1 / descaling_factor),
    'tall mirror':           _mirror_cfg(1 / descaling_factor),
    'periscope mirror':      _mirror_cfg(1 / descaling_factor),
    'large mirror':          _mirror_cfg(2 / descaling_factor, labelpad=0),
    'beam sampler':          _mirror_cfg(1 / descaling_factor, colour='teal'),
    'quadrant mirror':       _mirror_cfg(0.4 / descaling_factor),
    'small mirror':          _mirror_cfg(0.4 / descaling_factor),
    'dichroic mirror':       _mirror_cfg(2 / descaling_factor, colour='orange', labelpad=0),
    'small dichroic mirror': _mirror_cfg(0.5 / descaling_factor, colour='orange', labelpad=0),
    'dump':
        dict(method='beam_dump', size=0.6 / descaling_factor,
             angle_conv=minus_90_conv,
             extra=dict(colour='k', fillcolour='k'),
             labelpad=0.1),
    'water-cooled beam dump':
        dict(method='generic_circle', size=0.5,
             angle_conv=lambda a: a,
             extra=dict(colour='blue', fill=False, fillcolour='k'),
             labelpad=0.3, use_angle=False),
    'iris':                  _box_cfg(0.1, 1, linestyle='-.', labelpad=0.6),
    'PBS':
        dict(method='beamsplitter_cube', size=0.7 / descaling_factor,
             angle_conv=lambda a: a,
             extra=dict(direction='R'),
             labelpad=0.2),
    'large PBS':
        dict(method='beamsplitter_cube', size=1 / descaling_factor,
             angle_conv=lambda a: a,
             extra=dict(direction='R'),
             labelpad=0.2),
    'waveplate':             _waveplate_cfg(0.7 / descaling_factor),
    'tall waveplate':        _waveplate_cfg(0.7 / descaling_factor),
    'double waveplate':
        dict(method='box', size=None, angle_conv=lambda a: a,
             extra=dict(size_x=1.5, size_y=1.5, colour='c', standalone=True),
             labelpad=0.4),
    'lens':
        dict(method='convex_lens', size=1 / descaling_factor,
             angle_conv=plus_90_conv,
             extra={},
             labelpad=0),
    'PD':                    _box_cfg(1, 2, linestyle='--', labelpad=0.8),
    'small PD':              _box_cfg(1, 1, linestyle='--', labelpad=0.8),
    'chamber port':          _box_cfg(0.3, 2, labelpad=0.35),
    'post':
        dict(method='generic_circle', size=0.5,
             angle_conv=lambda a: a,
             extra=dict(colour='k', fill=False, fillcolour='k'),
             labelpad=0.35, use_angle=False),
    'AOM':                   _box_cfg(1, 2, linestyle='-.', colour='k', labelpad=0.6),
    '50-50 beam splitter':
        dict(method='mirror', size=0.5 / descaling_factor,
             angle_conv=minus_90_conv,
             extra={},
             label_pos_override='top',
             labelpad=0.1),
    'camera':                _box_cfg(1, 2, linestyle='-.', labelpad=0.6),
}


# ---------------------------------------------------------------------------
# Main CSV loop - place all optical elements
# ---------------------------------------------------------------------------

LOOP_LIMIT      = float('inf') if SHEET_ID else 340   # sheet is pre-filtered; local CSV stops at 340
ALREADY_PLACED  = 148   # elements below this were placed before this loop

for _, row in df.iterrows():
    label = str(row['Label']).strip()
    i = float(label.split('-')[1])

    if i == LOOP_LIMIT:
        break

    type_ = row['Type'].strip()
    try:
        x = x_conv(float(row['Position x']))
        y = y_conv(float(row['Position y']))
        angle = float(row['Orientation'])
    except Exception:
        x = y = angle = 0

    # ---- special multi-element type ----
    if type_ == 'large post':
        optical_elements[i] = table.generic_circle(
            x=x, y=y, size=0.75, colour='k', fill=False, fillcolour='k',
            label=label + ' ' + type_, label_pos=LABEL_POSITION,
            labelpad=0.35, textcolour=LABEL_COLOR)
        optical_elements[i + 0.1] = table.generic_circle(
            x=x, y=y, size=1.25, colour='k', fill=False, fillcolour='k',
            label=label + ' ' + type_ + 'base', label_pos=LABEL_POSITION,
            labelpad=0.5, textcolour=LABEL_COLOR)
        continue

    # ---- fiber launcher ----
    if type_.lower().startswith('fiber:'):
        laser_name = type_[type_.index(':') + 1:].strip().lower()
        optical_elements[i] = table.box_source(
            x=x, y=y,
            size_x=FIBER_SZ_X, size_y=FIBER_SZ_Y,
            angle=angle, output_side='right',
            label=label + ' ' + type_[type_.index(':') + 1:].strip(),
            label_pos=LABEL_POSITION, labelpad=0.7,
            textcolour=LABEL_COLOR, fontsize=LASER_FONT_SIZE,
        )
        continue

    type_ = TYPE_ALIASES.get(type_.lower(), type_)

    # ---- config-driven types ----
    cfg = ELEMENT_CONFIG.get(type_)
    if cfg is None:
        if i > ALREADY_PLACED:
            print(f"Skipping unknown element: {label} {type_}")
        continue

    method     = getattr(table, cfg['method'])
    angle_fn   = cfg['angle_conv']
    lpad       = cfg.get('labelpad', 0.1)
    lpos       = cfg.get('label_pos_override', LABEL_POSITION)
    extra      = cfg.get('extra', {})
    use_angle  = cfg.get('use_angle', True)
    full_label = label + ' ' + type_

    if cfg['size'] is not None:
        # Methods with a unified 'size' parameter (mirror, lens, beam_dump…)
        if use_angle:
            optical_elements[i] = method(
                x=x, y=y, size=cfg['size'], angle=angle_fn(angle),
                label=full_label, label_pos=lpos,
                labelpad=lpad, textcolour=LABEL_COLOR,
                **extra,
            )
        else:
            optical_elements[i] = method(
                x=x, y=y, size=cfg['size'],
                label=full_label, label_pos=lpos,
                labelpad=lpad, textcolour=LABEL_COLOR,
                **extra,
            )
    else:
        # Box-based methods where size_x/size_y live inside extra
        if use_angle:
            optical_elements[i] = method(
                x=x, y=y, angle=angle_fn(angle),
                label=full_label, label_pos=lpos,
                labelpad=lpad, textcolour=LABEL_COLOR,
                **extra,
            )
        else:
            optical_elements[i] = method(
                x=x, y=y,
                label=full_label, label_pos=lpos,
                labelpad=lpad, textcolour=LABEL_COLOR,
                **extra,
            )


# ---------------------------------------------------------------------------
# Special / override elements
# These either don't appear in the CSV or need parameters that can't be
# expressed generically. Collected here so they are easy to find and update.
# ---------------------------------------------------------------------------

optical_elements[31] = table.box(
    x=x_conv(47 + x_displacement), y=y_conv(51 + y_displacement),
    size_x=1, size_y=1.5, angle=minus_90_conv(90), standalone=True,
    label='O-31 lens tube', label_pos='right', labelpad=0.3, textcolour=LABEL_COLOR)

optical_elements[36] = table.box(
    x=x_conv(47 + x_displacement), y=y_conv(52 + y_displacement),
    size_x=1.5, size_y=0.1, angle=minus_90_conv(90), colour='orange', standalone=True,
    label='O-36 copper plate', label_pos='top', labelpad=0.2, textcolour=LABEL_COLOR)

optical_elements[73] = table.box(
    x=x_conv(47 + x_displacement), y=y_conv(59 + y_displacement),
    size_x=1, size_y=9, angle=minus_90_conv(90), standalone=True,
    label='O-73 lens tube', label_pos='right', labelpad=0.5, textcolour=LABEL_COLOR)

optical_elements[103] = table.box(
    x=x_conv(12 + x_displacement), y=y_conv(40.5 + y_displacement),
    size_x=1, size_y=2, angle=minus_90_conv(160), standalone=True,
    label='O-103 quadrant detector sensor head',
    label_pos=LABEL_POSITION, labelpad=0.5, textcolour=LABEL_COLOR)

optical_elements[134] = table.box(
    x=x_conv(44.5 + x_displacement), y=y_conv(35.4 + y_displacement),
    size_x=1, size_y=0.1, angle=minus_90_conv(-135), colour='b', standalone=True,
    label='O-134 flat PBS', label_pos=LABEL_POSITION, labelpad=0.4, textcolour=LABEL_COLOR)

optical_elements[137] = table.box(
    x=x_conv(32 + x_displacement), y=y_conv(36 + y_displacement),
    size_x=3.5, size_y=2, angle=0, standalone=True,
    label='O-137 3-hole tube', label_pos=LABEL_POSITION, labelpad=0.25, textcolour=LABEL_COLOR)

three_hole_tube_lens = table.convex_lens(
    x=x_conv(31 + x_displacement), y=y_conv(36 + y_displacement),
    size=2 / descaling_factor, angle=plus_90_conv(0), label='',
    label_pos=LABEL_POSITION, labelpad=0.07, textcolour=LABEL_COLOR)

optical_elements[138] = table.box(
    x=x_conv(47 + x_displacement), y=y_conv(73.75 + y_displacement),
    size_x=1, size_y=8, angle=minus_90_conv(90), standalone=True,
    label='O-138 lens tube', label_pos='right', labelpad=0.5, textcolour=LABEL_COLOR)

optical_elements[140] = table.convex_lens(
    x=x_conv(41 + x_displacement), y=y_conv(43 + y_displacement),
    size=0.75 / descaling_factor, angle=plus_90_conv(90),
    label='O-140 convex rectangular lens',
    label_pos=LABEL_POSITION, labelpad=0, textcolour=LABEL_COLOR)

optical_elements[143] = table.box(
    x=x_conv(45 + x_displacement), y=y_conv(43 + y_displacement),
    size_x=1, size_y=2, angle=minus_90_conv(90), standalone=True,
    label='O-143 lens tube', label_pos='right', labelpad=0.5, textcolour=LABEL_COLOR)

optical_elements[146] = table.convex_lens(
    x=x_conv(41 + x_displacement), y=y_conv(46 + y_displacement),
    size=1.5 / descaling_factor, angle=plus_90_conv(-90),
    label='O-146 convex rectangular lens',
    label_pos=LABEL_POSITION, labelpad=0, textcolour=LABEL_COLOR)

optical_elements[162] = table.box(
    x=x_conv(41.5 + x_displacement_2), y=y_conv(76 + y_displacement_2),
    size_x=1, size_y=5.5, angle=minus_90_conv(0), standalone=True,
    label='O-162 telescope lens tube', label_pos=LABEL_POSITION, labelpad=0.3, textcolour=LABEL_COLOR)

optical_elements[251] = table.box(
    x=x_conv(30 + x_displacement), y=y_conv(42 + y_displacement),
    size_x=0.7, size_y=6, angle=minus_90_conv(-135), standalone=True,
    label='O-251 waveplate & polarizer in front of camera',
    label_pos=LABEL_POSITION, labelpad=0.3, textcolour=LABEL_COLOR)

black_aluminum_dump_1 = table.beam_dump(
    x=x_conv(1 + x_displacement), y=y_conv(26 + y_displacement),
    size=0.5 / descaling_factor, angle=minus_90_conv(90),
    colour='k', fillcolour='k', label='black aluminum dump',
    label_pos=LABEL_POSITION, labelpad=0.1, textcolour=LABEL_COLOR)

center = table.generic_circle(
    x=x_conv(24 + x_displacement), y=y_conv(36 + y_displacement),
    size=0.5, colour='gold', fill=True, fillcolour='gold',
    label='center', label_pos=LABEL_POSITION, labelpad=0.3, textcolour=LABEL_COLOR)

lower_hole = table.generic_circle(
    x=x_conv(2), y=y_conv(7),
    size=0.5, colour='red', fill=False, fillcolour='k',
    label='hole', label_pos='top', labelpad=0.35, textcolour=LABEL_COLOR)

upper_hole = table.generic_circle(
    x=x_conv(2), y=y_conv(43),
    size=0.5, colour='red', fill=False, fillcolour='k',
    label='hole', label_pos='top', labelpad=0.35, textcolour=LABEL_COLOR)

empty_mount_1 = table.generic_circle(
    x=x_conv(12), y=y_conv(20),
    size=0.4, colour='k', fill=False, fillcolour='k',
    label='empty mount', label_pos='top', labelpad=0.35, textcolour=LABEL_COLOR)

empty_mount_2 = table.generic_circle(
    x=x_conv(13), y=y_conv(19),
    size=0.4, colour='k', fill=False, fillcolour='k',
    label='empty mount', label_pos='top', labelpad=0.35, textcolour=LABEL_COLOR)

empty_mount_3 = table.generic_circle(
    x=x_conv(14), y=y_conv(18),
    size=0.4, colour='k', fill=False, fillcolour='k',
    label='empty mount', label_pos='top', labelpad=0.35, textcolour=LABEL_COLOR)

empty_mount_4 = table.generic_circle(
    x=x_conv(15), y=y_conv(17),
    size=0.4, colour='k', fill=False, fillcolour='k',
    label='empty mount', label_pos='top', labelpad=0.35, textcolour=LABEL_COLOR)

ion_pump_pipe = table.generic_circle(
    x=x_conv(24), y=y_conv(28.5),
    size=2, colour='k', fill=False, fillcolour='k',
    label='ion pump pipe', label_pos='top', labelpad=0.35, textcolour=LABEL_COLOR)


# ---------------------------------------------------------------------------
# Beam paths  (unchanged from original - see future beam-path CSV refactor)
# ---------------------------------------------------------------------------

# Li_H_Imaging_1_Path.append(optical_elements[6])
# # Li_H_Imaging_1_Path.append(optical_elements[76.3])
# Li_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(16 - 0.05 + x_displacement_3), y_conv(22 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_H_Imaging_1_Path.append(optical_elements[60])
# Li_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(13 + x_displacement_3), y_conv(25 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_H_Imaging_1_Path.append(optical_elements[251])
# Li_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(30 + 2 + x_displacement_3), y_conv(42 + 2 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_H_Imaging_1.draw(table, Li_H_Imaging_1_Path)

# Li_H_Imaging_2_Path.append(optical_elements[305])
# Li_H_Imaging_2_Path.append(optical_elements[30])
# Li_H_Imaging_2_Path.append(optical_elements[325])
# Li_H_Imaging_2.draw(table, Li_H_Imaging_2_Path)

# Li_EOM_1_Path.append(optical_elements[38])
# # Li_EOM_1_Path.append(optical_elements[50])
# Li_EOM_1_Path.append(pyopt.OpticalElement(x_conv(9.9 - 0.1 + x_displacement_3), y_conv(15.63 + 0.02 + y_displacement_3), 't', angle=0, element_type='point_source'))
# # Li_EOM_1_Path.append(optical_elements[76.3])
# Li_EOM_1_Path.append(pyopt.OpticalElement(x_conv(16 - 0.05 + x_displacement_3), y_conv(22 - 0.15 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_EOM_1_Path.append(optical_elements[60])
# Li_EOM_1_Path.append(pyopt.OpticalElement(x_conv(13 + x_displacement_3), y_conv(25 - 0.2 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_EOM_1_Path.append(optical_elements[251])
# Li_EOM_1_Path.append(pyopt.OpticalElement(x_conv(30 + 2 + x_displacement_3), y_conv(42 + 2 - 0.2 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_EOM_1.draw(table, Li_EOM_1_Path)

# # Li_EOM_2_Path.append(optical_elements[305])
# Li_EOM_2_Path.append(pyopt.OpticalElement(x_conv(12 + x_displacement_3), y_conv(18 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_EOM_2_Path.append(optical_elements[30])
# Li_EOM_2_Path.append(pyopt.OpticalElement(x_conv(8.5 - 0.1 + x_displacement_3), y_conv(21.5 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_EOM_2_Path.append(optical_elements[325])
# Li_EOM_2_Path.append(pyopt.OpticalElement(x_conv(7 - 0.05 + x_displacement_3), y_conv(20 + 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_EOM_2.draw(table, Li_EOM_2_Path)

# Li_Repump_1_Path.append(optical_elements[307])
# # Li_Repump_1_Path.append(optical_elements[63])
# Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(15 - 0.05 + x_displacement_3), y_conv(15 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_Repump_1_Path.append(optical_elements[40])
# Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(14 + x_displacement_3), y_conv(16 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_Repump_1_Path.append(optical_elements[185])
# Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(19.8 + 0.05 + x_displacement_3), y_conv(21.8 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_Repump_1_Path.append(optical_elements[13])
# Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(19.6 + 0.2 + 0.05 + x_displacement), y_conv(7 + 0.2 + 0.05 + y_displacement), 'r', angle=0, element_type='point_source'))
# # Li_Repump_1_Path.append(optical_elements[250])
# Li_Repump_1_Path.append(pyopt.OpticalElement(x_conv(2 + x_displacement), y_conv(7 + 0.05 + y_displacement), 'r', angle=0, element_type='point_source'))
# Li_Repump_1.draw(table, Li_Repump_1_Path)

# # Li_Repump_2_Path.append(optical_elements[78.2])
# Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(18 + x_displacement_3), y_conv(20 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_Repump_2_Path.append(optical_elements[76.3])
# Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(16 + x_displacement_3), y_conv(22 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_Repump_2_Path.append(optical_elements[91])
# Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(19 + 0.05 + x_displacement_3), y_conv(25 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_Repump_2_Path.append(optical_elements[87])
# Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(29 + 0.05 + x_displacement_3), y_conv(15 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_Repump_2_Path.append(optical_elements[107])
# Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(37 + x_displacement_3), y_conv(23 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_Repump_2_Path.append(optical_elements[70])
# Li_Repump_2_Path.append(pyopt.OpticalElement(x_conv(14 + x_displacement_3), y_conv(46 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_2.draw(table, Li_Repump_2_Path)

# # Li_Repump_3_Path.append(optical_elements[76.3])
# Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(16 + x_displacement_3), y_conv(22 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_Repump_3_Path.append(optical_elements[60])
# Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(13 + x_displacement_3), y_conv(25 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Li_Repump_3_Path.append(optical_elements[251])
# Li_Repump_3_Path.append(pyopt.OpticalElement(x_conv(30 + 2 + x_displacement_3), y_conv(42 + 2 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Repump_3.draw(table, Li_Repump_3_Path)

# Li_Repump_4_Path.append(optical_elements[307])
# Li_Repump_4_Path.append(optical_elements[90])
# Li_Repump_4_Path.append(optical_elements[84])
# Li_Repump_4.draw(table, Li_Repump_4_Path)


# Li_MOT_1_Path.append(optical_elements[320])
# Li_MOT_1_Path.append(optical_elements[40])
# # Li_MOT_1_Path.append(optical_elements[78.1])
# Li_MOT_1_Path.append(optical_elements[78.2])
# # Li_MOT_1_Path.append(optical_elements[78.3])
# Li_MOT_1_Path.append(optical_elements[185])
# # Li_MOT_1_Path.append(optical_elements[13])
# Li_MOT_1_Path.append(pyopt.OpticalElement(x_conv(19.6 + 0.2 + x_displacement), y_conv(7 + 0.2 + y_displacement), 'r', angle=0, element_type='point_source'))
# Li_MOT_1_Path.append(optical_elements[250])
# Li_MOT_1.draw(table, Li_MOT_1_Path)

# Li_MOT_2_Path.append(optical_elements[320])
# Li_MOT_2_Path.append(optical_elements[105])
# Li_MOT_2_Path.append(optical_elements[313])
# Li_MOT_2.draw(table, Li_MOT_2_Path)

# Li_MOT_3_Path.append(optical_elements[78.2])
# # Li_MOT_3_Path.append(optical_elements[65])
# Li_MOT_3_Path.append(optical_elements[76.3])
# # Li_MOT_3_Path.append(optical_elements[76.2])
# # Li_MOT_3_Path.append(optical_elements[76.1])
# # Li_MOT_3_Path.append(optical_elements[83])
# Li_MOT_3_Path.append(optical_elements[91])
# # Li_MOT_3_Path.append(optical_elements[186])
# # Li_MOT_3_Path.append(optical_elements[106])
# Li_MOT_3_Path.append(optical_elements[87])
# Li_MOT_3_Path.append(optical_elements[107])
# Li_MOT_3_Path.append(optical_elements[69])
# Li_MOT_3_Path.append(optical_elements[70])
# Li_MOT_3.draw(table, Li_MOT_3_Path)

# Li_MOT_4_Path.append(optical_elements[76.3])
# Li_MOT_4_Path.append(optical_elements[60])
# Li_MOT_4_Path.append(optical_elements[251])
# Li_MOT_4.draw(table, Li_MOT_4_Path)

# Cs_MOT_1_Path.append(optical_elements[98])
# # Cs_MOT_1_Path.append(optical_elements[13])
# Cs_MOT_1_Path.append(pyopt.OpticalElement(x_conv(19.6 - 0.1 + x_displacement_3), y_conv(7 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Cs_MOT_1_Path.append(optical_elements[250])
# Cs_MOT_1.draw(table, Cs_MOT_1_Path)

# Cs_MOT_2_Path.append(optical_elements[79.1])
# Cs_MOT_2_Path.append(optical_elements[34])
# # Cs_MOT_2_Path.append(optical_elements[251])
# Cs_MOT_2_Path.append(pyopt.OpticalElement(x_conv(30 - 0.05 + x_displacement_3), y_conv(42 + 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Cs_MOT_2.draw(table, Cs_MOT_2_Path)

# Cs_MOT_3_Path.append(optical_elements[64.1])
# Cs_MOT_3_Path.append(optical_elements[93])
# # Cs_MOT_3_Path.append(optical_elements[87])
# Cs_MOT_3_Path.append(pyopt.OpticalElement(x_conv(29 + 0.1 + x_displacement_3), y_conv(15 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Cs_MOT_3_Path.append(optical_elements[107])
# Cs_MOT_3_Path.append(pyopt.OpticalElement(x_conv(37 + x_displacement_3), y_conv(23 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# # Cs_MOT_3_Path.append(optical_elements[70])
# Cs_MOT_3_Path.append(pyopt.OpticalElement(x_conv(14 + x_displacement_3), y_conv(46 - 0.1 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Cs_MOT_3.draw(table, Cs_MOT_3_Path)

# Cs_MOT_4_Path.append(optical_elements[306])
# Cs_MOT_4_Path.append(optical_elements[104])
# Cs_MOT_4_Path.append(optical_elements[315])
# Cs_MOT_4.draw(table, Cs_MOT_4_Path)

# Cs_H_Imaging_1_Path.append(optical_elements[4])
# # Cs_H_Imaging_1_Path.append(optical_elements[64.1])
# Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(13 + x_displacement_3), y_conv(21 - 0.05 + y_displacement_3), 't', angle=0, element_type='point_source'))
# # Cs_H_Imaging_1_Path.append(optical_elements[34])
# Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(10.95 + x_displacement_3), y_conv(23.05 - 0.05 + y_displacement_3), 't', angle=0, element_type='point_source'))
# # Cs_H_Imaging_1_Path.append(optical_elements[251])
# Cs_H_Imaging_1_Path.append(pyopt.OpticalElement(x_conv(30 + 2 - 0.05 + x_displacement_3), y_conv(42 + 2 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Cs_H_Imaging_1.draw(table, Cs_H_Imaging_1_Path)

# Cs_H_Imaging_2_Path.append(optical_elements[304])
# Cs_H_Imaging_2_Path.append(optical_elements[82])
# Cs_H_Imaging_2_Path.append(optical_elements[314])
# Cs_H_Imaging_2.draw(table, Cs_H_Imaging_2_Path)

# # Li_Zeeman_Path.append(optical_elements[21])
# Li_Zeeman_Path.append(optical_elements[23])
# # Li_Zeeman_Path.append(optical_elements[328])
# # Li_Zeeman_Path.append(optical_elements[24])
# Li_Zeeman_Path.append(optical_elements[2])
# Li_Zeeman_Path.append(optical_elements[22])
# Li_Zeeman_Path.append(optical_elements[20])
# Li_Zeeman_Path.append(optical_elements[19])
# # Li_Zeeman_Path.append(optical_elements[58])
# Li_Zeeman_Path.append(pyopt.OpticalElement(x_conv(24 + 0.1 + x_displacement_3), y_conv(16 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Zeeman_Path.append(pyopt.OpticalElement(x_conv(24 + 0.1 + x_displacement_3), y_conv(45 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Li_Zeeman.draw(table, Li_Zeeman_Path)

# # Cs_Zeeman_Path.append(optical_elements[44])
# Cs_Zeeman_Path.append(optical_elements[47])
# # Cs_Zeeman_Path.append(optical_elements[327])
# # Cs_Zeeman_Path.append(optical_elements[45])
# Cs_Zeeman_Path.append(optical_elements[3])
# Cs_Zeeman_Path.append(optical_elements[46])
# Cs_Zeeman_Path.append(optical_elements[43])
# Cs_Zeeman_Path.append(optical_elements[67])
# Cs_Zeeman_Path.append(optical_elements[35])
# Cs_Zeeman_Path.append(optical_elements[58])
# Cs_Zeeman_Path.append(pyopt.OpticalElement(x_conv(24 + x_displacement_3), y_conv(45 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Cs_Zeeman.draw(table, Cs_Zeeman_Path)

# RSC_1_Path.append(optical_elements[95])
# RSC_1_Path.append(optical_elements[149])
# RSC_1_Path.append(optical_elements[120])
# RSC_1_Path.append(optical_elements[5])
# RSC_1.draw(table, RSC_1_Path)

# RSC_2_Path.append(optical_elements[298])
# RSC_2_Path.append(optical_elements[121])
# RSC_2_Path.append(optical_elements[288])
# RSC_2.draw(table, RSC_2_Path)

# RSC_3_Path.append(optical_elements[114.1])
# RSC_3_Path.append(optical_elements[99])
# RSC_3_Path.append(optical_elements[109])
# RSC_3_Path.append(optical_elements[188])
# RSC_3_Path.append(optical_elements[250])
# RSC_3.draw(table, RSC_3_Path)

# RSC_4_Path.append(optical_elements[322])
# RSC_4_Path.append(optical_elements[308])
# RSC_4_Path.append(optical_elements[323])
# RSC_4.draw(table, RSC_4_Path)

# Cs_V_Optical_Pump_1_Path.append(optical_elements[119])
# # Cs_V_Optical_Pump_1_Path.append(optical_elements[114.1])
# Cs_V_Optical_Pump_1_Path.append(pyopt.OpticalElement(x_conv(21.3 - 0.05 + x_displacement), y_conv(17.3 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_1_Path.append(optical_elements[298])
# Cs_V_Optical_Pump_1_Path.append(pyopt.OpticalElement(x_conv(22.5 + x_displacement), y_conv(18.5 + 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_1_Path.append(optical_elements[121])
# Cs_V_Optical_Pump_1_Path.append(pyopt.OpticalElement(x_conv(15.5 + x_displacement), y_conv(25.5 + 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_1_Path.append(optical_elements[288])
# Cs_V_Optical_Pump_1_Path.append(pyopt.OpticalElement(x_conv(31 - 0.05 + x_displacement), y_conv(45 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_1.draw(table, Cs_V_Optical_Pump_1_Path)

# # Cs_V_Optical_Pump_2_Path.append(optical_elements[114.1])
# Cs_V_Optical_Pump_2_Path.append(pyopt.OpticalElement(x_conv(21.3 - 0.05 + x_displacement), y_conv(17.3 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_2_Path.append(optical_elements[99])
# Cs_V_Optical_Pump_2_Path.append(pyopt.OpticalElement(x_conv(22.3 + x_displacement), y_conv(16.3 - 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_2_Path.append(optical_elements[109])
# Cs_V_Optical_Pump_2_Path.append(pyopt.OpticalElement(x_conv(14 + x_displacement), y_conv(8 - 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_2_Path.append(optical_elements[188])
# Cs_V_Optical_Pump_2_Path.append(pyopt.OpticalElement(x_conv(15.4 + x_displacement), y_conv(6.6 - 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_2_Path.append(optical_elements[250])
# Cs_V_Optical_Pump_2_Path.append(pyopt.OpticalElement(x_conv(2 + x_displacement_3), y_conv(7 - 0.05 + y_displacement_3), 'r', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_2.draw(table, Cs_V_Optical_Pump_2_Path)

# Cs_V_Optical_Pump_3_Path.append(optical_elements[321])
# Cs_V_Optical_Pump_3_Path.append(optical_elements[309])
# Cs_V_Optical_Pump_3_Path.append(optical_elements[324])
# Cs_V_Optical_Pump_3.draw(table, Cs_V_Optical_Pump_3_Path)

# # Cs_V_Optical_Pump_4_Path.append(optical_elements[298])
# Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(22.5 + x_displacement), y_conv(18.5 + 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_4_Path.append(optical_elements[95])
# Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(26 - 0.05 + x_displacement), y_conv(22 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_4_Path.append(optical_elements[149])
# Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(30 - 0.05 + x_displacement), y_conv(18 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_4_Path.append(optical_elements[120])
# Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(37 + x_displacement), y_conv(24.5 + 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# # Cs_V_Optical_Pump_4_Path.append(optical_elements[5])
# Cs_V_Optical_Pump_4_Path.append(pyopt.OpticalElement(x_conv(13.3 + x_displacement), y_conv(45.3 + 0.05 + y_displacement), 't', angle=0, element_type='point_source'))
# Cs_V_Optical_Pump_4.draw(table, Cs_V_Optical_Pump_4_Path)

# OTOP_1_Path.append(optical_elements[167])
# OTOP_1_Path.append(optical_elements[162])
# OTOP_1_Path.append(optical_elements[163])
# OTOP_1_Path.append(optical_elements[151])
# OTOP_1_Path.append(optical_elements[151])
# OTOP_1_Path.append(optical_elements[152])
# OTOP_1_Path.append(optical_elements[153])
# # OTOP_1_Path.append(optical_elements[154])
# OTOP_1_Path.append(optical_elements[158])
# OTOP_1_Path.append(optical_elements[273])
# OTOP_1_Path.append(optical_elements[274])
# # OTOP_1_Path.append(optical_elements[135])
# OTOP_1_Path.append(pyopt.OpticalElement(x_conv(41 + x_displacement), y_conv(36.1 + y_displacement), 'r', angle=0, element_type='point_source'))
# # OTOP_1_Path.append(optical_elements[136])
# # OTOP_1_Path.append(optical_elements[137])
# # OTOP_1_Path.append(optical_elements[94.5])
# OTOP_1_Path.append(pyopt.OpticalElement(x_conv(28 + x_displacement), y_conv(36.1 + y_displacement), 't', angle=0, element_type='point_source'))
# # OTOP_1_Path.append(optical_elements[257])
# OTOP_1_Path.append(pyopt.OpticalElement(x_conv(13 + x_displacement), y_conv(36.1 + y_displacement), 'r', angle=0, element_type='point_source'))
# OTOP_1_Path.append(optical_elements[97])
# # OTOP_1_Path.append(optical_elements[92])
# OTOP_1_Path.append(optical_elements[86])
# OTOP_1_Path.append(optical_elements[85])
# OTOP_1_Path.append(optical_elements[80])
# OTOP_1_Path.append(optical_elements[81])
# OTOP_1_Path.append(optical_elements[89])
# OTOP_1.draw(table, OTOP_1_Path)

# OTOP_2_Path.append(pyopt.OpticalElement(x_conv(41 + x_displacement), y_conv(36.1 + y_displacement), 'r', angle=0, element_type='point_source'))
# OTOP_2_Path.append(optical_elements[128])
# OTOP_2.draw(table, OTOP_2_Path)

# OTOP_3_Path.append(optical_elements[80])
# OTOP_3_Path.append(optical_elements[74])
# OTOP_3_Path.append(optical_elements[75])
# OTOP_3.draw(table, OTOP_3_Path)

# # OTOP_4_Path.append(optical_elements[97])
# OTOP_4_Path.append(pyopt.OpticalElement(x_conv(5 + x_displacement), y_conv(36.1 + y_displacement), 't', angle=0, element_type='point_source'))
# # OTOP_4_Path.append(optical_elements[96])
# OTOP_4_Path.append(pyopt.OpticalElement(x_conv(1.5 + x_displacement), y_conv(36.1 + y_displacement), 'r', angle=0, element_type='point_source'))
# OTOP_4.draw(table, OTOP_4_Path)

# OTOP_5_Path.append(optical_elements[74])
# OTOP_5_Path.append(black_aluminum_dump_1)
# OTOP_5.draw(table, OTOP_5_Path)

# OTOP_6_Path.append(optical_elements[153])
# OTOP_6_Path.append(optical_elements[156])
# OTOP_6_Path.append(optical_elements[159])
# OTOP_6_Path.append(optical_elements[155])
# OTOP_6_Path.append(optical_elements[269])
# OTOP_6_Path.append(optical_elements[270])
# OTOP_6.draw(table, OTOP_6_Path)

# OTOP_7_Path.append(optical_elements[167])
# OTOP_7_Path.append(optical_elements[160])
# OTOP_7_Path.append(optical_elements[165])
# OTOP_7_Path.append(optical_elements[164])
# OTOP_7_Path.append(optical_elements[268])
# OTOP_7.draw(table, OTOP_7_Path)

# OTOP_8_Path.append(optical_elements[165])
# OTOP_8_Path.append(pyopt.OpticalElement(x_conv(41 + x_displacement_2), y_conv(80 + y_displacement_2), 't', angle=0, element_type='point_source'))
# OTOP_8.draw(table, OTOP_8_Path)

# # OTOP_9_Path.append(optical_elements[257])
# OTOP_9_Path.append(pyopt.OpticalElement(x_conv(13 + 0.1), y_conv(36 + 0.1), 'r', angle=0, element_type='point_source'))
# # OTOP_9_Path.append(optical_elements[258])
# OTOP_9_Path.append(pyopt.OpticalElement(x_conv(13 + 0.1), y_conv(28 + 0.1), 'r', angle=0, element_type='point_source'))
# # OTOP_9_Path.append(optical_elements[262])
# OTOP_9_Path.append(pyopt.OpticalElement(x_conv(11 - 0.1), y_conv(28 + 0.1), 'r', angle=0, element_type='point_source'))
# # OTOP_9_Path.append(optical_elements[263])
# OTOP_9_Path.append(pyopt.OpticalElement(x_conv(11 - 0.1), y_conv(31), 't', angle=0, element_type='point_source'))
# OTOP_9.draw(table, OTOP_9_Path)

# # OTOP_10_Path.append(optical_elements[262])
# OTOP_10_Path.append(pyopt.OpticalElement(x_conv(11 - 0.1), y_conv(28 + 0.1), 't', angle=0, element_type='point_source'))
# # OTOP_10_Path.append(optical_elements[260])
# OTOP_10_Path.append(pyopt.OpticalElement(x_conv(10), y_conv(28 + 0.1), 'r', angle=0, element_type='point_source'))
# OTOP_10.draw(table, OTOP_10_Path)

# Dual_Color_1_Path.append(optical_elements[129])
# Dual_Color_1_Path.append(optical_elements[145])
# # Dual_Color_1_Path.append(optical_elements[144])
# Dual_Color_1_Path.append(optical_elements[142])
# Dual_Color_1_Path.append(optical_elements[266])
# Dual_Color_1_Path.append(optical_elements[135])
# Dual_Color_1_Path.append(optical_elements[257])
# Dual_Color_1_Path.append(optical_elements[258])
# # Dual_Color_1_Path.append(optical_elements[259])
# Dual_Color_1_Path.append(optical_elements[262])
# Dual_Color_1_Path.append(optical_elements[263])
# Dual_Color_1.draw(table, Dual_Color_1_Path)

# Dual_Color_2_Path.append(optical_elements[129])
# Dual_Color_2_Path.append(optical_elements[71])
# Dual_Color_2.draw(table, Dual_Color_2_Path)

# Dual_Color_3_Path.append(optical_elements[262])
# Dual_Color_3_Path.append(optical_elements[260])
# Dual_Color_3.draw(table, Dual_Color_3_Path)


# # BFL_1_Path.append(optical_elements[141])
# BFL_1_Path.append(optical_elements[138])
# # BFL_1_Path.append(optical_elements[133])
# # BFL_1_Path.append(optical_elements[130])
# # BFL_1_Path.append(optical_elements[73])
# # BFL_1_Path.append(optical_elements[49])
# # BFL_1_Path.append(optical_elements[31])
# # BFL_1_Path.append(optical_elements[26])
# BFL_1_Path.append(optical_elements[11])
# BFL_1_Path.append(optical_elements[7])
# BFL_1_Path.append(optical_elements[122])
# BFL_1_Path.append(optical_elements[134])
# BFL_1_Path.append(optical_elements[139])
# # BFL_1_Path.append(optical_elements[137])
# BFL_1_Path.append(pyopt.OpticalElement(x_conv(30.88 + x_displacement), y_conv(36.6 + y_displacement), 't', angle=0, element_type='point_source'))
# BFL_1_Path.append(optical_elements[189])
# BFL_1.draw(table, BFL_1_Path)

# BFL_2_Path.append(optical_elements[134])
# # BFL_2_Path.append(optical_elements[137])
# BFL_2_Path.append(pyopt.OpticalElement(x_conv(30.88 + x_displacement), y_conv(35.4 + y_displacement), 't', angle=0, element_type='point_source'))
# BFL_2_Path.append(optical_elements[190])
# BFL_2.draw(table, BFL_2_Path)


# Cs_H_Optical_Pump_Path.append(optical_elements[124])
# Cs_H_Optical_Pump_Path.append(optical_elements[126])
# Cs_H_Optical_Pump_Path.append(optical_elements[123])
# Cs_H_Optical_Pump_Path.append(optical_elements[9])
# Cs_H_Optical_Pump_Path.append(optical_elements[68])
# Cs_H_Optical_Pump_Path.append(optical_elements[41])
# Cs_H_Optical_Pump.draw(table, Cs_H_Optical_Pump_Path)


# ---------------------------------------------------------------------------
# Sheet-driven beam paths
# Each column in the 'Beam Paths' sheet is one named beam path.
# A '-' cell ends the current segment and starts a new one (same colour).
# ---------------------------------------------------------------------------

if SHEET_ID:
    _bp_url = (f'https://docs.google.com/spreadsheets/d/{SHEET_ID}'
               f'/gviz/tq?tqx=out:csv&sheet=Beam+Paths')
    bp_df = pd.read_csv(_bp_url)

    for col in bp_df.columns:
        if col.startswith('Unnamed'):
            continue
        color = LASER_COLORS.get(col.lower(), 'gray')
        current_path = []

        for val in bp_df[col]:
            if pd.isna(val):
                break
            val = str(val).strip()
            if val == '-':
                if current_path:
                    pyopt.LaserBeam(colour=color, width=2, style='-').draw(table, current_path)
                    current_path = []
            else:
                try:
                    elem_id = float(val.split('-')[1])
                    current_path.append(optical_elements[elem_id])
                except KeyError:
                    print(f"Warning: {val} not placed — skipping in beam path '{col}'")
                except (IndexError, ValueError):
                    print(f"Warning: could not parse element ID from '{val}' in beam path '{col}'")

        if current_path:
            pyopt.LaserBeam(colour=color, width=2, style='-').draw(table, current_path)


# ---------------------------------------------------------------------------
# Save output
# ---------------------------------------------------------------------------

try:
    os.remove(OUTPUT_PATH)
    print(f"Removed existing file: {OUTPUT_PATH}")
except FileNotFoundError:
    pass

plt.savefig(OUTPUT_PATH, dpi=100, bbox_inches="tight", facecolor="white", transparent=False)
print(f"Saved: {OUTPUT_PATH}")

# plt.show()
