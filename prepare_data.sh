#!/bin/bash

# Copyright (c) 2022 National Taiwan Normal University
# License: Apache 2.0

. cmd.sh
. path.sh

if [ $# -ne 2 ]; then
    echo "Usage: $0 CORPUS_DIR_PATH CEFR_LABELS_PATH"
    echo "  e.g.    NICT_JLE_4.1 NICT_JLE_proficiency_and_CEFR"
    exit 100
fi

CORPUS_DIR_PATH=$1
CEFR_LABELS_PATH=$2

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

. ./utils/parse_options.sh

# prepare training data
echo "A. Prepare training data"
d="trn dev eval"
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
    cat $CEFR_LABELS_PATH/${i}_sst_scores.txt | cut -f1 -d$'\t' > data/$i/utt_id.list
    awk 'NR==FNR{tgts[$1]; next} $1 in tgts' data/$i/utt_id.list data/$i/text.LearnerErrortagged > data/$i/text_list
    rm data/$i/utt_id.list data/$i/text.LearnerErrortagged
    python local.nict_jle/prepare_feats.py \
        --input_text_list_file_path data/$i/text_list \
        --input_score_label_file_path $CEFR_LABELS_PATH/${i}_sst_scores.txt \
        --input_cefr_label_file_path $CEFR_LABELS_PATH/${i}_cefr_scores.txt \
        --output_text_file_path data/$i/text
done
