# Parseidon headings plugin
This plugin handles the situation where documents contain numbered headings that are written in the format of a valid IPv4-adress, e.g. 1.1.1.1. 

To avoid IPv4-adresses from mistakenly be ignored, the plugin only discard e.g. 1.1.1.1 if its parent headings 1.1.1, 1.1 and 1 preceeds it in the document.

##  Installation
To install the headings plugin, follow the guide on installing the core package([installation](../installation.md)) followed by:

```bash
pip install parseidon-headings-plugin
```

Make use to use `-e` option when running parseidon to enable plugin use.

#### Install local version
```bash
pip install -e parseidon_headings_plugin
```