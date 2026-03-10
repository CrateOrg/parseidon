# Parseidon hyphen plugin
This plugin handles words that are split with a hyphen and a newline due to the document line width being exceeded by the word.

The plugin analyzes each word that has been split into two separate lines and checks whether it should be handled as a word with or without the hyphen. This ensures e.g. hour-\nlong is handled as hour-long and hour-\nglass as hourglass.

##  Installation
To install the hyphen plugin, follow the guide on installing the core package([installation](../installation.md)) followed by:

```bash
pip install parseidon-hyphen-plugin
```

Make use to use `-e` option when running parseidon to enable plugin use.

#### Install local version
```bash
pip install -e parseidon_hyphen_plugin
```