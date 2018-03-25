from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')


@register.filter
def get_item_or_zero(dictionary, key):
    return dictionary.get(key, 0)


@register.filter()
def set_color(level):
    text_decoration = ''
    if level == 'INFO':
        color = 'blue'
    elif level == 'WARN':
        color = 'orange'
    elif level == 'ERROR' or level == 'CRIT':
        color = 'red'
        text_decoration = 'font-weight: bold;'
    else:
        color = 'inherit'
    return '<span style="color: ' + color + ';' + text_decoration + '">' + level + '</span>'