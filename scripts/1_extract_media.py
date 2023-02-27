"""
STEP 1 in media analysis pipeline: extract media from Twitter corpus
"""
import argparse
import csv
import re
from urllib.parse import urlparse

import pandas as pd
from urlextract import URLExtract
from tqdm import tqdm


def extract_urls(text):
	pattern = re.compile(r'((http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]))', re.DOTALL)
	tco_pattern = re.compile(r'.*(https?://t.co/[a-zA-Z0-9]+).*')
	urls = [x[0] for x in re.findall(pattern, text)]
	final_urls = []
	for url in urls:
		if url.startswith('https://t.co') or url.startswith('http://t.co'):
			url = tco_pattern.match(url)[1]
		final_urls.append(url)
	return final_urls


def get_data_per_tweet(corpus_df):
	data = []
	total_rows = len(corpus_df)
	for row in tqdm(corpus_df.itertuples(), total=total_rows):
		urls = extract_urls(row.text)
		for url in urls:
			data.append({
				'tweet_id': row.tweet_id,
				'created_at': row.created_at,
				'user_screen_name': row.user_screen_name,
				'tweet_retweet_count': row.tweet_retweet_count,
				'url': url,
			})
	return pd.DataFrame(data)


def prep_for_reanalyze(tweet_data_df):
	df = tweet_data_df[['url', 'user_screen_name', 'tweet_retweet_count']]
	df = df.assign(total_tweets_in_set=1)
	df = df.groupby(['url', 'user_screen_name']).sum().reset_index()
	return df.assign(expanded_url='', domain='', error_expanding=True)


def process_data_df(args):
	file_name = args['corpus_filename']
	sep = args['csv_sep']

	print(f'Reading corpus from {file_name}...')
	corpus_df = pd.read_csv(file_name, encoding='utf-8', sep=sep)

	print(f'Getting links from tweets...')
	tweet_data_df = get_data_per_tweet(corpus_df)

	save_file_name = file_name.removesuffix('.csv') + '_tweet_links' + '.csv'
	print(f'Saving links from tweets to {save_file_name}...')
	tweet_data_df.reset_index(drop=True, inplace=True)
	tweet_data_df.to_csv(save_file_name, mode='w+',index=True, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)

	reanalyze_save_file_name = file_name.removesuffix('.csv') + '_dictionary' + '.csv'
	print(f'Saving url dictionary data (for reanalyze) {reanalyze_save_file_name}...')
	reanalyze_df = prep_for_reanalyze(tweet_data_df)
	reanalyze_df.to_csv(reanalyze_save_file_name, mode='w+',index=False, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)

	print('Done!')



if __name__ == '__main__':
	pd.options.mode.chained_assignment = None
	p = argparse.ArgumentParser(description='Get and aggregate data for Media URL metrics (more granular than get_metrics.py)')
	p.add_argument(
		'-cf',
		'--corpus-filename',
		type=str,
		required=True,
		help='Full or relative path to the corpus csv file. E.g. results/my_data.csv',
	)
	p.add_argument(
		'--csv-sep',
		type=str,
		default=',',
		choices=[',', ';', '\\t', '|'],
		help='Separator for your csv files. Default: ","',
	)
	args = vars(p.parse_args())
	process_data_df(args)
