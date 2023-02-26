"""
STEP FOUR IN MEDIA PIPELINE
"""
import argparse
import csv

import pandas as pd


def add_archive_links(merged_df):
	print('Adding archive.org links...')
	print('> sorting by date (descending)')
	# sort by date
	sorted_df = merged_df.sort_values('created_at', ascending=False)

	print('> dropping duplicates')
	# drop duplicates
	unique_df = sorted_df.drop_duplicates(subset='url', keep='last', ignore_index=True)

	print('> excluding twitter.com links')
	# exclude twitter.com links
	unique_df = unique_df[~unique_df['root_domain'].isin(['twitter.com'])]

	print('> generating column')
	# generate column
	unique_df['archive_url'] = unique_df.apply(
		lambda x: 'https://web.archive.org/web/' + str(x['created_at'].year) + '%02d' % x['created_at'].month + '%02d' % x['created_at'].day + '/' + str(x['clean_expanded_url']),
		axis=1,
	)
	return unique_df


def save_df(df, file_name, suffix, index=False):
	save_file_name = file_name.removesuffix('.csv') + suffix + '.csv'
	print(f'Saving data to {save_file_name}...')
	df.to_csv(save_file_name, mode='w+', index=index, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)


def expand_media_metrics(args):
	data_per_tweet_file_name = args['data_per_tweet_filename']
	processed_expanded_file_name = args['processed_expanded_url_filename']
	output_filename = args['output_filename']
	sep = args['csv_sep']

	print(f'Reading data per tweet csv from {data_per_tweet_file_name}...')
	tweet_data_df = pd.read_csv(data_per_tweet_file_name, encoding='utf-8', sep=sep)
	tweet_data_df.created_at = pd.to_datetime(tweet_data_df.created_at)

	print(f'Reading processed expanded URL data from {processed_expanded_file_name}...')
	expanded_df = pd.read_csv(processed_expanded_file_name, encoding='utf-8', sep=sep)

	merged_df = tweet_data_df.merge(expanded_df, how='left', on='url')
	if 'total_tweets_in_set' in merged_df:
		merged_df = merged_df.drop(columns=['total_tweets_in_set'])

	archived_df = add_archive_links(merged_df)
	save_df(archived_df, output_filename, '_with_archived_links')

	# groups
	merged_df = merged_df.assign(tweet_count_for_dimensions_in_set=1)
	# logic here!
	print('Done!')



if __name__ == '__main__':
	pd.options.mode.chained_assignment = None
	p = argparse.ArgumentParser(description='Get and aggregate data for Media URL metrics (more granular than get_metrics.py)')
	p.add_argument(
		'-dptf',
		'--data-per-tweet-filename',
		type=str,
		required=True,
		help='Full or relative path to the data per tweet csv file from extract_media.py. E.g. results/my_data.csv',
	)
	p.add_argument(
		'-peuf',
		'--processed-expanded-url-filename',
		type=str,
		required=True,
		help='Full or relative path to the processed expanded URL csv file from process_expanded_url_data.py. E.g. results/my_data.csv',
	)
	p.add_argument(
		'-of',
		'--output-filename',
		type=str,
		required=True,
		help='Full or relative path store resulting csv files (will be edited with suffixes). E.g. results/my_data.csv',
	)
	p.add_argument(
		'--csv-sep',
		type=str,
		default=',',
		choices=[',', ';', '\\t', '|'],
		help='Separator for your csv files (do not enter/change if output is from other scripts). Default: ","',
	)
	args = vars(p.parse_args())
	expand_media_metrics(args)
