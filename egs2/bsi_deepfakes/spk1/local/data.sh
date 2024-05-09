#!/usr/bin/env bash
set -e
set -u
set -o pipefail

stage=1
stop_stage=4

n_proc=8

remove_corrupted=1
create_label_files=0

train_set=
test_sets=
valid_set=
cohort_set=

trg_dir=data

. utils/parse_options.sh
. db.sh
. path.sh
. cmd.sh
MAIN_ROOT=$(realpath $MAIN_ROOT)

log() {
    local fname=${BASH_SOURCE[1]##*/}
    echo -e "$(date '+%Y-%m-%dT%H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}

data_dir_prefix=${MAIN_ROOT}/egs2/bsi_deepfakes/spk1/data

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    log "Stage 1: Add symlinks"

    if [ $create_label_files -eq 1 ]; then
        log "Creating label files for bsi dataset. This is a long process and can take about 1.5 hours to generate."
        python ${BSI_DEEPFAKE}/extraction_utils/get_label_files.py
    else
        log "Skip creating label files for bsi dataset."
    fi

    if [ ! -d "${data_dir_prefix}/${train_set}" ]; then
        log "Adding symlinks for train data."
        python local/data_copy.py --src "${BSI_DEEPFAKE}" --dst "${data_dir_prefix}" --train ${train_set}
    else
       log "Skip adding symlinks for train data."
    fi

    if [ ! -d "${data_dir_prefix}/${test_sets}" ]; then
        log "Adding symlinks for test data."
        python local/data_copy.py --src "${BSI_DEEPFAKE}" --dst "${data_dir_prefix}" --test ${test_sets}
    else
       log "Skip adding symlinks for test data."
    fi

    if [ ! -d "${data_dir_prefix}/${valid_set}" ]; then
        log "Adding symlinks for valid data."
        python local/data_copy.py --src "${BSI_DEEPFAKE}" --dst "${data_dir_prefix}" --valid ${valid_set}
    else
       log "Skip adding symlinks for valid data."
    fi

    if [ ! -d "${data_dir_prefix}/${cohort_set}" ]; then
        log "Adding symlinks for cohort data."
        python local/data_copy.py --src "${BSI_DEEPFAKE}" --dst "${data_dir_prefix}" --cohort ${cohort_set}
    else
       log "Skip adding symlinks for cohort data."
    fi

    log "Stage 1, DONE."
fi

if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    log "Stage 2: Remove corrupted files"

    if [ $remove_corrupted -eq 1 ]; then
        python local/remove_corrupted.py --src "${data_dir_prefix}/${train_set}"
    fi

    log "Stage 2, DONE."
fi

if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    log "Stage 3: Download Musan and RIR_NOISES for augmentation."

    if [ ! -f ${data_dir_prefix}/rirs_noises.zip ]; then
        wget -P ${data_dir_prefix} -c http://www.openslr.org/resources/28/rirs_noises.zip
    else
        log "RIRS_NOISES exists. Skip download."
    fi

    if [ ! -f ${data_dir_prefix}/musan.tar.gz ]; then
        wget -P ${data_dir_prefix} -c http://www.openslr.org/resources/17/musan.tar.gz
    else
        log "Musan exists. Skip download."
    fi

    if [ -d ${data_dir_prefix}/RIRS_NOISES ]; then
        log "Skip extracting RIRS_NOISES"
    else
        log "Extracting RIR augmentation data."
        unzip -q ${data_dir_prefix}/rirs_noises.zip -d ${data_dir_prefix}
    fi

    if [ -d ${data_dir_prefix}/musan ]; then
        log "Skip extracting Musan"
    else
        log "Extracting Musan noise augmentation data."
        tar -zxvf ${data_dir_prefix}/musan.tar.gz -C ${data_dir_prefix}
    fi

    # make scp files
    for x in music noise speech; do
        find ${data_dir_prefix}/musan/${x} -iname "*.wav" > ${data_dir_prefix}/musan_${x}.scp
    done

    # Use small and medium rooms, leaving out largerooms.
    # Similar setup to Kaldi and VoxCeleb_trainer.
    find ${data_dir_prefix}/RIRS_NOISES/simulated_rirs/mediumroom -iname "*.wav" > ${data_dir_prefix}/rirs.scp
    find ${data_dir_prefix}/RIRS_NOISES/simulated_rirs/smallroom -iname "*.wav" >> ${data_dir_prefix}/rirs.scp
    log "Stage 3, DONE."
fi

if [ ${stage} -le 4 ] && [ ${stop_stage} -ge 4 ]; then
    log "Stage 4, Change into kaldi-style feature."
    python local/data_prep.py --src "${data_dir_prefix}/${train_set}" --dst "${data_dir_prefix}/${train_set}"
    python local/data_prep.py --src "${data_dir_prefix}/${test_sets}" --dst "${data_dir_prefix}/${test_sets}"
    python local/data_prep.py --src "${data_dir_prefix}/${valid_set}" --dst "${data_dir_prefix}/${valid_set}"
    python local/data_prep.py --src "${data_dir_prefix}/${cohort_set}" --dst "${data_dir_prefix}/${cohort_set}"

    log "Sorting."
    for f in wav.scp utt2spk spk2utt; do
        sort ${data_dir_prefix}/${train_set}/${f} -o ${data_dir_prefix}/${train_set}/${f}
        sort ${data_dir_prefix}/${test_sets}/${f} -o ${data_dir_prefix}/${test_sets}/${f}
        sort ${data_dir_prefix}/${cohort_set}/${f} -o ${data_dir_prefix}/${cohort_set}/${f}
        sort ${data_dir_prefix}/${valid_set}/${f} -o ${data_dir_prefix}/${valid_set}/${f}
    done

    log "Create veri txt."
    python local/create_veri.py --src ${data_dir_prefix}/${train_set} --dst ${data_dir_prefix}/${train_set}/veri.txt --picks 2 --random_picks 2
    python local/create_veri.py --src ${data_dir_prefix}/${test_sets} --dst ${data_dir_prefix}/${test_sets}/veri.txt --picks 2 --random_picks 2
    log "Make test trial compatible with ESPnet."
    python local/convert_trial.py --trial ${data_dir_prefix}/${test_sets}/veri.txt --scp ${data_dir_prefix}/${test_sets}/wav.scp --out ${data_dir_prefix}/${test_sets}

    log "Stage 4, DONE."

fi

log "Successfully finished. [elapsed=${SECONDS}s]"
