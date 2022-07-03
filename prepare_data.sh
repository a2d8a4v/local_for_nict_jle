#!/bin/bash

# Copyright (c) 2022 National Taiwan Normal University
# License: Apache 2.0

. ./path.sh || exit 1;
. ./cmd.sh || exit 1;

stage=0
stop_stage=10000
specific_scale=None
specific_sst=
CORPUS_DIR_PATH=NICT_JLE_4.1
CEFR_LABELS_PATH=nict_jle_cambridge_labels

. ./utils/parse_options.sh
set -euo pipefail


if [ ! -d $CORPUS_DIR_PATH ]; then
    echo "ERROR: source data directory not found: $CORPUS_DIR_PATH"
    exit 100
fi

missingdir=0
for src in LearnerErrortagged LearnerOriginal Native; do
    if [ ! -d ${CORPUS_DIR_PATH}/${src} ]; then
         echo "ERROR: individual source data directory not found: ${CORPUS_DIR_PATH}/${src}"
         missingdir=1
    fi
done
if [ $missingdir == 1 ]; then
    exit 100
fi

d="trn dev eval"
if [ $stage -le 0 ] && [ $stop_stage -ge 0 ] ; then    
    # prepare training data
    echo "A. Prepare training, dev and eval data"
    for i in $d; do
        mkdir -pv data/${i} > /dev/null 2>&1
    done

    for i in $d; do
        for src in LearnerErrortagged; do
            find ${CORPUS_DIR_PATH}/${src} -name "*.txt" -type f -exec basename {} .txt \; > data/$i/utt_id.list.${src}
            find ${CORPUS_DIR_PATH}/${src} -name "*.txt" -type f > data/$i/utt_id.path.${src}
            paste -d ' ' data/$i/utt_id.list.${src} data/$i/utt_id.path.${src} > data/$i/text.${src}
            rm data/$i/utt_id.list.${src} data/$i/utt_id.path.${src}
        done
    done

    for i in $d; do
        for src in LearnerErrortagged; do
            cat $CEFR_LABELS_PATH/${i}_sst_scores.txt | cut -f1 -d$'\t' > data/$i/utt_id.list
            awk 'NR==FNR{tgts[$1]; next} $1 in tgts' data/$i/utt_id.list data/$i/text.${src} > data/$i/text_list
            python local.nict_jle/prepare_feats.py \
                --input_text_list_file_path data/$i/text_list \
                --input_score_label_file_path $CEFR_LABELS_PATH/${i}_sst_scores.txt \
                --input_cefr_label_file_path $CEFR_LABELS_PATH/${i}_cefr_scores.txt \
                --output_text_file_path data/$i/text
            rm data/$i/utt_id.list data/$i/text.${src} data/$i/text_list
        done
    done
fi

a="all"
if [ $stage -le 1 ] && [ $stop_stage -ge 1 ] ; then    
    echo "B. Prepare all data"
    for i in $a; do
        mkdir -pv data/${i} > /dev/null 2>&1
        for src in LearnerErrortagged; do
            find ${CORPUS_DIR_PATH}/${src} -name "*.txt" -type f -exec basename {} .txt \; > data/$i/utt_id.list.${src}
            find ${CORPUS_DIR_PATH}/${src} -name "*.txt" -type f > data/$i/utt_id.path.${src}
            paste -d ' ' data/$i/utt_id.list.${src} data/$i/utt_id.path.${src} > data/$i/text.${src}
            rm data/$i/utt_id.list.${src} data/$i/utt_id.path.${src}
        done
    done

    cefr_scores_names=""
    for i in $d; do
        cefr_scores_names+="${i}_cefr_scores.txt "
    done
    cefr_scores_names=$(echo ${cefr_scores_names[*]} | tr ' ' ,)
    for i in $a; do
        for src in LearnerErrortagged; do
            # cat $CEFR_LABELS_PATH/"{$cefr_scores_names}" > data/$i/cefr_scores_names.txt.tmp
            # cat data/$i/cefr_scores_names.txt.tmp | cut -f1 -d$'\t' > data/$i/utt_id.list
            # awk 'NR==FNR{tgts[$1]; next} $1 in tgts' data/$i/utt_id.list data/$i/text.${src} > data/$i/text_list
            # rm data/$i/cefr_scores_names.txt.tmp data/$i/utt_id.list data/$i/text.${src}
            cat data/$i/text.${src} > data/$i/text_list
            cat $CEFR_LABELS_PATH/{trn_cefr_scores.txt,dev_cefr_scores.txt,eval_cefr_scores.txt} > data/$i/cefr_scores.txt
            cat $CEFR_LABELS_PATH/{trn_sst_scores.txt,dev_sst_scores.txt,eval_sst_scores.txt} > data/$i/stt_scores.txt
            python local.nict_jle/prepare_feats.py \
                --input_text_list_file_path data/$i/text_list \
                --input_score_label_file_path data/$i/stt_scores.txt \
                --input_cefr_label_file_path data/$i/cefr_scores.txt \
                --output_text_file_path data/$i/text \
                --get_specific_labels $specific_scale
            rm data/$i/cefr_scores.txt data/$i/stt_scores.txt data/$i/text_list
        done
    done
fi