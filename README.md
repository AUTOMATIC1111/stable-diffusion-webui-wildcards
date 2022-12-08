# Wildcards with sorting
An extension version of a script from https://github.com/jtkelm2/stable-diffusion-webui-1/blob/main/scripts/wildcards.py

Allows you to use `__name__` syntax in your prompt to get a random line from a file named `name.txt` in the wildcards directory.

Allows you to sort generated images into folders based on a specified wildcard. 

When enabled, `character` will look for the first instance of `__character__` in a prompt and save images into the directory `/sorted/characters/{charactername}.{extension}`
Providing an invalid wildcard will save to the default save path.
