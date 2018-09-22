from pydm.widgets.base import (
    PyDMPrimitiveWidget, PyDMWidget, PyDMWritableWidget)


def pydmwidget_factory(widgetclass, pydm_class='read'):
    if pydm_class.lower().startswith('primi'):
        pydmclass = PyDMPrimitiveWidget
    elif pydm_class.lower().startswith('read'):
        pydmclass = PyDMWidget
    else:
        pydmclass = PyDMWritableWidget

    class PyDMCustomWidget(widgetclass, pydmclass):

        def __init__(self, *args, **kwargs):
            try:
                init_channel = kwargs.pop('init_channel')
            except KeyError:
                init_channel = None

            widgetclass.__init__(self, *args, **kwargs)
            if pydm_class.lower().startswith('primi'):
                pydmclass.__init__(self)
            else:
                pydmclass.__init__(self, init_channel=init_channel)
    return PyDMCustomWidget
