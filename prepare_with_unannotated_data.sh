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
assign_native_sst=10
remove_punctuation=true
convert_meaningless2unk_tokens=true
skip_preA1=false

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
    echo "A. Prepare mapping"
    # if get error here, do not do the other blocks below

    for i in $d; do
        mkdir -pv data/${i} > /dev/null 2>&1

        cat ${CEFR_LABELS_PATH}/{trn_cefr_scores.txt,dev_cefr_scores.txt,eval_cefr_scores.txt} > data/${i}/${i}_cefr_scores.txt
        cat ${CEFR_LABELS_PATH}/{trn_sst_scores.txt,dev_sst_scores.txt,eval_sst_scores.txt} > data/${i}/${i}_stt_scores.txt
        python local.nict_jle/prepare/get_sst_cefr_relation.py \
            --input_sst_label_file_path data/${i}/${i}_stt_scores.txt \
            --input_scale_label_file_path data/${i}/${i}_cefr_scores.txt \
            --output_mapping_file_path data/${i}/stt2scale \
            --assign_native_sst $assign_native_sst
    done
fi

d="all"
s="LearnerOriginal Native"
if [ $stage -le 1 ] && [ $stop_stage -ge 1 ] ; then    
    echo "B. generate cefr scale labels and sst score labels for the unannotated files"
    for i in $d; do
        mkdir -pv data/${i} > /dev/null 2>&1
    done

    for i in $d; do
        for src in $s; do
            find ${CORPUS_DIR_PATH}/${src} -name "*.txt" -type f -exec basename {} .txt \; > data/$i/utt_id.list.${src}
            find ${CORPUS_DIR_PATH}/${src} -name "*.txt" -type f > data/$i/utt_id.path.${src}
            paste -d ' ' data/$i/utt_id.list.${src} data/$i/utt_id.path.${src} > data/$i/text.${src}
            rm data/$i/utt_id.list.${src} data/$i/utt_id.path.${src}
        done
    done

    for i in $d; do
        for src in $s; do
            # we need to generate sst scores first
            python local.nict_jle/prepare/prepare_scores.py \
                --assign_native_sst $assign_native_sst \
                --input_mapping_file_path data/${i}/stt2scale \
                --input_text_list_file_path data/$i/text.${src} \
                --output_scores_file_path data/$i/${i}_sst_scores.${src}.txt

            # second, we can get cefr scales from sst scores with mapping
            python local.nict_jle/prepare/prepare_scales.py \
                --input_mapping_file_path data/${i}/stt2scale \
                --input_scores_file_path data/$i/${i}_sst_scores.${src}.txt \
                --output_scales_file_path data/$i/${i}_cefr_scales.${src}.txt

            rm data/$i/text.${src}
        done
    done

    scores_file_path=""
    scales_file_path=""
    for i in $d; do
        for src in $s; do
            scores_file_path+="data/$i/${i}_sst_scores.${src}.txt "
            scales_file_path+="data/$i/${i}_cefr_scales.${src}.txt "
        done
    done
    for i in $d; do
        cat $scores_file_path > data/$i/${i}_sst_scores.txt
        cat $scales_file_path > data/$i/${i}_cefr_scales.txt
    done

    for i in $d; do
        rm data/$i/${i}_sst_scores.*.txt data/$i/${i}_cefr_scales.*.txt
    done
fi

d="all"
s="LearnerOriginal Native"
if [ $stage -le 2 ] && [ $stop_stage -ge 2 ] ; then    
    # prepare training data
    echo "C. generate new train combo files"
    for i in $d; do
        mkdir -pv data/${i} > /dev/null 2>&1
    done

    for i in $d; do
        for src in $s; do
            find ${CORPUS_DIR_PATH}/${src} -name "*.txt" -type f -exec basename {} .txt \; > data/$i/utt_id.list.${src}
            find ${CORPUS_DIR_PATH}/${src} -name "*.txt" -type f > data/$i/utt_id.path.${src}
            # get text file path list
            paste -d ' ' data/$i/utt_id.list.${src} data/$i/utt_id.path.${src} > data/$i/text.${src}
            # get momlanguage
            touch data/$i/momlanguage.${src}.list
            lines=$(cat data/$i/utt_id.list.${src}| wc -l)
            for j in $(seq 1 $lines); do
                if [ $src == 'LearnerOriginal' ]; then
                    echo 'japanese' >> data/$i/momlanguage.${src}.list
                elif [ $src == 'Native' ]; then
                    echo 'american' >> data/$i/momlanguage.${src}.list
                fi
            done
            paste -d ' ' data/$i/utt_id.list.${src} data/$i/momlanguage.${src}.list > data/$i/momlanguage.${src}
            # delete temporary files
            rm data/$i/utt_id.list.${src} data/$i/utt_id.path.${src} data/$i/momlanguage.${src}.list
        done
    done

    momlanguage_files=""
    text_files=""
    for i in $d; do
        for src in $s; do
            momlanguage_files+="data/$i/momlanguage.${src} "
            text_files+="data/$i/text.${src} "
        done
    done

    for i in $d; do
        cat $momlanguage_files > data/$i/momlanguage
        cat $text_files > data/$i/text_list
    done

    for i in $d; do
        python local.nict_jle/prepare/prepare_feats.py \
            --input_text_list_file_path data/$i/text_list \
            --input_score_label_file_path data/$i/${i}_sst_scores.txt \
            --input_cefr_label_file_path data/$i/${i}_cefr_scales.txt \
            --input_spk2momlang_file_path data/$i/momlanguage \
            --output_text_file_path data/$i/text.tsv \
            --remove_punctuation $remove_punctuation \
            --convert_meaningless2unk_tokens $convert_meaningless2unk_tokens \
            --skip_preA1 $skip_preA1
    done
    rm data/$i/text_list $text_files data/$i/momlanguage.*
fi