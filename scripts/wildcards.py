import os
import random
import sys
import gradio as gr

from modules import scripts, script_callbacks, shared

warned_about_files = {}
repo_dir = scripts.basedir()

class bcolors:
    OK = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

class WildcardsScript(scripts.Script):
    def title(self):
        return "Simple wildcards for adetailer"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        elem = 'wildcard_'+("img2img_" if is_img2img else "txt2img_")
        with gr.Row(elem_id=elem+"wildcard_adetailer_row"):
            with gr.Accordion("Wildcards for adetailer", open=False, elem_id=elem+"wildcard_adetailer_accordion"):
                with gr.Row():
                    wca_enable = gr.Checkbox(label="Enable locking of wildcards randomization to a specific seed", value=False, elem_id=elem+"enable", interactive=True)
                with gr.Row():
                    wca_seed = gr.Number(precision=0, label="Which seed to lock", interactive=False, elem_id=elem+"seed")
                with gr.Row():
                    wca_linelock = gr.Number(value=1, precision=0, label="Specific iterative line number to lock", interactive=False, elem_id=elem+"linelock")
                with gr.Row():
                    wca_iterative_unlock = gr.Checkbox(label="Don't lock iterative wildcards", value=False, elem_id=elem+"iterativeunlock", interactive=False)
                with gr.Accordion('More info about Wildcards for adetailer',open=False,elem_id=elem+'help'):
                    gr.Markdown('''

# Methods:

- Normal use: `__wildcard__`
- Tiered wildcards: `__0_wildcard__` up to `__99_wildcard__`
- Iterative wildcard: `__$_wildcard__`


## Random generation method:

The random generation method just uses a seeding method based on the generation seed. Which means that every seed number will always have the same random results. A float between 0-1 will be randomly generated and that will be multiplied by the length of your txt file in order to decide which line to choose. 


## Explanation of methods:

- Normal use is only really still here because people might be used to it. Personally I recommend using tiered wildcards only. The random generation for normal wildcards use a total of 100 unshared random seeds. So if you use more than 100 wildcards (lol), seeds will get reused.
  Note however that normal wildcards are order sensative when it comes to adetailer, unlike tiered wildcards. (first normal wildcard in mainprompt shares same random generation as first normal wildcard in adetailer.)

- Tiered use is a great way to split wildcards into parts if you need to use only parts in adetailer prompt or want to seperate lora's. If you have three text files with 20 lines each and put them all in the same tier, let's say `__4_lora__` `__4_body__` in main prompt and `__4_face__` in adetailer prompt, then every time the same line number will be chosen for each of these wildcards.
  You can use up to 100 different tiers `(0 - 99)` which each having their own random generation seeding.
  Tiered wildcards are not order sensative. everything on the same tier shares the same random generation no matter what prompt it is in.

- Iterative wildcard is a way to have a wildcard go through the lines one by one instead of randomly choosing one. This can be great for making large batches and you want one result for each line in your wildcard text file.


## Seed locking:

The seed locking feature is for if you have a particular result and want to generate more of the same image with that result. You can manually input the seed you want to lock and then generate images in other seeds based on the random generation of the seed you locked.

You can enable iterative wildcards to work while locking the random generation by selecing that option. You can specify the linenumber as a starting point of the iterative wildcard. Default this is 1.

Save your wildcards in the wildcards folder. To avoid issues, use only a-z in your txt filename.
                    ''')
        outs = [wca_seed,wca_iterative_unlock,wca_linelock]
        wca_enable.change(fn=lambda value:[gr.update(interactive=value) for _ in outs],inputs=[wca_enable],outputs=outs, queue=False)
        return [wca_enable, wca_seed, wca_iterative_unlock, wca_linelock]

    def replace_wildcard(self, text, rlist, replacement_file):
        with open(replacement_file, encoding="utf8") as f:
            textarray = []
            textarray = f.read().splitlines()
            nline = round(len(textarray) * rlist)
            if rlist >= 1:
                nline = rlist
                if rlist > len(textarray):
                    nline = rlist % len(textarray)
                    if nline == 0:
                        nline = len(textarray)
            print(bcolors.OK + "[*] " + bcolors.RESET + bcolors.YELLOW + f"Line {nline:02d} " + ( f"{text}.txt" if len(text)<15 else f"{text[:14]}_.txt" ) + ( "\t\t" if len(text)<9 else "\t" ) + f"► {textarray[nline-1][:100]}" + bcolors.RESET)
        return textarray[nline-1]

    def process(self, p, wca_enable, wca_lock_seed, wca_iterative_unlock, wca_linelock):
        original_prompt = p.all_prompts[0]
        wildcards_dir = shared.cmd_opts.wildcards_dir or os.path.join(repo_dir, "wildcards")
        global original_seed
        try:
            original_seed
        except NameError:
            original_seed=p.all_seeds[0]
        if p.n_iter > 1 or p.batch_size > 1:
            if original_seed != p.all_seeds[0]:
                original_seed=p.all_seeds[0]
            print (bcolors.OK + f"[*] Batchsize {(p.n_iter * p.batch_size)}" + bcolors.RESET)
            print (bcolors.OK + f"[*] Starting Seed: {original_seed}" + bcolors.RESET)
        for j, text in enumerate(p.all_prompts):
            print (bcolors.OK + "[*] " + bcolors.RESET + bcolors.YELLOW + f"Current Seed: {p.all_seeds[j]}" + bcolors.RESET)
            random.seed(wca_lock_seed if wca_enable == True and wca_lock_seed > 0 else p.all_seeds[j])
            rand_list_tiers = []
            rand_list = []
            for i in range(100):
                rand_list_tiers.append(random.random())
                rand_list.append(random.random())
            fixedline = 1
            if wca_enable == True and wca_iterative_unlock == True or wca_enable == False:
                if len(p.all_seeds) > 1 and p.all_seeds[j] > original_seed:
                    fixedline = p.all_seeds[j] - original_seed + 1
                if p.all_seeds[0] > original_seed:
                    fixedline = p.all_seeds[0] - original_seed + 1
            if wca_enable == True and wca_iterative_unlock == False:
                fixedline = wca_linelock
            text = text.split("__")
            i = 0
            n = 0
            while i < len(text):
                line = str(text[i])
                if " " not in line and len(line) > 0:
                    replacement_file = os.path.join(wildcards_dir, f"{line}.txt")
                    if os.path.exists(replacement_file):      
                        if n > 99:
                            n = n % 99
                        text[i] = self.replace_wildcard(line, rand_list[n], replacement_file)
                        n = n + 1
                    if line.startswith("$_"):
                        line = line[2:]
                        replacement_file = os.path.join(wildcards_dir, f"{line}.txt")
                        if os.path.exists(replacement_file):
                            text[i] = self.replace_wildcard(line, fixedline, replacement_file)
                    for x in range(100):
                        if line.startswith(str(x) + "_"):
                            if x > 9:
                                line = line[3:]
                            else:
                                line = line[2:]
                            replacement_file = os.path.join(wildcards_dir, f"{line}.txt")
                            if os.path.exists(replacement_file):
                                text[i] = self.replace_wildcard(line, rand_list_tiers[x], replacement_file)
                    if len(p.all_seeds) > 1:
                        p.all_prompts[j] = ''.join(text)
                    else:
                        p.all_prompts[0] = ''.join(text)
                i = i + 1

        if getattr(p, 'all_hr_prompts', None) is not None:
            p.all_hr_prompts[j] = ''.join(text)

        if original_prompt != p.all_prompts[0]:
            p.extra_generation_params["Wildcard prompt"] = original_prompt
