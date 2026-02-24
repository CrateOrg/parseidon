# Language data and resources
This document describes the process of gathering language resources and creation of the data tries.

Parseidon includes two data tries, where one consists of swedish vocabulary items and the other contains punctuations.

For attribution to the respective sources, please see [third party notices](../third_party_notices/THIRD_PARTY_NOTICES)

## Sources for language resources
Below follows a detailed presentation of the sources used to create the wordlists.

### Swedish wordlist sources
This wordlist mainly comprises of two lexical datasets from Språkbanken at the university of Gothenburg. A list of common swedish names was also collected from Språkbanken. The mentioned data can be found here:

[SALDO](https://spraakbanken.gu.se/en/resources/saldo)

[SALDOs morfologi](https://spraakbanken.gu.se/en/resources/saldom)

[Svenska namn 2023](https://spraakbanken.gu.se/resurser/swename2023)

Lastly, [swedish locations](https://www.scb.se/MI0810) were collected from SCB and added to the trie.

### Special characters
To prevent the filtermode from matching every single dot and comma, a separate punctuation trie was created. The trie is built upon the characters in the punctuation string, which is a part of the Python string module.

### English wordlist sources
Parseidon does not distribute a english trie. Instead a python script has been included for the creation of such. By executing the script, users are responsible for ensuring compliance with the licenses of the external sources referenced in the script.

To create the english trie, run the following from the project root:
```bash
python generate_english_trie.py
```

This will generate the file `src/parseidon/data/trie/english.marisa`.

## Create and update tries
The tries are built from wordlists in the form of plaintext files with one word entry per line.

To create a new trie file run the following command from the project root:

```bash
python create_trie.py <path/to/new_trie_file> <path/to/wordlist_file_1> ... <path/to/wordlist_file_N> 
```

Similarly run the following command to update an existing trie:

```bash
python update_trie.py <path/to/existing_trie_file> <path/to/wordlist_file_1> ... <path/to/wordlist_file_N> 
```
