# Parseidon
Parseidon is a document parsing text extracting tool written in Python. The purpose of parseidon is to let the user extract strings that match a desired predefined format using either regex or PEG for pattern matching. Additionally the filter mode of parseidon uses vocabulary data to filter out common words, leaving uncommon strings that might be of interest. The pattern matching and the filtering functionality can also be used together in the find mode, letting the filter assist the user in identifying words not covered by their regexes or PEGs

## Modes
Parseidon consists of four separate modes:
* `regex_mode` performs pattern matching on the document strings using regular expressions.
    - A more detailed description can be found here [regex_mode](/docs/usage/regex_mode.md)
* `pegparse_mode` essentially has the same functionality as `regex_mode` except it utilizes parsing expression grammar(PEG) rules to find matches.
    - A more detailed description can be found here [pegparse_mode](/docs/usage/pegparse_mode.md)
* `filter_mode`filters out common dictionary items, leaving the unrecognized potentially interesting words for manual inspection by the user.
 - A more detailed description can be found here [filter_mode](/docs/usage/filter_mode.md)
* `find_mode`combines the functionality of `filter_mode` with either `regex_mode` or `pegparse_mode`, highlighting both pattern matches and unrecognized strings.
 - A more detailed description can be found here [find_mode](/docs/usage/find_mode.md)




## Plugins
The project includes plugins in addition to the core project. Below follows a list of implemented plugins.

* parseidon-headings-plugin
    - Removes numbered headings that could falsely be identified as IPv4-adresses

* parseidon-hyphen-plugin
    - Determines if a word containing a hyphen is correct or if the hyphen exists only due to the line width being exceeded by the word.

These are described in more detail in [headings_plugin](/docs/plugins/headings_plugin.md) and [hyphen_plugin](/docs/plugins/hyphen_plugin.md).


## Documentation
In addition to this document, the project includes a [documentation](/docs/) folder which contain information about [installation](/docs/installation.md), [usage](/docs/usage/), [plugins](/docs/plugins/) and [language resources](/docs/language_data.md).

## Contact
For questions, feedback, or general inquiries, please contact us at [parseidon@foi.se](mailto:parseidon@foi.se).

## Data attribution
For attribution of language resources used in this project, please refer to [third party notices](third_party_notices/THIRD_PARTY_NOTICES). For information on how the respective sources are used, please see [language resources](/docs/language_data.md).