import argparse
import os
import glob
import uuid
from csv import QUOTE_NONNUMERIC

import pandas as pd


def merge(pattern):
    files = glob.glob(pattern)
    if not files:
        raise Exception(f'No files found for the given pattern: {pattern}')

    dfs = []
    for file in files:
        df = pd.read_csv(file)
        df = df.assign(thread_id=str(uuid.uuid4()))  # so every thread has its own ID
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def analyze(args):
    if not args['save_folder'].endswith('/'):
        args['save_folder'] += '/'

    try:
        os.makedirs(args['save_folder'])
    except FileExistsError:
        # directory already exists
        pass

    df = merge(args['filepath_pattern'])
    df.to_csv(args['save_folder'] + 'merged_data.csv', mode='w+', encoding='utf-8', index=False, quoting=QUOTE_NONNUMERIC)

    stats = df.groupby('thread_id')['UserID'].nunique().reset_index()
    stats.to_csv(args['save_folder'] + 'unique_users.csv', mode='w+', encoding='utf-8', index=False, quoting=QUOTE_NONNUMERIC)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Categorize a csv file using keywords')
    parser.add_argument(
        '-fp',
        '--filepath-pattern',
        type=str,
        required=True,
        help='Pattern for the csv files. Can use wildcards. Example: "C://Downloads/2channel_mythread_*.csv"',
    )
    parser.add_argument(
        '-s',
        '--save-folder',
        type=str,
        required=True,
        help='Folder prefix to store results in. Can be something like "results/mythread/"',
    )
    args = vars(parser.parse_args())

    print('Analyzing...')
    analyze(args)
    print('Done!')
