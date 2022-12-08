import os
import random
import sys

from modules import scripts, script_callbacks, shared
from modules.script_callbacks import ImageSaveParams

warned_about_files = {}
wildcard_dir = scripts.basedir()
wildcard_sort_name = ""


class WildcardsScript(scripts.Script):

    def title(self):
        return "Sorted wildcards"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def replace_wildcard(self, text, gen):
        if " " in text or len(text) == 0:
            return text, False

        replacement_file = os.path.join(
            wildcard_dir, "wildcards", f"{text}.txt")
        if os.path.exists(replacement_file):
            with open(replacement_file, encoding="utf8") as f:
                return gen.choice(f.read().splitlines()), True
        else:
            if replacement_file not in warned_about_files:
                print(
                    f"File {replacement_file} not found for the __{text}__ wildcard.", file=sys.stderr)
                warned_about_files[replacement_file] = 1

        return text

    def wildcard_sort_enabled(self):
        # check if all wildcard sort settings are enabled
        return shared.opts.enable_wildcard_sort and shared.opts.wildcard_key

    def generate_wildcard_prompt_no_sort(self, prompt, gen):
        # default functionality
        return "".join(self.replace_wildcard(chunk, gen) for chunk in prompt.split("__"))

    def get_wildcard_sort_name(self, prompt, gen):
        # gets the value of the wildcard being sorted by
        # will only attempt to find the first instance of said wildcard
        global wildcard_sort_name
        wildcard_sort_name = ""
        new_prompt = ""
        for chunk in prompt.split("__"):
            replace_val, is_wildcard = self.replace_wildcard(chunk, gen)
            new_prompt += replace_val
            if shared.opts.wildcard_key == chunk and is_wildcard:
                wildcard_val = self.clean_wildcard(replace_val)
                wildcard_sort_name = wildcard_val if not wildcard_sort_name else f"{wildcard_sort_name} and {wildcard_val}"
        return new_prompt

    def clean_wildcard(self, wildcard_val):
        return wildcard_val.replace('\\', '').replace('/', '-')

    def process(self, p):
        original_prompt = p.all_prompts[0]
        for i in range(len(p.all_prompts)):
            gen = random.Random()
            gen.seed(p.all_seeds[0 if shared.opts.wildcards_same_seed else i])

            prompt = p.all_prompts[i]
            prompt = self.get_wildcard_sort_name(prompt, gen) if self.wildcard_sort_enabled(
            ) else self.wildcard_sort_enabled(prompt, gen)

            p.all_prompts[i] = prompt

        if original_prompt != p.all_prompts[0]:
            p.extra_generation_params["Wildcard prompt"] = original_prompt


def create_if_not_exist(dirs: list):
    # creates the directory for sorting
    for dir in dirs:
        isExist = os.path.exists(dir)
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(dir)


def on_before_image_saved(params: ImageSaveParams):
    # callback sets image path to the new directory if sort is enabled
    if shared.opts.enable_wildcard_sort and wildcard_sort_name and shared.opts.wildcard_key:
        base_name = os.path.basename(params.filename)
        new_dir = params.filename.replace(
            base_name, f"/sorted/{shared.opts.wildcard_key}s/{wildcard_sort_name}")
        create_if_not_exist([new_dir])
        params.filename = os.path.realpath(f"{new_dir}/{base_name}")
    return params


def on_ui_settings():
    shared.opts.add_option("wildcards_same_seed", shared.OptionInfo(
        False, "Use same seed for all images", section=("wildcards", "Wildcards")))
    shared.opts.add_option("enable_wildcard_sort", shared.OptionInfo(
        False, "Enable wildcard Sort", section=("wildcards", "Wildcards")))
    shared.opts.add_option("wildcard_key", shared.OptionInfo(
        "character", "Wildcard to sort image by", section=("wildcards", "Wildcards")))


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_before_image_saved(on_before_image_saved)
