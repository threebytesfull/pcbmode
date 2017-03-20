#!/usr/bin/python

from math import pi, sin, cos, sqrt, ceil
import re
from lxml import etree as et

import pcbmode.config as config

# import pcbmode modules
from . import utils
from .point import Point
from .svg_grammar import SvgGrammar
from .svgpath import SvgPath
from .path_utils import boundary_box_check, calculate_points_of_quadratic_bezier, calculate_points_of_cubic_bezier



def absolute_to_relative_path(path):
    """
    Converts an SVG path into a path that has only relative commands.
    This basically allows taking paths from anywhere and placing them
    in a new SVG.
    """
    # TODO: add support all commands
    # TODO: optimise 'switch' logic

    # check to see if path is empty or doesn't exist
    if (path == None) or (path == ''):
        return

    return SvgPath(path).getRelative()



def calculate_bounding_box_of_path(path):
    """
    Calculates the bounding box of an SVG path
    """

    svg_path = SvgPath(path)
    w, h = svg_path._getDimensions() # TODO: force calculation but avoid private interface
    bbox_top_left = svg_path.top_left
    bbox_bot_right = svg_path.bottom_right

    return bbox_top_left, bbox_bot_right


def transform_path(p, center=False, scale=1, rotate_angle=0, rotate_point=Point()):
    """
    transforms a path
    """

    p_tl, p_br = calculate_bounding_box_of_path(p)

    width, height = get_width_and_height_of_shape_from_two_points(p_tl, p_br)

    # parse the input with SVG path grammar
    pd = SvgGrammar().parseString(path)

    # first point of path
    first_point = Point(pd[0][1][0], pd[0][1][1])

    if center is True:
        # center point of path
        origin_point = Point(p_tl.x+width/2, p_tl.y-height/2)

        # calculate what's the new starting point of path based on the new origin
        new_first_point = Point(first_point.x - origin_point.x, first_point.y - origin_point.y)
    else:
        new_first_point = Point(first_point.x, first_point.y)

    new_first_point.rotate(rotate_angle, rotate_point)
    new_first_point.mult(scale)
    new_p = "m %f,%f " % (new_first_point.x, new_first_point.y)

    tmpp = Point()
    origin = Point()

    for n in range(0, len(pd)):
        if pd[n][0] == 'm' and n == 0:
            for m in range(2, len(pd[n])):
                tmpp.assign(pd[n][m][0], pd[n][m][1])
                tmpp.rotate(rotate_angle, rotate_point)
                tmpp.mult(scale)
                new_p += str(tmpp.x) + "," + str(tmpp.y) + " "
        else:
            if pd[n][0] == 'h' or pd[n][0] == 'v':
                new_p += "l "
            else:
                new_p += pd[n][0] + " "

            for m in range(1, len(pd[n])):
                if pd[n][0] == 'h':
                    tmpp.assign(pd[n][m][0], 0)
                elif pd[n][0] == 'v':
                    tmpp.assign(0, pd[n][m][0])
                else:
                    tmpp.assign(pd[n][m][0], pd[n][m][1])

                tmpp.rotate(rotate_angle, rotate_point)
                tmpp.mult(scale)
                new_p += str(tmpp.x) + "," + str(tmpp.y) + " "

    return width, height, new_p




def get_width_and_height_of_shape_from_two_points(tl, br):
    """
    SVG's origin is top left so we need to take the absolute value, otherwise
    the length will be negative (alternatively, we can do tl.y - br.y)
    """
    return (br.x - tl.x), abs(br.y - tl.y) # width, height




def width_and_height_to_path(width, height, radii=None):
    """
    Returns a centered path based on width and height; smooth corners
    can be defined with radii
    """

    width = float(width)
    height = float(height)

    # The calculation to obtain the 'k' coefficient can be found here:
    # http://itc.ktu.lt/itc354/Riskus354.pdf
    # "APPROXIMATION OF A CUBIC BEZIER CURVE BY CIRCULAR ARCS AND VICE VERSA"
    # by Aleksas Riskus
    k = 0.5522847498

    all_zeros = True

    if radii is not None:
        # check if all values are equal to '0'
        for value in radii.values():
            if value != 0:
                all_zeros = False

        if all_zeros is True:
            path = "m %f,%f h %f v %f h %f v %f z" % (-width/2, -height/2,
                                                      width, height,
                                                      -width, -height)
        else:

            top_left = float(radii.get('tl') or radii.get('top_left') or 0)
            top_right = float(radii.get('tr') or radii.get('top_right') or 0)
            bot_right = float(radii.get('br') or radii.get('bot_right') or radii.get('bottom_right') or 0)
            bot_left = float(radii.get('bl') or radii.get('bot_left') or radii.get('bottom_left') or 0)

            path = "m %f,%f " % (-width/2, 0)
            if top_left == 0:
                path += "v %f h %f " % (-height/2, width/2)
            else:
                r = top_left
                path += "v %f c %f,%f %f,%f %f,%f h %f " % (-(height/2-r), 0,-k*r, -r*(k-1),-r, r,-r, width/2-r)

            if top_right == 0:
                path += "h %f v %f " % (width/2, height/2)
            else:
                r = top_right
                path += "h %f c %f,%f %f,%f %f,%f v %f " % (width/2-r, k*r,0, r,-r*(k-1), r,r, height/2-r)

            if bot_right == 0:
                path += "v %f h %f " % (height/2, -width/2)
            else:
                r = bot_right
                path += "v %f c %f,%f %f,%f %f,%f h %f " % (height/2-r, 0,k*r, r*(k-1),r, -r,r, -(width/2-r))

            if bot_left == 0:
                path += "h %f v %f " % (-width/2, -height/2)
            else:
                r = bot_left
                path += "h %f c %f,%f %f,%f %f,%f v %f " % (-(width/2-r), -k*r,0, -r,r*(k-1), -r,-r, -(height/2-r))

            path += "z"

    else:
        path = "m %f,%f h %f v %f h %f v %f z" % (-width/2, -height/2,
                                                   width, height,
                                                   -width, -height)

    return path




def ring_diameters_to_path(d1, d2):
    """
    Returns a path for a ring based on two diameters; the
    function automatically determines which diameter is the
    inner and which is the outer diameter
    """

    path = None

    if d1 == d2:
        path = circle_diameter_to_path(d1)
    else:
        if d1 > d2:
            outer = d1
            inner = d2
        else:
            outer = d2
            inner = d1
        path = circle_diameter_to_path(outer)
        path += circle_diameter_to_path(inner, Point(0, outer/2))

    return path





def circle_diameter_to_path(d, offset=Point()):
    """
    Returns an SVG path of a circle of diameter 'diameter'
    """

    r = d/2.0

    # The calculation to obtain the 'k' coefficient can be found here:
    # http://itc.ktu.lt/itc354/Riskus354.pdf
    # "APPROXIMATION OF A CUBIC BEZIER CURVE BY CIRCULAR ARCS AND VICE VERSA"
    # by Aleksas Riskus
    k = 0.5522847498

    return "m %s,%s c %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s z" % (0,r-offset.y, k*r,0, r,-r*(1-k), r,-r, 0,-r*k, -r*(1-k),-r, -r,-r, -r*k,0, -r,r*(1-k), -r,r, 0,r*k, r*(1-k),r, r,r)





def drillPath(diameter):
    """
    Returns an SVG path for a drill symbol of diameter 'diameter'
    """

    r = diameter/2.0

    # The calculation to obtain the 'k' coefficient can be found here:
    # http://itc.ktu.lt/itc354/Riskus354.pdf
    # "APPROXIMATION OF A CUBIC BEZIER CURVE BY CIRCULAR ARCS AND VICE VERSA"
    # by Aleksas Riskus
    k = 0.5522847498

    # internal circle
    b = r*0.9

    return "m %s,%s c %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s z m %s,%s %s,%s c %s,%s %s,%s %s,%s l %s,%s %s,%s c %s,%s %s,%s %s,%s z" % (0,r, k*r,0, r,-r*(1-k), r,-r, 0,-r*k, -r*(1-k),-r, -r,-r, -r*k,0, -r,r*(1-k), -r,r, 0,r*k, r*(1-k),r, r,r, 0,-(r-b), 0,-2*b, -b*k,0, -b,b*(1-k), -b,b, b,0, b,0, 0,k*b, -b*(1-k),b, -b,b)





def placementMarkerPath():
    """
    Returns a path for the placement marker
    """
    diameter = 0.2

    r = diameter/2.0

    # The calculation to obtain the 'k' coefficient can be found here:
    # http://itc.ktu.lt/itc354/Riskus354.pdf
    # "APPROXIMATION OF A CUBIC BEZIER CURVE BY CIRCULAR ARCS AND VICE VERSA"
    # by Aleksas Riskus
    k = 0.5522847498

    # extension
    b = r*1.8

#    return "m %s,%s c %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s m %s,%s %s,%s m %s,%s %s,%s z" % (0,r, k*r,0, r,-r*(1-k), r,-r, 0,-r*k, -r*(1-k),-r, -r,-r, -r*k,0, -r,r*(1-k), -r,r, 0,r*k, r*(1-k),r, r,r, 0,-(r-b), 0,-2*b, -b,b, 2*b,0)

    return "m %s,%s c %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s %s,%s m %s,%s %s,%s z" % (0,r, k*r,0, r,-r*(1-k), r,-r, 0,-r*k, -r*(1-k),-r, -r,-r, -r*k,0, -r,r*(1-k), -r,r, 0,r*k, r*(1-k),r, r,r, -b,-r, 2*b,0)





def mirror_transform(transform, axis='y'):
    """
    Returns a mirrored transfrom
    """

    mirrored_transform = transform

    regex = r"(?P<before>.*?)translate\s?\(\s?(?P<x>-?[0-9]*\.?[0-9]+)\s+(?P<y>-?[0-9]*\.?[0-9]+\s?)\s?\)(?P<after>.*)"
    capture = re.match(regex, transform)

    if capture is not None:
        mirrored_transform = "%s translate(%g %s) %s" % (
                capture.group('before'),
                -float(capture.group('x')),
                capture.group('y'),
                capture.group('after'))

    return mirrored_transform





def makeSvgLayers(top_layer, transform=None, refdef=None):
    """
    Creates Inkscape SVG layers that correspond to a board's layers.
    Includes the default style definition from the stylesheet.
    Returns a dictionary of layer instantiations.
    """

    layer_control = config.brd['layer-control']

    # Holds SVG layers
    layers = {}

    # Create layers for top and bottom PCB layers
    for layer_dict in reversed(config.stk['layers-dict']):

        layer_type = layer_dict['type']
        layer_name = layer_dict['name']

        # create SVG layer for PCB layer
        layers[layer_name] = {}
        element = layers[layer_name]['layer'] = makeSvgLayer(top_layer,
                                                             layer_name,
                                                             transform,
                                                             None,
                                                             refdef)
        element.set('{'+config.cfg['ns']['pcbmode']+'}%s' % ('pcb-layer'), layer_name)

        sheets = layer_dict['stack']
        if layer_type == 'signal-layer-surface':
            placement_dict = [{"name": "placement", "type": "placement"}]
            assembly_dict = [{"name": "assembly", "type": "assembly"}]
            solderpaste_dict = [{"name": "solderpaste", "type": "solderpaste"}]

            # Layer appear in Inkscape first/top to bottom/last
            sheets = placement_dict + assembly_dict + solderpaste_dict + sheets

        for sheet in reversed(sheets):

            sheet_type = sheet['type']
            sheet_name = sheet['name']

            # Set default style for this sheet
            try:
                style = utils.dictToStyleText(config.stl['layout'][sheet_type]['default'][layer_name])
            except:
                # A stylesheet may define one style for any sheet type
                # or a specific style for multiple layers of the same
                # type. If, for example, a specific style for
                # 'internal-2' cannot be found, PCBmodE will default
                # to the general definition for this type of sheet
                style = utils.dictToStyleText(config.stl['layout'][sheet_type]['default'][layer_name.split('-')[0]])

            if layer_control[sheet_type]['hide'] == True:
                style += 'display:none;'

            tmp = layers[layer_name]
            tmp[sheet_type] = {}
            element = tmp[sheet_type]['layer'] = makeSvgLayer(parent_layer=tmp['layer'],
                                                              layer_name=sheet_name,
                                                              transform=None,
                                                              style=style,
                                                              refdef=refdef)

            element.set('{'+config.cfg['ns']['pcbmode']+'}%s' % ('sheet'), sheet_type)
            if layer_control[sheet_type]['lock'] == True:
                element.set('{'+config.cfg['ns']['sodipodi']+'}insensitive', 'true')

            # A PCB layer of type 'conductor' is best presented in
            # seperate sub-layers of 'pours', 'pads', and
            # 'routing'. The following generates those sub-layers
            if sheet_type == 'conductor':
                tmp2 = layers[layer_name]['conductor']
                conductor_types = ['routing', 'pads', 'pours']

                for cond_type in conductor_types:
                    try:
                        style = utils.dictToStyle(config.stl['layout']['conductor'][cond_type].get(layer_name))
                    except:
                        # See comment above for rationalle
                        style = utils.dictToStyleText(config.stl['layout']['conductor'][cond_type][layer_name.split('-')[0]])


                    if layer_control['conductor'][cond_type]['hide'] == True:
                        style += 'display:none;'

                    tmp2[cond_type] = {}
                    element = tmp2[cond_type]['layer'] = makeSvgLayer(parent_layer=tmp2['layer'],
                                                                      layer_name=cond_type,
                                                                      transform=None,
                                                                      style=style,
                                                                      refdef=refdef)

                    element.set('{'+config.cfg['ns']['pcbmode']+'}%s' % ('sheet'), cond_type)

                    if layer_control['conductor'][cond_type]['lock'] == True:
                        element.set('{'+config.cfg['ns']['sodipodi']+'}insensitive', 'true')



    for info_layer in ['origin','dimensions','outline','drills','documentation']:
        style = utils.dictToStyleText(config.stl['layout'][info_layer].get('default'))
        if layer_control[info_layer]['hide'] == True:
            style += 'display:none;'
        layers[info_layer] = {}
        element = layers[info_layer]['layer'] = makeSvgLayer(top_layer,
                                                             info_layer,
                                                             transform,
                                                             style,
                                                             refdef)
        element.set('{'+config.cfg['ns']['pcbmode']+'}%s' % ('sheet'), info_layer)
        if layer_control[info_layer]['lock'] == True:
            element.set('{'+config.cfg['ns']['sodipodi']+'}insensitive', 'true')

    return layers





def makeSvgLayer(parent_layer,
                 layer_name,
                 transform=None,
                 style=None,
                 refdef=None):
    """
    Create and return an Inkscape SVG layer
    """

    new_layer = et.SubElement(parent_layer, 'g')
    new_layer.set('{'+config.cfg['ns']['inkscape']+'}groupmode', 'layer')
    new_layer.set('{'+config.cfg['ns']['inkscape']+'}label', layer_name)
    if transform is not None:
        new_layer.set('transform', transform)
    if style is not None:
        new_layer.set('style', style)
    if refdef is not None:
        new_layer.set('refdef', refdef)

    return new_layer






def create_layers_for_gerber_svg(cfg, top_layer, transform=None, refdef=None):
    """
    Creates a dictionary of SVG layers

    'top_layer' is the parent layer element

    """

    # holds all SVG layers for the board
    board_svg_layers = {}

    # create layers for top and bottom PCB layers
    for pcb_layer_name in reversed(utils.get_surface_layers(cfg)):

        # create SVG layer for PCB layer
        layer_id = pcb_layer_name
        board_svg_layers[pcb_layer_name] = {}
        board_svg_layers[pcb_layer_name]['layer'] = create_svg_layer(cfg, top_layer,
                                                                     pcb_layer_name,
                                                                     layer_id,
                                                                     transform,
                                                                     None,
                                                                     refdef)

        # create the following PCB sheets for the PCB layer
        pcb_sheets = ['copper', 'silkscreen', 'soldermask']
        for pcb_sheet in pcb_sheets:

            # define a layer id
            layer_id = "%s_%s" % (pcb_layer_name, pcb_sheet)
            if refdef is not None:
                layer_id += "_%s" % refdef

            style = utils.dict_to_style(cfg['layout_style'][pcb_sheet]['default'].get(pcb_layer_name))
            tmp = board_svg_layers[pcb_layer_name]
            tmp[pcb_sheet] = {}
            tmp[pcb_sheet]['layer'] = create_svg_layer(cfg, tmp['layer'],
                                                       pcb_sheet,
                                                       layer_id,
                                                       None,
                                                       style,
                                                       refdef)



    # create dimensions layer
    layer_name = 'outline'
    # define a layer id
    layer_id = "%s" % (layer_name)
    if refdef is not None:
        layer_id += "_%s" % refdef
    style = '' #utils.dict_to_style(cfg['layout_style'][layer_name].get('default'))
    board_svg_layers[layer_name] = {}
    board_svg_layers[layer_name]['layer'] = create_svg_layer(cfg,
                                                             top_layer,
                                                             layer_name,
                                                             layer_id,
                                                             transform,
                                                             style,
                                                             refdef)

    # create drills layer
    layer_name = 'drills'
    # define a layer id
    layer_id = "%s" % (layer_name)
    if refdef is not None:
        layer_id += "_%s" % refdef
    style = utils.dict_to_style(cfg['layout_style'][layer_name].get('default'))
    board_svg_layers[layer_name] = {}
    board_svg_layers[layer_name]['layer'] = create_svg_layer(cfg,
                                                             top_layer,
                                                             layer_name,
                                                             layer_id,
                                                             transform,
                                                             style,
                                                             refdef)

    # create drills layer
    layer_name = 'documentation'
    # define a layer id
    layer_id = "%s" % (layer_name)
    if refdef is not None:
        layer_id += "_%s" % refdef
    style = utils.dict_to_style(cfg['layout_style'][layer_name].get('default'))
    board_svg_layers[layer_name] = {}
    board_svg_layers[layer_name]['layer'] = create_svg_layer(cfg,
                                                             top_layer,
                                                             layer_name,
                                                             layer_id,
                                                             transform,
                                                             style,
                                                             refdef)

    return board_svg_layers







def rect_to_path(shape):
    """
    Takes a 'rect' definition and returns a corresponding path
    """
    width = float(shape['width'])
    height = float(shape['height'])
    radii = shape.get('radii')
    path = width_and_height_to_path(width,
                                    height,
                                    radii)

    return path






def create_meandering_path(params):
    """
    Returns a meander path based on input parameters
    """

    deg_to_rad = 2 * pi / 360

    radius = params.get('radius')
    theta = params.get('theta')
    width = params.get('trace-width')
    number = params.get('bus-width') or 1
    pitch = params.get('pitch') or 0

    coords = []
    coords.append(Point(0, -(number-1)*pitch/2))
    for n in range(1, int(number)):
        coords.append(Point(2*radius*cos(theta*deg_to_rad), pitch))

    path = ''

    for coord in coords:
        path += create_round_meander(radius, theta, coord)

    # calculate the reduction of bounding box width to be used in
    # pattern spacing setting
    spacing = radius - radius*cos(theta*deg_to_rad)

    return path, spacing






def create_round_meander(radius, theta=0, offset=Point()):
    """
    Returns a single period of a meandering path based on radius
    and angle theta
    """

    deg_to_rad = 2 * pi / 360

    r = radius
    t = theta * deg_to_rad

    # The calculation to obtain the 'k' coefficient can be found here:
    # http://itc.ktu.lt/itc354/Riskus354.pdf
    # "APPROXIMATION OF A CUBIC BEZIER CURVE BY CIRCULAR ARCS AND VICE VERSA"
    # by Aleksas Riskus
    k = 0.5522847498

    # the control points need to be shortened relative to the angle by this factor
    j = 2*t/pi

    path =  "m %s,%s " % (-2*r*cos(t)-offset.x, -offset.y)
    path += "c %s,%s %s,%s %s,%s " % (-k*r*j*sin(t),-k*r*j*cos(t), -(r-r*cos(t)),-r*sin(t)+r*k*j, -(r-r*cos(t)),-r*sin(t))
    path += "c %s,%s %s,%s %s,%s " % (0,-k*r, r-k*r,-r, r,-r)
    path += "c %s,%s %s,%s %s,%s " % (k*r,0, r,r-k*r, r,r)
    path += "c %s,%s %s,%s %s,%s " % (0,k*r*j, -(r-r*cos(t)-k*r*j*sin(t)),r*sin(t)-r*k*j*cos(t), -r+r*cos(t),r*sin(t))
    path += "c %s,%s %s,%s %s,%s " % (-k*r*j*sin(t),k*r*j*cos(t), -(r-r*cos(t)),r*sin(t)-r*k*j, -(r-r*cos(t)),r*sin(t))
    path += "c %s,%s %s,%s %s,%s " % (0,k*r, r-k*r,r, r,r)
    path += "c %s,%s %s,%s %s,%s " % (k*r,0, r,-r+k*r, r,-r)
    path += "c %s,%s %s,%s %s,%s "  % (0,-k*r*j, -(r-r*cos(t)-k*r*j*sin(t)),-r*sin(t)+r*k*j*cos(t), -r+r*cos(t),-r*sin(t))

    return path





def coord_list_to_svg_path(coord_list):
    """
    Turn a list of points into an SVG path
    """

    path = '' #'M 0,0 '# % (coord_list[0]['coord'].x, coord_list[0]['coord'].y)
    last_action_type = ''

    for action in coord_list:
        if action['type'] == 'move':
            if last_action_type != 'M':
                path += 'M '
            path += '%s,%s ' % (action['coord'].x, -action['coord'].y)
            last_action_type = 'M'
        if action['type'] == 'draw':
            if last_action_type != 'L':
                path += 'L '
            path += '%s,%s ' % (action['coord'].x, -action['coord'].y)
            last_action_type = 'L'

    return path

