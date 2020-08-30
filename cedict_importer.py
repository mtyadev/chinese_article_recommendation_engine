import os
import re

def cedict_importer(raw_cedict):
    """
    https://cc-cedict.org/wiki/ will be used as Chinese English Dictionary
    This function cleans the raw cedict_ts.u8 file and converts it into a python dictionary

    The first entries in cedict_ts just contain some metadata, which can be skipped

    # Structure of cedict_ts Entries is as follows:

    一對兒 一对儿 [yi1 dui4 r5] /a pair/a couple/\n'
    <Traditional Characters> <Simplified Characters> [<Pinyin>] /<English Translation>

    # Converting this into cleaned dictionary with following structure

    一对儿: (yi1 dui4 r5, a pair/a couple)
    <Simplified Characters>: (<Pinyin>, <English Translation>)
    """

    cleaned_cedict = {}

    for entry in raw_cedict[30:]:
        try:
            cleaned_entry = re.search(r"(^.*)( )(.*)( )(\[)(.*)(\])( )(/)(.*)", entry)
            cleaned_cedict.update(
                {cleaned_entry.groups()[2].encode("utf-8"): (cleaned_entry.groups()[5], cleaned_entry.groups()[9].replace("\n", ""))})
        except BaseException:
            print("Dictionary could not be processed. Aborting.")
            quit()
    return cleaned_cedict


cedict_ts = './chinese_english_dictionary/cedict_ts.u8'

with open(cedict_ts, encoding="utf8") as f:
    cedict = f.readlines()

cleaned_cedict = cedict_importer(cedict)


