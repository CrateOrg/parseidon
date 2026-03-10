# Usage of the find mode
This file describes the usage area of the find mode, along with a step-by-step tutorial on how to use it.

## Pattern matching and identifying abnormal strings with find mode
Find mode combines filter mode with a pattern matching mode(regex or PEG) of your choosing. The mode starts of by identifying all pattern matches. This is then followed by running the filter mode to find uncommon strings that might be interesting even though the pattern matcher did not have coverage for them.

If you wish to learn how the pattern matcher and filter modes function, please see:

[pegparse_mode.md](pegparse_mode.md)

[regex_mode.md](regex_mode.md)

[filter_mode.md](filter_mode.md)

## How to use the find mode

The program in find mode is ran from the project root with the following command:
```bash
parseidon find </path/to/input_file1> </path/to/dir2/>* ... </path/to/input_fileN>
```
Where `/path/to/inputX` refers to scanning a specific file, the `*` in `/path/to/dir2/*` refers to scanning every file in the given directory.

Flags/keyword arguments:
* `--output </path/to/output/directory/filename>, -o </path/to/output/directory/filename> `
    - This keyword argument is used to specify the prefered output directory along with the desired filename.
    - Default: ./yyyy-mm-dd_hh:mm:ss.csv.
    - If output name is set to `-`, the output will be sent to stdout.

* `--regex-file </path/to/regex_filename.yaml>, -g </path/to/regex_filename.yaml>`
    - Keyword argument to specify regexes to use in for pattern extraction.
    - Default: `regex_files/main_regex.yaml`

* `--peg-file </path/to/peg_filename.txt>, -g </path/to/peg_filename.txt>`
    - Keyword argument to specify PEG grammars to use in for pattern extraction.
    - Default: `peg_files/peg_grammars.txt`

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

* `--skip-list </path/to/skip_list.txt>, -l </path/to/skip_list.txt>`
    - Keyword argument to specify possible regex matches to exclude from the output.

* `--num-threads, -n <number of threads>`
    - Number of threads to spawn during content extraction.

* `--regex, -r`
    - Keyword argument to specify regex should be used for pattern matching.

* `--pegparse, -p`
    - Keyword argument to specify pegparse should be used for pattern matching.

* `--enable-plugins, -e`
    - Enables the use of installed plugins.
