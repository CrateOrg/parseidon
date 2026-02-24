# Usage of the regex mode
This file describes the usage area of the regex mode, along with a step-by-step tutorial on how to use it.

## Pattern matching with regex
In order to match patterns using regular expressions(regex) the user defines patterns that captures the desired format of the intended matches.

Parseidon includes `src/parseidon/data/regex_files/main_regex.yaml` which defines a set of regex patterns for matching the following formats:
- IPv4-adresses
- IPv6-adresses
- MAC-adresses
- FOI document IDs
- URLs
- E-mail adresses
- Phone numbers in valid swedish formats
- Wifi-verions
- Dates in valid swedish and international formats
- Various SI-units and units of data
- Some recognized techniques and protocols.

This file serves as the default for pattern matching with the regex mode, however, the user of parseidon is free to define their own regex-patterns, either to extend a existing set of patterns or to generate a new pattern file.

## How to use the regex mode

The program in regex mode is ran from the project root with the following command:
```bash
parseidon regex </path/to/input_file1> </path/to/dir2/>* ... </path/to/input_fileN>
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
    - Keyword argument to specify possible regex matches to exclude from the output.

* `--num-threads, -n <number of threads>`
    - Number of threads to spawn during content extraction.

