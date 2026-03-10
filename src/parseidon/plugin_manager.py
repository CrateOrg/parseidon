import pluggy
from importlib.metadata import entry_points
from parseidon.hookspecs import ContentHandlerSpecs


class PluginManager:

    __instance = None

    @staticmethod
    def init_plugin_manager(enable_plugins: bool):
        if PluginManager.__instance is not None:
            return # Should maybe consider DI
        PluginManager.__instance = pluggy.PluginManager(project_name="parseidon")
        PluginManager.__instance.add_hookspecs(ContentHandlerSpecs)
        if enable_plugins:
            for ep in entry_points(group="parseidon.plugins"):
                plugin = ep.load()
                PluginManager.__instance.register(plugin())

    @staticmethod
    def get_plugin_manager():
        if PluginManager.__instance is None:
            raise RuntimeError("Plugin manager must be initialized first!")
        return PluginManager.__instance
