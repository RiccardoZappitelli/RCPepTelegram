# Plugin System

This document explains how the **pep2 plugin system** works, how plugins are structured, and how they are loaded and executed.

If you need documentation about **pep2 core functions and commands**, refer to: **docs/COMMANDS.md**

---

## Overview

The plugin system allows extending pep2 by registering self-contained Python classes that expose callable actions.
Each plugin encapsulates a single feature (system control, automation, scheduling, etc.) and is discovered and managed by pep2 at runtime.

Plugins are defined as **classes**, not instances. pep2 is responsible for instantiating them and binding them to the core.

---

## Plugin Structure

Every plugin must inherit from the base `Plugin` class:

```python
from .plugin_base import Plugin
```

A minimal plugin looks like this:

```python
class ExamplePlugin(Plugin):
    def __init__(self):
        super().__init__(
            "✨ Example Plugin",
            "example_plugin",
            "Short description of what this plugin does."
        )

    def action(self, arg1: str) -> None:
        ...
```

---

## Plugin Metadata

Plugin metadata is defined in the constructor via `super().__init__`.

### Metadata Fields

| Field | Purpose |
|------|--------|
| Name | Human-readable name (emoji allowed) |
| Plugin ID | Unique internal identifier |
| Description | Short explanation of the plugin behavior |

This metadata is used for:
- plugin discovery
- user-facing listings
- documentation generation
Note: if a plugins has "<STARTUPSCRIPT>" as button_label, its action will be executed as soon as it loaded.

---

## Actions

Plugins expose functionality through **action methods**.

By convention, the main entry point is named `action`.

```python
def action(self, ...) -> None:
    ...
```

### Argument Handling

pep2 inspects the function signature to determine how the action can be called.

| Python parameter kind | User-visible behavior |
|----------------------|----------------------|
| Positional-only | Positional argument |
| Positional-or-keyword | Positional argument |
| `*args` | Variable positional arguments |
| Keyword-only | Keyword-only argument |
| `**kwargs` | Variable keyword arguments |

---

## pep2 Binding

Each plugin instance receives a reference to the pep2 core through `self.pep2`.

This allows plugins to:
- send messages
- update loading bars
- access shared state
- interact with other core services

Refer to **docs/COMMANDS.md** for the complete list of available pep2 functions.

---

## Plugin Registration

Plugins are registered by adding their **class** to the plugin list:

```python
plugins = [
    PluginA,
    PluginB,
    PluginC,
]
```

pep2 will:
1. Instantiate each plugin
2. Bind the pep2 core
3. Register exposed actions
