import os
import random
import argparse
import sys

def list_wav_files(directory):
    """List all .wav files in subdirectories of the given directory."""
    wav_files = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.wav'):
                path = root.split(os.sep)[-1]
                if path not in wav_files:
                    wav_files[path] = []
                wav_files[path].append(file.rstrip('.wav'))
    return wav_files

def generate_combinations(wav_files, num_random_picks):
    """Generate combinations of wav files."""
    output_lines = []
    paths = list(wav_files.keys())
    
    for path in paths:
        files = wav_files[path]
        # Combinations within the same directory
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                output_lines.append(f"1 {files[i]} {files[j]}")
        
        # Random combinations from other directories
        other_files = []
        other_paths = [p for p in paths if p != path]  # Ensure no repeat of current path
        for other_path in other_paths:
            other_files.extend([f"{file}" for file in wav_files[other_path]])
        
        for file in files:
            if other_files:
                chosen_files = random.sample(other_files, min(num_random_picks, len(other_files)))
                for other_file in chosen_files:
                    output_lines.append(f"0 {file} {other_file}")

    return output_lines


def write_output_file(output_lines, output_filename):
    """Write the output lines to a file."""
    with open(output_filename, 'w') as file:
        for line in output_lines:
            file.write(line + '\n')

def main(args):
    # List all wav files in the subdirectories
    wav_files = list_wav_files(args.src)
    
    # Generate combinations
    output_lines = generate_combinations(wav_files, args.random_picks)
    
    # Write to file
    write_output_file(output_lines, args.dst)
    print(f"Output written to {args.dst}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BSI copy tool")
    parser.add_argument(
        "--src",
        type=str,
        required=True,
        help="Source directory of bsi data",
    )
    parser.add_argument(
        "--dst",
        type=str,
        required=True,
        help="Destination file where data is written",
    )
    parser.add_argument(
        "--random_picks",
        type=int,
        default=10,
        help="Number of random picks from other directories",
    )
    args = parser.parse_args()
    sys.exit(main(args))
