## Wildcards with Adetailer Support

#### Supports:
* ***All Prompts***: Positive \ Negative \ HR Postive \ HR Negative \ Adetailer Positive \ Adetailer Negative
* ***Nested Wildcards*** inside of wildcard text files. (ie. hair.txt line 1: `__20_hairstyle__ __21_haircolor__ hair` makes for a cleaner looking prompt where you only need one wildcard. `__0_hair__`. Be careful when nesting a wildcard inside of itself.)

#### Features
* ***Tiered Wildcards*** that share the same random generation based on the seed. (ie. `__0_wildcard__` up to `__99_wildcard__`)
* ***Iterative wildcards*** that go through wildcard text files line by line in a batch. (ie. `__$_wildcard__`)
* ***Locking wildcards*** to specific lines. (ie. `__0_wildcard_9__`/`__wildcard_9__` in which in all cases the ninth line from the wildcard will be chosen. for `__$_wildcard_9__`, it will lock to the ninth line when generating a single image, but in a batch it will start to iterate starting from that line instead.)
* Depreciated vanilla use. (ie. `__wildcard__` completely random, remaking the same seed will never be the same, haha.)
#### Menu
* Locking random seed generation to a specific seed.
* Changing inner and outer separators and iterative symbol, for if you have compatibility issues.
<img width="1740" height="334" alt="wcad" src="https://github.com/user-attachments/assets/72c49e9c-dc1c-4e55-87b7-e0bc956266a5" />

#### Tiered Wildcards: `__0_wildcard__` up to `__99_wildcard__`
* The number represents a linked random seed generation. So `__0_wildcard__` will output the same result in any prompt. As long as the wildcards have the same number of lines, can link different wildcards with each other. (ie. `__5_one__` and `__5_two__` where one.txt and two.txt both have 50 lines of text will always pick the same line result.

#### Incompatibility:
- Do not use `_`character in wildcard txt file names. (or whichever INNER separator you input in the menu, the inner separator will conflict with any instances of it in wildcard text file names.)
- Do not use `__` anywhere else in the prompt. (or whichever OUTER separator you input in the menu, the outer separator will conflict with any instances of it in the prompt text.)
- Does not work properly with Batch Size. Use Batch Count instead when making batches.

#### Install
To install from webui, go to `Extensions -> Install from URL`, paste `https://github.com/uorufu/stable-diffusion-webui-wildcards-adetailer`
into URL field, and press Install.

![Screenshot](https://raw.githubusercontent.com/uorufu/stable-diffusion-webui-wildcards-adetailer/refs/heads/master/ss.png)

