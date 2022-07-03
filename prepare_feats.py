import re
import argparse

from tqdm import tqdm
from espnet.utils.cli_utils import strtobool
from utils.utilities import (
    open_utt2value
)

# mapping_dict = {
#     0: 0,
#     'preA1': 1,
#     'A1': 2,
#     'A1+': 3,
#     'A2': 4,
#     'A2+': 5,
#     'B1': 6,
#     'B1+': 7,
#     'B2': 8,
# }

mapping_dict = {
    0: 0,
    'A1': 1,
    'A1+': 2,
    'A2': 3,
    'A2+': 4,
    'B1': 5,
    'B1+': 6,
    'B2': 7
}

def nullable_string(val):
    if val.lower() == 'none':
        return None
    return val

def argparse_function():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_text_list_file_path",
                        default='data/trn/text_list',
                        type=str)

    parser.add_argument("--input_score_label_file_path",
                        default='CEFR_LABELS_PATH/trn_sst_scores.txt',
                        type=str)

    parser.add_argument("--input_cefr_label_file_path",
                        default='CEFR_LABELS_PATH/trn_cefr_scores.txt',
                        type=str)

    parser.add_argument("--output_text_file_path",
                    default='CEFR_LABELS_PATH/trn_cefr_scores.txt',
                    type=str)

    parser.add_argument("--get_specific_labels",
                    default=None,
                    type=nullable_string)

    parser.add_argument("--skip_preA1",
                    default=True,
                    type=strtobool)

    args = parser.parse_args()

    return args

def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    selected_tags_list = re.findall('(<.*?>)', raw_html)

    return cleantext, selected_tags_list

def mapping_cefr2num(scale):
    return mapping_dict[scale]

## Data preparation
"""
The experiments in our work were performed on responses collected to Cambridge Assessment's [BULATs examination](https://www.cambridgeenglish.org/exams-and-tests/bulats), which is not publicly available. However, you can provide any TSV file (containing a header) of transcriptions containing the following columns:
- text (required): the transcription of the speech (spaces are assumed to signify tokenization)
- score (required): the numerical score assigned to the speech (by default, a scale between 0 - 6 is used to match CEFR proficiency levels)
- pos (optional): Penn Treebank part of speech tags. These should be space-separated and aligned with a token in text (i.e. there should be an identical number of tokens and POS tags)
- deprel (optional): Universal Dependency relation to head/parent token. These should be space-separated and aligned with a token in text (i.e. there should be an identical number of tokens and Universal Dependency relation labels)
- l1 (optional): native language/L1 of the speaker. Our experiments included L1 speakers of Arabic, Dutch, French, Polish, Thai and Vietnamese.
"""

if __name__ == '__main__':

    # argparse
    args = argparse_function()

    # as per recommendation from @freylis, compile once only
    CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

    # variables
    special_tags_tokens_list = ['<OL>']
    utt_text_dict = dict()
    get_specific_labels = args.get_specific_labels
    skip_preA1 = args.skip_preA1

    if get_specific_labels is not None:
        assert get_specific_labels in mapping_dict.keys(), "get_specific_labels was given out-of-domain label!"

    text_file_path_dict = open_utt2value(args.input_text_list_file_path)
    sst_file_path_dict = open_utt2value(args.input_score_label_file_path)
    cefr_file_path_dict = open_utt2value(args.input_cefr_label_file_path)

    for utt_id, utt_text_file_path in tqdm(text_file_path_dict.items()):

        # variable
        xml_list = []
        tags_list = []
        stages_dict = dict()
        stage_num_count = 1
        stage_num_now = 0
        utt_text_list = []

        with open(utt_text_file_path, 'r') as f:
            for line in f.readlines():
                line = line.strip().replace('\n','')
                if line == '':
                    continue
                xml_list.append(line)

        for xml_line in xml_list:
            
            # filter out the end tag toekns
            if xml_line[:2] == "</":
                continue
            
            if xml_line[1:-1] == "stage{}".format(stage_num_count):
                stages_dict.setdefault("stage{}".format(stage_num_count), [])
                stage_num_count += 1
                stage_num_now += 1
                
            if xml_line[:3] == '<B>':
                remove_head_tail_line = xml_line[3:-4]
                cleantext, selected_tags_list = cleanhtml(
                    remove_head_tail_line
                )
                stages_dict.setdefault("stage{}".format(stage_num_now), []).append(
                    cleantext
                )
                selected_tags_list = [ tag for tag in selected_tags_list if tag[:2] != '</' ]
                selected_tags_list_ori_len = len(selected_tags_list)
                
                collect_string_list = []
                tmp_substring = ''
                selected_tags_end_list = []
                # while remove_head_tail_line != '' and len(selected_tags_list) > 0 and len(selected_tags_end_list) != selected_tags_list_ori_len:
                #     tag_token = selected_tags_list.pop()
                #     end_token = "</{}>".format(tag_token[1:-1].split()[0])
                #     selected_tags_end_list.insert(0, end_token)
                #     start_tag_len = len(tag_token)
                #     end_tag_len = len(end_token)
                    
                #     # remove first token
                #     if remove_head_tail_line[:start_tag_len] == tag_token:
                #         remove_head_tail_line = remove_head_tail_line[start_tag_len:]
                #     else:
                #         selected_tags_list.insert(0, tag_token)
                #         selected_tags_end_list.pop()
                #     if remove_head_tail_line[:end_tag_len] == end_token:
                #         print("B")
                #         remove_head_tail_line = remove_head_tail_line[end_tag_len:]
                #         collect_string_list.append(tmp_substring)
                #         tmp_substring = ''
                #     tmp_substring += remove_head_tail_line[0]
                #     remove_head_tail_line = remove_head_tail_line[1:]
                #     if remove_head_tail_line[:end_tag_len] == end_token:
                #         print("C")
                #         remove_head_tail_line = remove_head_tail_line[:end_tag_len]
                #         collect_string_list.append(tmp_substring)
                #         tmp_substring = ''


                    
                # print(selected_tags_list)
                # print(collect_string_list)
                # input()
                tags_list.extend(selected_tags_list)

        tags_list = list(set(tags_list))

        for _, stage_info_list in stages_dict.items():
            utt_text_list.extend(stage_info_list)

    # BUG: fix empty token to avoid the problem of POS max tokens len
        token_list = [ token for token in " ".join(utt_text_list).split() if token != '']
        utt_text_dict.setdefault(utt_id, " ".join(token_list))

    if get_specific_labels is not None:
        count_cefr_labels = 0

    with open(args.output_text_file_path, 'w') as f:
        f.write("{}\t{}\t{}\n".format('score', 'sst', 'text'))
        for utt_id, text in utt_text_dict.items():

            if skip_preA1:
                if cefr_file_path_dict[utt_id].lower() == 'prea1':
                    continue

            if get_specific_labels is not None:
                if get_specific_labels.lower() == cefr_file_path_dict[utt_id].lower():
                    f.write("{}\t{}\t{}\n".format(
                            mapping_cefr2num(
                                cefr_file_path_dict[utt_id]
                            ),
                            sst_file_path_dict[utt_id],
                            text
                        )
                    )
                    count_cefr_labels+=1
            else:
                f.write("{}\t{}\t{}\n".format(
                        mapping_cefr2num(
                            cefr_file_path_dict[utt_id]
                        ),
                        sst_file_path_dict[utt_id],
                        text
                    )
                )

    if get_specific_labels is not None:
        print("{} has {} utterances.".format(
                get_specific_labels,
                count_cefr_labels
            )
        )
