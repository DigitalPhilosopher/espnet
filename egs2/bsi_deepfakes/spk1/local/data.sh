#!/usr/bin/env bash
set -e
set -u
set -o pipefail

stage=1
stop_stage=3

n_proc=8

data_dir_prefix=
#tts="/mnt/z/Datensätze/BSI/BSI-Dataset/Genuine_libritts"
tts="/mnt/z/Datensätze/Light"
deepfakes=""

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

if [ -z ${data_dir_prefix} ]; then
    log "Root dir for dataset not defined, setting to ${MAIN_ROOT}/egs2/bsi_deepfakes/data"
    data_dir_prefix=${MAIN_ROOT}/egs2/bsi_deepfakes/spk1/data
else
    log "Root dir set to ${BSI_DEEPFAKE}"
    data_dir_prefix=${BSI_DEEPFAKE}
fi

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    log "Stage 1: Add symlinks"

    # If genuine exists, skip
    if [ ! -d "${data_dir_prefix}/genuine" ]; then
        log "Adding symlinks for genuine data."
        python local/data_copy.py --src "${tts}" --dst "${data_dir_prefix}/genuine"
    else
       log "Skip adding symlinks for genuine."
    fi

    log "Stage 1, DONE."
fi

if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    log "Stage 2: Download Musan and RIR_NOISES for augmentation."

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

if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    log "Stage 3, Change into kaldi-style feature."
    mkdir -p ${trg_dir}/genuine
    python local/data_prep.py --src "${data_dir_prefix}/genuine" --dst "${trg_dir}/genuine"

    mkdir -p ${trg_dir}/bsi_train
    for f in wav.scp utt2spk spk2utt; do
        sort ${trg_dir}/genuine/${f} -o ${trg_dir}/bsi_train/${f}
    done

    # TODO
    mkdir -p ${trg_dir}/bsi_valid
    for f in wav.scp utt2spk spk2utt; do
        sort ${trg_dir}/genuine/${f} -o ${trg_dir}/bsi_valid/${f}
    done

    # make test trial compatible with ESPnet.
    python local/convert_trial.py --trial ${data_dir_prefix}/veri.txt --scp ${trg_dir}/genuine/wav.scp --out ${trg_dir}/genuine

    log "Stage 3, DONE."

fi

log "Successfully finished. [elapsed=${SECONDS}s]"
