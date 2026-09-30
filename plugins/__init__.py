from dataclasses import dataclass, field

@dataclass
class Plugin:
    name: str
    version: str
    description: str
    permissions: set[str] = field(default_factory=set)
    enabled: bool = True

class PluginManager:
    def __init__(self):
        self._plugins = {}
    def register(self, plugin: Plugin):
        self._plugins[plugin.name] = plugin
    def list_plugins(self):
        return list(self._plugins.values())
    def set_enabled(self, name: str, enabled: bool):
        if name in self._plugins:
            self._plugins[name].enabled = enabled