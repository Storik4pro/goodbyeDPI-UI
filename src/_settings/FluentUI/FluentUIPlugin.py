from ..FluentUI.Controls import FluentUIControlsPlugin
from ..FluentUI.impl import FluentUIImplPlugin
from ..FluentUI import resource_rc

__uri__ = "FluentUI"
__major__ = 1
__minor__ = 0


def registerTypes():
    FluentUIImplPlugin.registerTypes()
    FluentUIControlsPlugin.registerTypes()
