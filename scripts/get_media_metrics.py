import argparse
import csv
import re
from urllib.parse import urlparse, parse_qs

import pandas as pd
import tldextract


def extract_url(text):
	pattern = re.compile(r'.*(https://t.co/[a-zA-Z0-9]+).*')
	result = pattern.match(text)
	return result[1] if result else None


def get_data_per_tweet(corpus_df):
	data_df = corpus_df[['text', 'created_at', 'user_screen_name', 'tweet_retweet_count']]
	data_df['url'] = data_df['text'].apply(extract_url)
	return data_df[data_df['url'].notnull()].drop(columns=['text'])


def process_data_df(file_name, sep):
	print(f'Reading corpus from {file_name}...')
	corpus_df = pd.read_csv(file_name, encoding='utf-8', sep=sep)

	print(f'Getting data on the tweet level...')
	tweet_data_df = get_data_per_tweet(corpus_df)

	save_file_name = file_name.removesuffix('.csv') + '_data_per_tweet' + '.csv'
	print(f'Saving data on the tweet level to {save_file_name}...')
	tweet_data_df.reset_index(drop=True, inplace=True)
	tweet_data_df.to_csv(save_file_name, mode='w+',index=True, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)

	return tweet_data_df


def get_domain(url):
	extracted = tldextract.extract(url)
	return f'{extracted.domain}.{extracted.suffix}'


def get_subdomain(url):
	subdomain = tldextract.extract(url).subdomain
	return subdomain if subdomain != 'www' else ''


def clean_youtube(row):
	query = parse_qs(urlparse(row['expanded_url']).query)
	if 'youtube' in row['root_domain'] and 'v' in query:
		v_id = query['v'][0]
		return f'https://youtube.com/watch?v={v_id}'
	return row['expanded_url']


def process_expanded_df(file_name, sep):
	print(f'Reading expanded URL data from {file_name}...')
	expanded_df = pd.read_csv(file_name, encoding='utf-8', sep=sep)

	expanded_df['root_domain'] = expanded_df['expanded_url'].apply(get_domain)
	expanded_df['sub_domain'] = expanded_df['expanded_url'].apply(get_subdomain)
	expanded_df['expanded_url'] = expanded_df.apply(clean_youtube, axis=1)
	
	save_file_name = file_name.removesuffix('.csv') + '_processed' + '.csv'
	print(f'Saving processed expanded URL data to {save_file_name}...')
	expanded_df.to_csv(save_file_name, mode='w+',index=False, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)


def get_media_metrics(args):
	corpus_file_name = args['corpus_filename']
	expanded_url_file_name = args['expanded_url_filename']
	sep = args['csv_sep']

	if corpus_file_name: # REMOVE AFTER AGG
		tweet_data_df = process_data_df(corpus_file_name, sep)

	if expanded_url_file_name: # REMOVE AFTER AGG
		expanded_url_df = process_expanded_df(expanded_url_file_name, sep)
	print('Done!')



if __name__ == '__main__':
	pd.options.mode.chained_assignment = None
	p = argparse.ArgumentParser(description='Get and aggregate data for Media URL metrics (more granular than get_metrics.py)')
	p.add_argument(
		'-cf',
		'--corpus-filename',
		type=str,
		# required=True,
		help='Full or relative path to the corpus csv file. E.g. results/my_data.csv',
	)
	p.add_argument(
		'-euf',
		'--expanded_url-filename',
		type=str,
		# required=True,
		help='Full or relative path to the expanded URL csv file. E.g. results/my_data.csv',
	)
	p.add_argument(
		'--csv-sep',
		type=str,
		default=',',
		choices=[',', ';', '\\t', '|'],
		help='Separator for your csv files (has to be the same across all files). Default: ","',
	)
	args = vars(p.parse_args())
	get_media_metrics(args)

# AGG:
# auto-generate archive URLs with dates
# agg by month/year
# agg by unique users (+ date?)