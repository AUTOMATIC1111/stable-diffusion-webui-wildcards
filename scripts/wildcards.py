import os
import random

from modules import scripts


class WildcardsScript(scripts.Script):
    def title(self):
        return "Simple wildcards"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def replace_wildcard(self, text):
        if " " in text:
            return text

        replacement_file = os.path.join(scripts.basedir(), f"wildcards/{text}.txt")
        if os.path.exists(replacement_file):
            with open(replacement_file, encoding="utf8") as f:
                return random.choice(f.read().splitlines())

        return text

    def process(self, p):
        p.extra_generation_params["Wildcard prompt"] = p.all_prompts[0]

        for i in range(len(p.all_prompts)):
            random.seed(p.all_seeds[i])

            prompt = p.all_prompts[i]
            prompt = "".join(self.replace_wildcard(chunk) for chunk in prompt.split("__"))
            p.all_prompts[i] = prompt
