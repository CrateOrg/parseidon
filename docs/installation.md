# Installation guide for parseidon
This is a step by step on how to install parseidon and how you can run it.

## Installation
Parseidon can either be run locally using uv, in a docker container or it can be installed using pip.

### Requirements
The program is written solely in Python 3. Other than a few non-standard Python packages,
the program also requires LibreOffice if you plan on extracting information from older 
word files(.doc), excel(.xls) and OpenDocument(.odt, .odf) files. 
The C library libmagic1 is also required for parsing plaintext documents with fileextensions
other than .txt. Furthermore, to extract data from EPS images Ghostscript has to be installed on
the system.

There is also an option to use OCR to extract the text from pictures/images in PDFs, Word-, Image- and Excelfiles, for this to be possible, you also need to have Tesseract-ocr installed on your machine.

* `python3`
* `libreoffice`
* `libmagic1`
* `ghostscript`
* `tesseract-ocr`
* `tesseract-ocr-swe` (for swedish language support)

To install parseidon using `pip`, the following command is used:
```bash
pip install parseidon
```

### Run locally
To manage dependencies and running the program locally, [`uv`](https://github.com/astral-sh/uv) is recommended to use.

Install `uv` and run `uv sync --locked` to sync the enviroment with the `uv.lock` file.
Run Parseidon by running `uv run parseidon [...]`.

Update package versions with `uv sync --upgrade`.

To run unit-tests, run `uv run pytest`.

Parseidon can also be installed locally using `pip:

```bash
pip install -e .
```

### Docker
The program can either be installed and ran through bash, or ran with docker.

To run the program with docker, you must have the docker engine installed on your machine.
Then build the docker image with the following command from the projectroot:
```bash
docker build -t parseidon .
```
Followed by the following command to start the container:
```bash
docker run --rm -v /path/to/host_input_file_directory:/path/to/mount/host -i parseidon [arguments to program ...]

docker run --rm -v /home/user/Documents/important_documents/:/files -v ~/output:/out -i parseidon find -n 12 -r '/files/*' -o /out/find.pdf
```
Alternatively you can run the image in 'interactive mode':
```bash
docker run --rm -it --entrypoint /bin/bash parseidon
```

Usage inside the container works as stated under [Usage](usage/) and Testing respectively.

However, when running the program inside a Docker container, you are required to reside in the project root directory.

## Testing
Parseidon includes a test suite to ensure proper functionality in pattern matching, filtering out lexical items, usage of command line arguments and more.

To run the test suite use the following command from the project root:
```bash
pytest 
```
for increase verbosity the flags `-v` or `-vv` can be used.
