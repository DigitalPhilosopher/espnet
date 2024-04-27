#!/usr/bin/env bash
set -e
set -u
set -o pipefail


spk_config=conf/train_ECAPA_mel.yaml

train_set="bsi_train"
valid_set="bsi_test"
cohort_set="bsi_test"
test_sets="bsi_test"
feats_type="raw"

./spk.sh \
    --feats_type ${feats_type} \
    --spk_config ${spk_config} \
    --train_set ${train_set} \
    --valid_set ${valid_set} \
    --cohort_set ${cohort_set} \
    --test_sets ${test_sets} \
    "$@"
