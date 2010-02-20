
from amsn2.core import aMSNUserInterfaceManager
import sys

# Here we load the actual front end.
# We need to import the front end module and return it
# so the guimanager can access its classes
def load():
    try:
        import web
        import amsn2.ui.front_ends.web._web
    except ImportError:
        etype, value, traceback = sys.exc_info()
        traceback.print_exception(etype, value, traceback.tb_next)
        return None
    return amsn2.ui.front_ends.web._web

# Initialize the front end by checking for any
# dependency then register it to the guimanager
try:
    import imp
    aMSNUserInterfaceManager.register_frontend("web", sys.modules[__name__])

except ImportError:
    pass

