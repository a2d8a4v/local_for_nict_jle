import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "local.nict_jle/utils"))) # Remember to add this line to avoid "module no exist" error

from utilities import (
    open_utt2value
)
from defined_scales import (
    mapping_dict
)


def argpare_function():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_text_file_path",
                        default="data/train/text",
                        type=str)

    parser.add_argument("--words_file_path",
                        default="Librispeech-model-mct-tdnnf/data/lang_t3/words.txt",
                        type=str)

    args = parser.parse_args()
    return args

def opentext(file):
    s = set()
    with open(file, "r") as f:
        for l in f.readlines():
            for word in l.split():
                s.add(word.lower())
    return list(s)

def openwords(file):
    s = dict()
    with open(file, "r") as f:
        for l in f.readlines():
            s.setdefault(l[0].lower(), [])
    return s


if __name__ == '__main__':

    args = argpare_function()

    # variables
    input_text_file_path = args.input_text_file_path
    words_file_path = args.words_file_path

    # text
    words_list = opentext(input_text_file_path)

    # words
    words_dict = opentext(words_file_path)

    oov_words_list = list(set([word for word in words_list if word not in words_dict]))

    print(
        "{} words not in dictionary {}".format(
            len(oov_words_list),
            words_file_path
        )
    )

    print(
        oov_words_list
    )