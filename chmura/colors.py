from django.core.exceptions import ObjectDoesNotExist
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000 as delta_e
from colormath.color_conversions import convert_color
from chmura.models import Subject

material_palette = ['#FFCDD2', '#F8BBD0', '#E1BEE7', '#D1C4E9', '#C5CAE9', '#BBDEFB', '#B3E5FC', '#B2EBF2', '#B2DFDB',
                    '#C8E6C9', '#DCEDC8', '#F0F4C3', '#FFF9C4', '#FFECB3', '#FFE0B2', '#FFCCBC', '#D7CCC8', '#F5F5F5',
                    '#CFD8DC']


def hex_to_rgb(h):
    h = h[1:]
    # Thanks to StackOverflow, John1024
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hex_to_labcolor(r):
    return convert_color(sRGBColor(*hex_to_rgb(r)), LabColor)


def find_nearest_color(hex_color):
    color_in = hex_to_labcolor(hex_color)

    minv = [0, delta_e(color_in, hex_to_labcolor(material_palette[0]))]

    for idx, color in enumerate(material_palette[1:]):
        delta = delta_e(color_in, hex_to_labcolor(color))
        if delta < minv[1]:
            minv = [idx+1, delta]
    return material_palette[minv[0]]


def get_color(nazwa, hex_color):
    try:
        return Subject.objects.get(name=nazwa).color
    except ObjectDoesNotExist:
        hex_color = find_nearest_color(hex_color)
        color = Subject(name=nazwa, color=hex_color)
        color.save()
        return hex_color
