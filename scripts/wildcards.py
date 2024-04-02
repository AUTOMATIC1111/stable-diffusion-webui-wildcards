import os
import random
import sys
import re
import math

from modules import scripts, script_callbacks, shared

warned_about_files = {}
repo_dir = scripts.basedir()

class bcolors:
    OK = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

class WildcardsScript(scripts.Script):
    def title(self):
        return "Simple wildcards"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def replace_wildcard(self, text, rlist, rseed):
        if " " in text or len(text) == 0:
            return text

        wildcards_dir = shared.cmd_opts.wildcards_dir or os.path.join(repo_dir, "wildcards")

        replacement_file = os.path.join(wildcards_dir, f"{text}.txt")
        if os.path.exists(replacement_file):
            with open(replacement_file, encoding="utf8") as f:
                textarray = []
                textarray = f.read().splitlines()
                nline = round(len(textarray) * rlist)
                print(bcolors.YELLOW + f"[-] {nline:02d} - {textarray[nline-1][:80]}" + bcolors.RESET)
            return textarray[nline-1]

        else:
            if replacement_file not in warned_about_files:
                print(f"File {replacement_file} not found for the _{text}_ wildcard.", file=sys.stderr)
                warned_about_files[replacement_file] = 1
        return text

    def process(self, p):
        original_prompt = p.all_prompts[0]
        global original_seed
        try:
            original_seed
        except NameError:
            original_seed = p.all_seeds[0]

        for j, text in enumerate(p.all_prompts):
            random.seed(original_seed if shared.opts.wildcards_same_seed_batch else p.all_seeds[j])
            rand_list = []
            n=20
            for i in range(n):
                rand_list.append(random.random())
            text = text.split("__")
            i = 0
            while i < len(text):    
                line = str(text[i])
                if line != " " or line != 0:
                    x = 0
                    for x in range(20):
                        if line.startswith(str(x) + "_"):
                            if len(str(x)) == 2:
                                line = line[3:]
                            else:
                                line = line[2:]
                            text[i] = self.replace_wildcard(line, rand_list[x], p.all_seeds[j])
                i = i + 1
                
            p.all_prompts[j] = ''.join(text)
            if getattr(p, 'all_hr_prompts', None) is not None:
                p.all_hr_prompts[j] = ''.join(text) 

        if original_prompt != p.all_prompts[0]:
            p.extra_generation_params["Wildcard prompt"] = original_prompt

def on_ui_settings():
    shared.opts.add_option("wildcards_same_seed_batch", shared.OptionInfo(False, "Keep the same wildcard seed generation from the first image you generate until this setting is turned off. Compatible with Adetailer now.", section=("wildcards", "Wildcards")))


script_callbacks.on_ui_settings(on_ui_settings)