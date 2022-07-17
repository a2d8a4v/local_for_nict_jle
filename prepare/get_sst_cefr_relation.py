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
from defined_scales import (
    mapping_dict
)

def argparse_function():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_sst_label_file_path",
                        default='data/trn/text_list',
                        type=str)

    parser.add_argument("--input_scale_label_file_path",
                        default='CEFR_LABELS_PATH/trn_sst_scores.txt',
                        type=str)

    parser.add_argument("--output_mapping_file_path",
                        default='CEFR_LABELS_PATH/trn_sst_scores.txt',
                        type=str)

    parser.add_argument("--assign_native_sst",
                        default=10,
                        type=int)

    args = parser.parse_args()

    return args

if __name__ == '__main__':

    # argparse
    args = argparse_function()

    # variable
    assign_native_sst = args.assign_native_sst
    input_sst_label_file_path = args.input_sst_label_file_path
    input_scale_label_file_path = args.input_scale_label_file_path
    output_mapping_file_path = args.output_mapping_file_path
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
    for _, saved_scales_idxs_list in saved_heap_tree.items():
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

    assert check == False, 'Mapping does not exist!'

    # save
    reversed_mapping_dict = { idx:scale for scale, idx in mapping_dict.items() }
    with io.open(output_mapping_file_path, 'w') as f:
        if 0 not in saved_heap_tree:
            f.write("{} {}\n".format(0, 0)) # do not forget 0
        for stt_score, saved_scales_idxs_list in saved_heap_tree.items():
            unique_scales_list = list(set(saved_scales_idxs_list))
            for scale_idx in unique_scales_list:
                f.write("{} {}\n".format(
                        stt_score,
                        reversed_mapping_dict[scale_idx]
                    )
                )
        # deal with the native speakers
        max_sst_score = max(list(saved_heap_tree.keys()))
        assert int(assign_native_sst) > int(max_sst_score), 'The assign_native_sst score should be bigger than other sst score in NICT JLE Corpus. Max sst score is {}'.format(max_sst_score)
        f.write("{} {}\n".format(assign_native_sst, 'C')) # assign for C scale
            


