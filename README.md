#### Wildcards Adetailer fix

An personal fork I made to make wildcards extension work better with Adetailer.

## Changes from main extension:

1. Now, order does not matter and you can add any wildcard to adetailer prompt without it generating a different item. 

2. Also, I have made it so there can be tiers. So you can link certain wildcard txt files to each other so all of them will grab the same line number in the TXT.
    The proper use for this fork is by using `__0_name__` up to `__9_name__` to pull from **name.txt** in the wildcards directory. (the leading number **should not** be on the txt filename.)
    Every wildcard using the same leading number will use the same random generation (and if the txt files have an equal amount of lines, will pick the same line number.

This is great when you want to add a lengthy bit of prompt into the main prompt but only want a small part of the same prompt in adetailer prompt. Now you can just seperate them into two txt files and use the same leading number like `__0_partone__ __0_parttwo__` in your main prompt and only `__0_partone__` in adetailer. If both partone.txt and parttwo.txt have the same number of lines, they will both get the same linenumber.

3. For the best randomization, unless you need to use the same tier, it is best to use as many tiers as possible. So `__0_name__ __1_name__ __2_name__` etc. If you need more than 10 wildcards in your prompt, you will have to combine them into other tiers. But note that if those txt files have the same or very similar amount of lines, you might end up generating similar prompts between the two. Ideally, tiers should only be utilized to pull apart a smaller part of a longer prompt for adetailer prompt purposes.

Small issue, the same seed setting will not work with this fork. As it is not something I personally use, I didn't bother with it.

Just like the main extension, make sure you use spaces at the beginning and end of newlines.

The pseudo random method is random enough, but of course each seed will always create the same prompt, as the pseudo random method is based off of the seed.

## Install
To install from webui, go to `Extensions -> Install from URL`, paste `https://github.com/uorufu/stable-diffusion-webui-wildcards-adetailer`
into URL field, and press Install.
