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

    parser.add_argument("--input_scores_file_path",
                        default='data/trn/text_list',
                        type=str)

    parser.add_argument("--input_mapping_file_path",
                        default='data/trn/text_list',
                        type=str)

    parser.add_argument("--output_scales_file_path",
                        default='CEFR_LABELS_PATH/trn_sst_scores.txt',
                        type=str)

    args = parser.parse_args()

    return args

if __name__ == '__main__':

    # argparse
    args = argparse_function()

    # variable
    input_scores_file_path = args.input_scores_file_path
    input_mapping_file_path = args.input_mapping_file_path
    output_scales_file_path = args.output_scales_file_path
    mapping_dict = open_utt2value(input_mapping_file_path)
    utt2stt_dict = open_utt2value(input_scores_file_path)
    
    # retrieve sst score
    utt2scale_dict = {}
    for utt_id, sst_score in tqdm(utt2stt_dict.items()):
        
        utt2scale_dict.setdefault(
            utt_id,
            mapping_dict[sst_score]
        )

    # save
    with io.open(output_scales_file_path, 'w') as f:
        for utt_id, scale in utt2scale_dict.items():
            f.write("{} {}\n".format(utt_id, scale))