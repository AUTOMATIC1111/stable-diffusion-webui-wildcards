import os
import random
import gradio as gr
from modules import scripts, shared

WC_DIR = shared.cmd_opts.wildcards_dir or os.path.join(scripts.basedir(), "wildcards")

class BColors:
    OK = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    RED = "\033[91m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"

class WildcardsScript(scripts.Script):
    def __init__(self):
        self.cache = {}

    def title(self):
        return "Wildcards with Adetailer Support"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        elem_prefix = 'wildcard_' + ("img2img_" if is_img2img else "txt2img_")

        with gr.Row(elem_id=elem_prefix + "wildcard_adetailer_row"):
            with gr.Accordion("Wildcards for Adetailer", open=False, elem_id=elem_prefix + "wildcard_adetailer_accordion"):
                with gr.Row():
                    lock_enabled = gr.Checkbox(scale=2, label="Enable lock", value=False, elem_id=elem_prefix + "lock_enabled")
                with gr.Row():
                    lock_seed = gr.Number(scale=1, label="Seed", value=0, visible=False, elem_id=elem_prefix + "lock_seed")
                with gr.Row():
                    lock_method = gr.Radio(["Unlock", "Lock"], scale=1, label="Partial Unlock (lock all except:) or Lock (unlock all except:) Method", value="Unlock", visible=False, elem_id=elem_prefix + "lock_method")
                    lock_tiers = gr.Textbox(scale=2, label="Specified Tiers", value="#,#,#...", visible=False, elem_id=elem_prefix + "lock_tiers")
                with gr.Row():
                    outer_sep = gr.Textbox(label="Outer Separator", value="__", elem_id=elem_prefix + "outer_sep")
                    inner_sep = gr.Textbox(label="Inner Separator", value="_", elem_id=elem_prefix + "inner_sep")
                    iter_sym = gr.Textbox(label="Iteration Symbol", value="$", elem_id=elem_prefix + "iter_sym")

        outs = [lock_seed, lock_method, lock_tiers]
        lock_enabled.change(fn=lambda val: [gr.update(visible=val) for _ in outs], inputs=[lock_enabled], outputs=outs)

        return [lock_enabled, lock_seed, outer_sep, inner_sep, iter_sym, lock_method, lock_tiers]

    def file_exists(self, filename):
        return os.path.exists(os.path.join(WC_DIR, f"{filename}.txt"))

    def identify_wildcard_type(self, token, inner_sep, iter_sym):
        parts = token.split(inner_sep)

        if parts[-1].isdigit():
            line_num = int(parts[-1])
            base_file = parts[-2]
            mode = "I" if parts[0] == iter_sym else "L"
            return mode, base_file, line_num

        elif parts[0] == iter_sym:
            return "I", parts[1] if len(parts) > 1 else parts[0], 1

        elif parts[0].isdigit():
            return "T", parts[1] if len(parts) > 1 else parts[0], int(parts[0])

        return "N", token, 0

    def resolve_wildcard(self, base_file, mode, value, current_seed, color):

        if base_file not in self.cache:
            path = os.path.join(WC_DIR, f"{base_file}.txt")
            if not os.path.exists(path):
                print(f"{BColors.RED}[*] Wildcard missing: {base_file}.txt{BColors.RESET}")
                return base_file
            with open(path, encoding="utf8") as f:
                self.cache[base_file] = f.read().splitlines()

        lines = self.cache[base_file]
        if not lines: return ""
        count = len(lines)

        if mode == "L" or mode == "I":
            idx = (int(value) - 1) % count
        elif mode == "T":
            rng = random.Random(current_seed + (int(value) * 100))
            idx = rng.randint(0, count - 1)
        else:
            rng = random.Random(current_seed)
            idx = rng.randint(0, count - 1)

        left_side = f"{base_file}.txt Line {idx+1}"
        print (f"{color}[{mode}] {BColors.YELLOW}{left_side.ljust(35)} ► {lines[idx][:50]}{BColors.RESET}")
        return lines[idx]

    def process_single_prompt(self, prompt, current_seed, batch_offset, config, color, depth=0):
        if depth > 10 or config['outer_sep'] not in prompt:
            return prompt

        parts = prompt.split(config['outer_sep'])
        for i in range(1, len(parts), 2):
            token = parts[i]
            mode, base_file, val = self.identify_wildcard_type(token, config['inner_sep'], config['iter_sym'])

            if config['lock_enabled']:
                is_target = (config['lock_method'] == "Lock" and str(val) in config['lock_tiers']) or \
                            (config['lock_method'] == "Unlock" and str(val) not in config['lock_tiers'])
                if mode == "T" and is_target:
                    current_seed = config['lock_seed']

            res_val = (batch_offset + val) if mode == "I" else val
            parts[i] = self.resolve_wildcard(base_file, mode, res_val, current_seed, color)

        final_prompt = "".join(parts)
        if config['outer_sep'] in final_prompt:
            return self.process_single_prompt(final_prompt, current_seed, batch_offset, config, color, depth + 1)
        return final_prompt

    def process(self, p, lock_enabled, lock_seed, outer_sep, inner_sep, iter_sym, lock_method, lock_tiers):
        if not hasattr(p, 'original_prompts'):
            if not hasattr(p, '_ad_inner'):
                self.cache = {}
                self.anchor_seed = p.all_seeds[0]
                self.total_batch_size = p.n_iter * p.batch_size
                p.original_prompts = list(p.all_prompts)
                p.original_negative_prompts = list(p.all_negative_prompts)
                p.original_hr_prompts = getattr(p, 'all_hr_prompts', None)
                p.original_hr_negatives = getattr(p, 'all_hr_negative_prompts', None)
                if p.original_prompts:
                    p.extra_generation_params["Wildcard Pos"] = p.original_prompts[0]
                if p.original_negative_prompts:
                    p.extra_generation_params["Wildcard Neg"] = p.original_negative_prompts[0]
                if p.original_hr_prompts:
                    p.extra_generation_params["Wildcard HR Pos"] = p.original_hr_prompts[0]
                if p.original_hr_negatives:
                    p.extra_generation_params["Wildcard HR Neg"] = p.original_hr_negatives[0]
                print (f"{BColors.YELLOW}[N] Normal [T] Tiered [I] Iterative [L] Locked {BColors.OK}[*] POS {BColors.RED}[*] NEG {BColors.CYAN}[*] HR POS {BColors.PURPLE}[*] HR NEG{BColors.RESET}")
                print (f"{BColors.YELLOW}[*] Batchsize: {self.total_batch_size}{BColors.RESET}")

        config = {
            'outer_sep': outer_sep, 'inner_sep': inner_sep, 'iter_sym': iter_sym,
            'lock_enabled': lock_enabled, 'lock_seed': lock_seed,
            'lock_method': lock_method, 'lock_tiers': [t.strip() for t in lock_tiers.split(",")]
        }

        prompt_map = [
            ('pos', p.all_prompts, BColors.OK),
            ('neg', p.all_negative_prompts, BColors.RED),
            ('hr_pos', getattr(p, 'all_hr_prompts', None), BColors.CYAN),
            ('hr_neg', getattr(p, 'all_hr_negative_prompts', None), BColors.PURPLE),
        ]

        for j in range(len(p.all_seeds)):
            current_seed = p.all_seeds[j]
            batch_offset = (current_seed - self.anchor_seed)
            print (f"{BColors.YELLOW}[*] Current Seed: {current_seed}{BColors.RESET}")
            for _, prompt_list, color in prompt_map:
                if not prompt_list:
                    continue
                prompt_list[j] = self.process_single_prompt(prompt_list[j], current_seed, batch_offset, config, color)
