import io
import os
import re
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "local.nict_jle/utils"))) # Remember to add this line to avoid "module no exist" error

from tqdm import tqdm
from espnet.utils.cli_utils import strtobool
from utilities import (
    open_utt2value
)

def argparse_function():
    parser = argparse.ArgumentParser()

    parser.add_argument("--assign_native_sst",
                        default=10,
                        type=int)

    parser.add_argument("--input_mapping_file_path",
                        default='data/trn/text_list',
                        type=str)

    parser.add_argument("--input_text_list_file_path",
                        default='data/trn/text_list',
                        type=str)

    parser.add_argument("--output_scores_file_path",
                        default='CEFR_LABELS_PATH/trn_sst_scores.txt',
                        type=str)

    args = parser.parse_args()

    return args

def get_token(raw_html):
    regex = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(regex, '', raw_html)
    selected_tags_list = re.findall('(<.*?>)', raw_html)

    return cleantext, selected_tags_list

if __name__ == '__main__':

    # argparse
    args = argparse_function()

    # variable
    assign_native_sst = args.assign_native_sst
    input_text_list_file_path = args.input_text_list_file_path
    input_mapping_file_path = args.input_mapping_file_path
    output_scores_file_path = args.output_scores_file_path
    mapping_dict = open_utt2value(input_mapping_file_path)
    text_file_path_dict = open_utt2value(input_text_list_file_path)
    
    # retrieve sst score
    utt2stt_dict = {}
    for i, (utt_id, utt_text_file_path) in enumerate(tqdm(text_file_path_dict.items())):

        # variable
        sst_level_tags_list = []

        # for Native
        if utt_id[0] == 'N':
            utt2stt_dict[utt_id] = assign_native_sst
            continue

        with io.open(utt_text_file_path, 'rb') as f:
            for line in f.readlines():
                line = line.decode('utf-8', 'ignore').strip().replace('\n','').replace('\r','')
                if line == '':
                    continue

                # filter out the end tag toekns
                if line[:11] == "<SST_level>":
                    sst_level_tags_list.append(line)
                    break

        for sst_tag in sst_level_tags_list:
            sst_score, _ = get_token(sst_tag)
            utt2stt_dict[utt_id] = sst_score

    # save
    with io.open(output_scores_file_path, 'w') as f:
        for utt_id, sst_score in utt2stt_dict.items():
            f.write("{} {}\n".format(utt_id, sst_score))