from django import template

register = template.Library()


@register.filter
def list_index(obj, i):
    """
    get index values of an list at django template.
    :param obj: []
    :param i: 0, 1,2,3 .. etc
    :return: [][0-1]
    """
    return obj[i - 1]


@register.filter
def dict_index(obj, i):
    """
    get index values of an list at django template.
    :param obj: {"key": "value", "k3": "v3", "k4": "v4"}
    :param i: key, k3 etc
    :return: value of key.
    """
    return obj[i]
