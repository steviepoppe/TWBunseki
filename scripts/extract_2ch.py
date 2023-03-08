import argparse
import os
import glob
import uuid
from csv import QUOTE_NONNUMERIC
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup


def extract_df(file):
    with open(file, encoding='shift_jisx0213') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'html.parser')
    posts = soup.find_all(class_='post')
    data = []
    for post in posts:
        post_data = {}
        meta = post.find(class_='meta')
        post_data['post_id'] = meta.find(class_='number').get_text()
        if int(post_data['post_id']) <= 1000:
            date = meta.find(class_='date').get_text().split('(')
            post_data['date'] = date[0] + ' ' + date[1].split(') ')[1]
            post_data['user'] = meta.find(class_='name').get_text()
            post_data['user_id'] = meta.find(class_='uid').get_text()
            post_data['contents'] = post.find(class_='message').find(class_='escaped').get_text()
            data.append(post_data)
    
    return pd.DataFrame(data)



def merge(pattern):
    files = glob.glob(pattern)
    if not files:
        raise Exception(f'No files found for the given pattern: {pattern}')

    dfs = []
    meta = []
    for file in files:
        print(f'Merging file: {file}')
        df = extract_df(file)
        df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d %H:%M:%S.%f')
        df['date'] = df['date'].dt.tz_localize('Asia/Tokyo')
        thread_id = str(int(datetime.timestamp(df[df.post_id == '1'].iloc[0].date)))
        meta.append({'filepath': file, 'thread_id': thread_id})
        df = df.assign(thread_id=thread_id)  # so every thread has its own ID
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True), pd.DataFrame(meta)


def analyze(args):
    if not args['save_folder'].endswith('/'):
        args['save_folder'] += '/'

    try:
        os.makedirs(args['save_folder'])
    except FileExistsError:
        # directory already exists
        pass

    df, meta_df = merge(args['filepath_pattern'])
    df = df.sort_values(['thread_id', 'date'])
    save_file_name = args['save_folder'] + 'merged_data' 
    print(f'Saving to {save_file_name}...')
    df.to_csv(save_file_name + '.csv', mode='w+', encoding='utf-8', index=False, quoting=QUOTE_NONNUMERIC)
    meta_df.to_csv(save_file_name + '_meta.csv', mode='w+', encoding='utf-8', index=False, quoting=QUOTE_NONNUMERIC)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Categorize a csv file using keywords')
    parser.add_argument(
        '-fp',
        '--filepath-pattern',
        type=str,
        required=True,
        help='Pattern for the csv files. Can use wildcards. Example: "C://Downloads/2channel_mythread_*.html"',
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
