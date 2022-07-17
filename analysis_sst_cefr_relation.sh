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

d="all"
if [ $stage -le 0 ] && [ $stop_stage -ge 0 ] ; then    
    echo "A. Check annotated files"

    for i in $d; do
        mkdir -pv data/${i} > /dev/null 2>&1

        cat $CEFR_LABELS_PATH/{trn_cefr_scores.txt,dev_cefr_scores.txt,eval_cefr_scores.txt} > data/${i}/${i}_cefr_scores.txt
        cat $CEFR_LABELS_PATH/{trn_sst_scores.txt,dev_sst_scores.txt,eval_sst_scores.txt} > data/${i}/${i}_stt_scores.txt
        python local.nict_jle/analysis/check_sst_cefr_relation.py \
            --input_sst_label_file_path data/${i}/${i}_stt_scores.txt \
            --input_scale_label_file_path data/${i}/${i}_cefr_scores.txt
    done
fi
