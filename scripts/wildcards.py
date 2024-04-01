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

    def get_digit(self, number, n):
        return number // 10**n % 10

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def replace_wildcard(self, text, gen, genseed):
        if " " in text or len(text) == 0:
            return text

        wildcards_dir = shared.cmd_opts.wildcards_dir or os.path.join(repo_dir, "wildcards")

        replacement_file = os.path.join(wildcards_dir, f"{text}.txt")
        if os.path.exists(replacement_file):
            with open(replacement_file, encoding="utf8") as f:
                textarray = []
                textarray = f.read().splitlines()
                if gen > len(textarray):
                    genfloor = math.floor(gen / len(textarray))
                    gen = gen - (len(textarray) * genfloor)
                    print(bcolors.YELLOW + f"[seed:{genseed}][line:{gen + 1}]: {textarray[gen][:40]}" + bcolors.RESET)
                    return textarray[gen]
                else:
                    print(bcolors.YELLOW + f"[seed:{genseed}][line:{gen + 1}]: {textarray[gen][:40]}" + bcolors.RESET)
                    return textarray[gen]

        else:
            if replacement_file not in warned_about_files:
                print(f"File {replacement_file} not found for the _{text}_ wildcard.", file=sys.stderr)
                warned_about_files[replacement_file] = 1

        return text

    def process(self, p):
        original_prompt = p.all_prompts[0]
        
        for j, text in enumerate(p.all_prompts):
            genseed = p.all_seeds[j]
            gen = self.get_digit(p.all_seeds[j], 3) + 33 * self.get_digit(p.all_seeds[j], 1) + 33 * self.get_digit(p.all_seeds[j], 0)
            text = text.split("__")
            i = 0
            while i < len(text):    
                line = str(text[i])
                if line != " " or line != 0:
                    x = 0
                    for x in range(11):
                        if line.startswith(str(x) + "_"):
                            line = line[2:]
                            finalgen = gen + ( x * 11 )
                            text[i] = self.replace_wildcard(line, finalgen, genseed)
                i = i + 1

            p.all_prompts[j] = ''.join(text)
            if getattr(p, 'all_hr_prompts', None) is not None:
                p.all_hr_prompts = self.replace_prompts(p.all_hr_prompts, i, gen)

        if original_prompt != p.all_prompts[0]:
            p.extra_generation_params["Wildcard prompt"] = original_prompt
