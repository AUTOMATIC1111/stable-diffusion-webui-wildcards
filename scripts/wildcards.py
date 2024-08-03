import os
import random
import sys

from modules import scripts, script_callbacks, shared

warned_about_files = {}
repo_dir = scripts.basedir()


class WildcardsScript(scripts.Script):
    def title(self):
        return "Simple wildcards"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def replace_wildcard(self, text, gen):
        if " " in text or len(text) == 0:
            return text

        wildcards_dir = shared.cmd_opts.wildcards_dir or os.path.join(repo_dir, "wildcards")

        replacement_file = os.path.join(wildcards_dir, f"{text}.txt")
        if os.path.exists(replacement_file):
            with open(replacement_file, encoding="utf8") as f:
                return gen.choice(f.read().splitlines())
        else:
            if replacement_file not in warned_about_files:
                print(f"File {replacement_file} not found for the __{text}__ wildcard.", file=sys.stderr)
                warned_about_files[replacement_file] = 1

        return text

    def replace_prompts(self, prompts, seeds):
        res = []

        for i, text in enumerate(prompts):
            gen = random.Random()
            gen.seed(seeds[0 if shared.opts.wildcards_same_seed else i])

            res.append("".join(self.replace_wildcard(chunk, gen) for chunk in text.split("__")))

        return res

    def process(self, p, *args):
        for attr, infotext_suffix in [
            ('all_prompts', 'prompt'), ('all_negative_prompts', 'negative prompt'),
            ('all_hr_prompts', 'hr prompt'), ('all_hr_negative_prompts', 'hr negative prompt'),
        ]:
            if all_original_prompts := getattr(p, attr, None):
                setattr(p, attr, self.replace_prompts(all_original_prompts, p.all_seeds))
                if shared.opts.wildcards_write_infotext and all_original_prompts[0] != getattr(p, attr)[0]:
                    if infotext_suffix.startswith("hr ") and p.extra_generation_params.get(f"Wildcard {infotext_suffix[3:]}", None) == all_original_prompts[0]:
                        continue  # don't overwrite original hr prompt is same as original first pass prompt
                    p.extra_generation_params[f"Wildcard {infotext_suffix}"] = all_original_prompts[0]


def on_ui_settings():
    shared.opts.add_option("wildcards_same_seed", shared.OptionInfo(False, "Use same seed for all images", section=("wildcards", "Wildcards")))
    shared.opts.add_option("wildcards_write_infotext", shared.OptionInfo(True, "Write original prompt to infotext", section=("wildcards", "Wildcards")).info("the original prompt before __wildcards__ are applied"))


script_callbacks.on_ui_settings(on_ui_settings)
