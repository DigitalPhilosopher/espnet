import argparse
import os
import sys


def main(args):
    src = args.src
    dst = args.dst

    # Walk through the source directory
    for root, dirs, files in os.walk(src):
        # Determine the equivalent directory path in the destination
        rel_path = os.path.relpath(root, src)
        dst_dir = os.path.join(dst, rel_path)
        
        # Make sure the destination directory exists
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        
        # For each file, check if it's a .wav file
        for file in files:
            if os.path.splitext(file)[1] == ".wav":
                # Full path of the source file
                src_file = os.path.join(root, file)
                # Full path where the symlink will be created
                dst_file = os.path.join(dst_dir, file)
                
                # Create a symbolic link pointing to the source file
                os.symlink(src_file, dst_file)


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
    args = parser.parse_args()

    sys.exit(main(args))
