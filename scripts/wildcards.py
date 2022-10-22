import os
import random
import sys

from modules import scripts

warned_about_files = {}
wildcard_dir = scripts.basedir()


class WildcardsScript(scripts.Script):
    def title(self):
        return "Simple wildcards"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def replace_wildcard(self, text):
        if " " in text or len(text) == 0:
            return text

        replacement_file = os.path.join(wildcard_dir, "wildcards", f"{text}.txt")
        if os.path.exists(replacement_file):
            with open(replacement_file, encoding="utf8") as f:
                return random.choice(f.read().splitlines())
        else:
            if replacement_file not in warned_about_files:
                print(f"File {replacement_file} not found for the __{text}__ wildcard.", file=sys.stderr)
                warned_about_files[replacement_file] = 1

        return text

    def process(self, p):
        p.extra_generation_params["Wildcard prompt"] = p.all_prompts[0]

        for i in range(len(p.all_prompts)):
            random.seed(p.all_seeds[i])

            prompt = p.all_prompts[i]
            prompt = "".join(self.replace_wildcard(chunk) for chunk in prompt.split("__"))
            p.all_prompts[i] = prompt
