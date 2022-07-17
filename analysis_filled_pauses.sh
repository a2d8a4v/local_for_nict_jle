#!/bin/bash

# Copyright (c) 2022 National Taiwan Normal University
# License: Apache 2.0

. ./path.sh || exit 1;
. ./cmd.sh || exit 1;

stage=0
stop_stage=10000
# dict_file_path=/share/nas167/a2y3a1N0n2Yann/speechocean/espnet_amazon/egs/tlt-school/is2021_data-prep-all_baseline/data/lang/words.txt
# dict_file_path=/share/nas167/a2y3a1N0n2Yann/speechocean/espnet_amazon/egs/tlt-school/is2021_data-prep-all_baseline/Librispeech-model-mct-tdnnf/data/lang_t3/words.txt
dict_file_path=/share/nas167/a2y3a1N0n2Yann/speechocean/espnet_amazon/egs/tlt-school/is2021_data-prep-all_baseline/TLT-school-s6-tdnn1j/data/lang_test4gr/words.txt

. ./utils/parse_options.sh
set -euo pipefail

d="all"
s="LearnerOriginal Native"
if [ $stage -le 0 ] && [ $stop_stage -ge 0 ] ; then    
    # prepare training data
    for i in $d; do
        if [ ! -f data/$i/text.tsv ]; then
            echo "You need to do prepare the data before running this script."
            exit 10
        fi
    done

    for i in $d; do
        tail -n +2 data/$i/text.tsv | awk '{print $5}' > data/$i/text.tmp
        python local.nict_jle/prepare/get_oov.py \
            --input_text_file_path data/$i/text.tmp \
            --words_file_path $dict_file_path
        rm data/$i/text.tmp
    done
fi