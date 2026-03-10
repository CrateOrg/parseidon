# Usage of the filter mode
This file describes the usage area of the filter mode, along with a step-by-step tutorial on how to use it.

## Identifying abnormal strings with filter mode
In addition to the pattern matching, a filter mode was developed to filter out vocabulary terms, leaving only unrecognized strings that might be of interest. The process of filtering out the vocabulary items is based on trie datastructures, where a trie represents rexognized strings that should not be highlighted by the filter mode. Parseidon comes with a [swedish trie](../../src/parseidon/data/trie/swedish.marisa) which contains common vocabulary items in swedish. Along with the language based trie, a [special characters trie](../../src/parseidon/data/trie/punctuation.marisa) has been created to handle common punctuation characters. 

In order to update the trie files or create your own, please see the [language_data](../language_data.md) docs. There you will also find more information regarding the data collection for the tries included in parseidon.

## How to use the filter mode

The program in filter mode is ran from the project root with the following command:
```bash
parseidon filter </path/to/input_file1> </path/to/dir2/>* ... </path/to/input_fileN>
```
Where `/path/to/inputX` refers to scanning a specific file, the `*` in `/path/to/dir2/*` refers to scanning every file in the given directory.

Flags/keyword arguments:
* `--output </path/to/output/directory/filename>, -o </path/to/output/directory/filename> `
    - This keyword argument is used to specify the prefered output directory along with the desired filename.
    - Default: ./yyyy-mm-dd_hh:mm:ss.csv.
    - If output name is set to `-`, the output will be sent to stdout.

* `--trie-file </path/to/trie_file.marisa>, -t </path/to/trie_file.marisa>`
    - Keyword argument to specify PEG grammars to use in for pattern extraction.
    - Default: `trie/swedish.marisa`
    - English version: `trie/english.marisa`

* `--image-extract, -i`
    - If the flag is set, extraction from document images will be enabled with Tesseract-ocr.
    - Extracting text from images with OCR is a timeconsuming task, the extraction time grows with the number and complexity of images.
    - The extraction process is usually getting text from 2-5 images per second, however, it is highly dependent on the complexity and size of each image.

* `--column-context, -c`
    - If the flag is set, the context in spreadsheet matches will be based on the previous and next cell
    in the column. Otherwise it is rowbased

* `--draw-boxes, -d`
    - When the flag is set, the program will output a PDF-document where the matches have been outlined by a green rectangle. 
    - No csv-output will be generated.
    - Can not be combined with `-f` flag.

* `--output-format, -f`
    - Format of output.
    - Valid choices are `csv` (default) and `json`
    - Can not be combined with `-d` flag.

* `--skip-list </path/to/skip_list.txt>, -l </path/to/skip_list.txt>`
    - Keyword argument to specify possible filter matches to exclude from the output.

* `--num-threads, -n <number of threads>`
    - Number of threads to spawn during content extraction.

* `--enable-plugins, -e`
    - Enables the use of installed plugins.
