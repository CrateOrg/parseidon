import pluggy
from importlib.metadata import entry_points
from parseidon.hookspecs import ContentHandlerSpecs


def load_plugins():
    pm = pluggy.PluginManager(project_name="parseidon")
    pm.add_hookspecs(ContentHandlerSpecs)
    for ep in entry_points(group="parseidon.plugins"):
        plugin = ep.load()
        pm.register(plugin())
    return pm
