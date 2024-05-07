import argparse
import os
import sys
import importlib.util
import pandas as pd


def main(args):
    src = args.src
    dst = args.dst

    train_genuine, test_genuine, valid_genuine, _ = get_label_files(src + "/extraction_utils/get_label_files.py", use_bsi_genuine=True)
    
    if args.train is not None:
        copy_symlinks(dst + "/" + args.train, train_genuine)

    if args.test is not None:
        copy_symlinks(dst + "/" + args.test, test_genuine)
    
    if args.valid is not None:
        copy_symlinks(dst + "/" + args.valid, valid_genuine)
    
    if args.cohort is not None:
        copy_symlinks(dst + "/" + args.cohort, valid_genuine)

def copy_symlinks(dst_folder, files):
    df = create_data(files)
    create_directories(df, dst_folder)
    num_rows = df.shape[0]

    print(f"${dst_folder}: Number of rows in the DataFrame: ${num_rows}")
    for index, row in df.iterrows():
        if row['Filename'].endswith('.wav'):
            src_file = row['Text']
            dst_dir = os.path.join(dst_folder, row['SpeakerID'])
            filename = row['Filename'].split("_")
            filename[0] = filename[0].zfill(4)
            filename = "_".join(filename)
            dst_file = os.path.join(dst_dir, filename)

            if not os.path.exists(dst_file):
                os.symlink(src_file, dst_file)

def get_label_files(file_path,
                    use_bsi_tts: bool = False,
                    use_bsi_vocoder: bool = False,
                    use_bsi_vc: bool = False,
                    use_bsi_genuine: bool = False,
                    use_bsi_ttsvctk: bool = False,
                    use_bsi_ttslj: bool = False,
                    use_bsi_ttsother: bool = False,
                    use_bsi_vocoderlj: bool = False,
                    use_wavefake: bool = False,
                    use_LibriSeVoc: bool = False,
                    use_lj: bool = False,
                    use_asv2019: bool = False):
    # Save the current working directory
    original_cwd = os.getcwd()

    # Add the directory of the file to sys.path if not already there
    file_dir = '/'.join(file_path.split('/')[:-1])
    if file_dir not in sys.path:
        sys.path.append(file_dir)

    # Temporarily change the working directory
    os.chdir(file_dir)

    try:
        # Import the module using importlib
        module_name = file_path.split('/')[-1].replace('.py', '')
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Access and use the function
        labels_text_path_list_train, labels_text_path_list_dev, labels_text_path_list_test, all_datasets_used = module.get_label_files( 
            use_bsi_tts=use_bsi_tts, 
            use_bsi_vocoder=use_bsi_vocoder,
            use_bsi_vc=use_bsi_vc, 
            use_bsi_genuine=use_bsi_genuine, 
            use_bsi_ttsvctk=use_bsi_ttsvctk, 
            use_bsi_ttslj=use_bsi_ttslj, 
            use_bsi_ttsother=use_bsi_ttsother, 
            use_bsi_vocoderlj=use_bsi_vocoderlj, 
            use_wavefake=use_wavefake, 
            use_LibriSeVoc=use_LibriSeVoc, 
            use_lj=use_lj, 
            use_asv2019=use_asv2019)
    finally:
        # Restore the original working directory
        os.chdir(original_cwd)

    return labels_text_path_list_train, labels_text_path_list_dev, labels_text_path_list_test, all_datasets_used

def create_data(file_paths):
    df = get_utterances(file_paths)

    # Apply the function to the DataFrame to create new columns
    df['SpeakerID'] = df['Text'].apply(extract_speaker_id)
    df['Filename'] = df['Text'].apply(extract_filename)
    return df

def get_utterances(file_paths):
    # List to hold all the text entries
    data = []

    # Process each file
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as file:
                # Read each line in the file
                for line in file:
                    # Split the line at the first comma and take the first part
                    before_comma = line.split(',', 1)[0]
                    base_dir = os.path.dirname(file_path)
                    full_path = os.path.join(base_dir, before_comma.lstrip('/'))
                    data.append(full_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred while processing the file {file_path}: {str(e)}")

    # Convert the list to a DataFrame
    return pd.DataFrame(data, columns=['Text'])

def extract_filename(path):
    # Extract the last element as the filename
    filename = path.split('/')[-1]
    if not "_" in filename:
        filename = "9024_" + filename
    return filename

def extract_speaker_id(path):
    parts = path.split('/')
    # -2 index to get the second to last element, assuming the path always ends with a file
    speaker_id = parts[-2] if len(parts) > 1 else None
    if speaker_id == "wavs": # For private files
        speaker_id = "9024"
    else:
        speaker_id = speaker_id.split('_')[-1]
    return str(speaker_id).zfill(4)

def create_directories(df, dst_folder):
    for speaker_id in df['SpeakerID'].unique():
        speaker_id_padded = str(speaker_id).zfill(4)
        
        # Create the directory using the padded speaker ID
        speaker_dir = os.path.join(dst_folder, speaker_id_padded)
        if not os.path.exists(speaker_dir):
            os.makedirs(speaker_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BSI copy tool")
    parser.add_argument(
        "--src",
        type=str,
        required=True,
        help="source directory of bsi data",
    )
    parser.add_argument(
        "--dst",
        type=str,
        required=True,
        help="destination directory of data",
    )
    parser.add_argument(
        "--train",
        type=str,
        required=False,
        help="destination directory of train data",
    )
    parser.add_argument(
        "--test",
        type=str,
        required=False,
        help="destination directory of test data",
    )
    parser.add_argument(
        "--valid",
        type=str,
        required=False,
        help="destination directory of valid data",
    )
    parser.add_argument(
        "--cohort",
        type=str,
        required=False,
        help="destination directory of cohort data",
    )
    parser.add_argument(
        "--create_label_files",
        action="store_true",
        required=False,
        help="if label files should be created",
    )
    args = parser.parse_args()

    sys.exit(main(args))
