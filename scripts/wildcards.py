import os
import random
import sys
from pathlib import Path
from modules import scripts, script_callbacks, shared

warned_about_files = {}
wildcard_dir = scripts.basedir()


class WildcardsScript(scripts.Script):
    def title(self):
        return "Simple wildcards"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def replace_wildcard(self, text, gen):
        if " " in text or len(text) == 0:
            return text

        replacement_file_dir = Path(wildcard_dir) / "wildcards"
        replacement_file = self.search_wildcard_file(text, replacement_file_dir)
        if replacement_file:
            with open(replacement_file, encoding="utf8") as f:
                return gen.choice(f.read().splitlines())
        else:
            if replacement_file not in warned_about_files:
                warned_about_files[replacement_file] = 1

        return text

    def search_wildcard_file(self, filename: str, replacement_file_dir: Path):
        for prompt_file in replacement_file_dir.iterdir():
            if prompt_file.is_file and prompt_file.stem == filename:
                return prompt_file
            elif prompt_file.is_dir() and shared.opts.wildcards_recursive:
                prompt_file = self.search_wildcard_file(filename, prompt_file)
                if prompt_file:
                    return prompt_file

    def process(self, p):
        original_prompt = p.all_prompts[0]
        for i in range(len(p.all_prompts)):
            gen = random.Random()
            gen.seed(p.all_seeds[0 if shared.opts.wildcards_same_seed else i])

            prompt = p.all_prompts[i]
            prompt = "".join(
                self.replace_wildcard(chunk, gen) for chunk in prompt.split("__")
            )
            p.all_prompts[i] = prompt

        if original_prompt != p.all_prompts[0]:
            p.extra_generation_params["Wildcard prompt"] = original_prompt
        if shared.opts.wildcards_negative_prompts:
            negative_prompt = p.all_negative_prompts[0]

            for i in range(len(p.all_negative_prompts)):
                gen = random.Random()
                gen.seed(p.all_seeds[0 if shared.opts.wildcards_same_seed else i])

                prompt = p.all_negative_prompts[i]
                prompt = "".join(
                    self.replace_wildcard(chunk, gen) for chunk in prompt.split("__")
                )
                p.all_negative_prompts[i] = prompt

            if original_prompt != p.all_negative_prompts[0]:
                p.extra_generation_params["Wildcard negative prompt"] = negative_prompt


def on_ui_settings():
    shared.opts.add_option(
        "wildcards_same_seed",
        shared.OptionInfo(
            False, "Use same seed for all images", section=("wildcards", "Wildcards")
        ),
    )
    shared.opts.add_option(
        "wildcards_recursive",
        shared.OptionInfo(
            True,
            "Recursively search for wildcards",
            section=("wildcards", "Wildcards"),
        ),
    )
    shared.opts.add_option(
        "wildcards_negative_prompts",
        shared.OptionInfo(
            True,
            "Use wildcards for negative prompts",
            section=("wildcards", "Wildcards"),
        ),
    )


script_callbacks.on_ui_settings(on_ui_settings)
