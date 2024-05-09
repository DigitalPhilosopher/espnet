import argparse
import os
import sys
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor, as_completed


def main(args):
    corrupted_files = check_audio_files(args.src)
    print(f"Found {len(corrupted_files)} corrupted files. Removing...")
    remove_symlinks(corrupted_files)

# Function to check if an audio file is corrupted
def is_file_corrupted(file_list):
    """Check a list of audio files for corruption."""
    corrupted_files = []
    for filepath in file_list:
        try:
            with sf.SoundFile(filepath) as sf_file:
                # Check if file has a valid sample rate
                if not sf_file.samplerate or sf_file.samplerate <= 0:
                    raise ValueError("Invalid sample rate")
                # Read the entire file to check for errors
                sf_file.read()
        except Exception as e:
            corrupted_files.append(filepath)
    return corrupted_files

# Function to split the file list into chunks
def chunkify(lst, n):
    """Divide a list into n approximately equal chunks."""
    return [lst[i::n] for i in range(n)]

# Parallel check function
def check_audio_files(directory, num_workers=8):
    """Check for corrupted audio files in a given directory using parallel processing."""
    audio_files = []

    # Collect all audio files into a list
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".wav"):
                audio_files.append(os.path.join(root, file))

    # Split the audio file list into chunks
    file_chunks = chunkify(audio_files, num_workers)

    corrupted_files = []

    # Use ThreadPoolExecutor to handle file chunks concurrently
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = executor.map(is_file_corrupted, file_chunks)

    # Combine all corrupted files found
    for result in results:
        corrupted_files.extend(result)

    return corrupted_files


def remove_symlinks(file_list):
    """Remove symbolic links given a list of paths."""
    for filepath in file_list:
        try:
            # Verify if the path is a symlink before attempting to remove it
            if os.path.islink(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Error removing {filepath}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remover for corrupted wav files")
    parser.add_argument(
        "--src",
        type=str,
        required=True,
        help="directory of wav files",
    )
    args = parser.parse_args()

    sys.exit(main(args))
