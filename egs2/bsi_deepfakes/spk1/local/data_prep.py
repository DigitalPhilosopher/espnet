import argparse
import os
import sys


def main(args):
    src = args.src
    dst = args.dst

    spk2utt = {}
    utt2spk = []
    wav_list = []

    for r, ds, fs in os.walk(src):
        for f in fs:
            if os.path.splitext(f)[1] != ".wav":
                continue

            utt_dir = os.path.join(r, f)
            utt_id = os.path.splitext(f)[0]

            spk = utt_id.split('_')[0]
            if spk not in spk2utt:
                spk2utt[spk] = []
            spk2utt[spk].append(utt_id)
            utt2spk.append([utt_id, spk])
            wav_list.append([utt_id, utt_dir])

    with open(os.path.join(dst, "spk2utt"), "w") as f_spk2utt, open(
        os.path.join(dst, "utt2spk"), "w"
    ) as f_utt2spk, open(os.path.join(dst, "wav.scp"), "w") as f_wav:
        for spk in spk2utt:
            f_spk2utt.write(f"{spk}")
            for utt in spk2utt[spk]:
                f_spk2utt.write(f" {utt}")
            f_spk2utt.write("\n")

        for utt in utt2spk:
            f_utt2spk.write(f"{utt[0]} {utt[1]}\n")

        for utt in wav_list:
            f_wav.write(f"{utt[0]} {utt[1]}\n")

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Prep for dataset")
    parser.add_argument(
        "--src",
        type=str,
        required=True,
        help="source directory",
    )
    parser.add_argument(
        "--dst",
        type=str,
        required=True,
        help="destination directory",
    )
    args = parser.parse_args()

    sys.exit(main(args))
