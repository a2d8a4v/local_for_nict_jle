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

mapping_dict = {
    0: 0,
    'preA1': 1,
    'A1': 2,
    'A1+': 3,
    'A2': 4,
    'A2+': 5,
    'B1': 6,
    'B1+': 7,
    'B2': 8
}

def argparse_function():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_sst_label_file_path",
                        default='data/trn/text_list',
                        type=str)

    parser.add_argument("--input_scale_label_file_path",
                        default='CEFR_LABELS_PATH/trn_sst_scores.txt',
                        type=str)

    args = parser.parse_args()

    return args

if __name__ == '__main__':

    # argparse
    args = argparse_function()

    # variable
    input_sst_label_file_path = args.input_sst_label_file_path
    input_scale_label_file_path = args.input_scale_label_file_path
    utt2sst_dict = open_utt2value(input_sst_label_file_path)
    utt2cefr_dict = open_utt2value(input_scale_label_file_path)
    utt2cefr_dict = { utt_id:mapping_dict[scale] for utt_id, scale in utt2cefr_dict.items() }
    saved_heap_tree = {}

    # generate heap tree
    # use the sst score as the root node and save leaves from cefr_dict
    for utt_id, score in utt2sst_dict.items():
        saved_heap_tree.setdefault(score, []).append(
            utt2cefr_dict[utt_id]
        )
    
    # check is mono-linear, which is one-to-one or one-to-many
    saved_heap_tree = dict(sorted(saved_heap_tree.items()))
    saved_range_list = []
    for i, saved_scales_idxs_list in saved_heap_tree.items():
        max_value = max(saved_scales_idxs_list)
        min_value = min(saved_scales_idxs_list)
        saved_range_list.append([min_value, max_value])

    previous_next_min_value = -1
    previous_this_max_value = -1
    check = False
    for i in range(len(saved_range_list)-1):
        previous_this_max_value = saved_range_list[i][1]
        previous_next_min_value = saved_range_list[i+1][0]
        if previous_this_max_value > previous_next_min_value: # The equals should be valid
            check = True
            print("{} and {} are not one-to-one or one-to-many mapping".format(input_sst_label_file_path, input_scale_label_file_path))
            print("Error terms are sst-{} and sst-{}, {} and {}, respectively.".format(i, i+1, saved_range_list[i], saved_range_list[i+1]))

    if not check:
        print('mapping is a monotonic sequence!')

    print('Done.')
