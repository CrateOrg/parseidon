import yaml

patterns = {}

base_dir = "./src/parseidon/data/peg_files/"

with open(base_dir + "peg_grammars_source.yaml", "r") as file:
    raw_patterns = yaml.safe_load(file)

grammars = {}


def name_exists(name):
    for t, _ in grammars.items():
        if grammars[t].get(name) is not None:
            return True
    return False


for t, definitions in raw_patterns.items():
    grammars[t] = {}
    for d in definitions:
        if len(d) != 1:
            raise RuntimeError()
        name, definition = list(d.items())[0]
        if name != "mult" and name_exists(name):
            raise RuntimeError(f"Duplicate keys in type: '{t}' for name '{name}'")
        grammars[t][name] = f"{definition}"

# Write all grammars
with open(base_dir + "peg_grammars.txt", "w") as all_grammars:
    for t, d in grammars.items():
        # print(f"Type: {t}")
        for name, definition in d.items():
            if t != "General" and name == "mult":
                continue  # Do not write individual mults to complete grammar
            # print(f"{name} = {definition}")
            all_grammars.write(f"{name} = {definition}\n")
        all_grammars.write("\n")

# Write individual grammars
for t, d in grammars.items():
    if t == "General":
        continue
    with open(f"{base_dir}individual_pegs/{t.lower()}_peg.txt", "w") as ind_grammar:
        # Write individuals
        for name, definition in d.items():
            # print(f"{name} = {definition}")
            ind_grammar.write(f"{name} = {definition}\n")
        ind_grammar.write("\n")
        # Write generals
        for name, definition in grammars["General"].items():
            if name == "mult":
                continue  # Do not write general mult to individual files
            ind_grammar.write(f"{name} = {definition}\n")
        ind_grammar.write("\n")
