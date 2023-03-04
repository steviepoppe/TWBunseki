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

	print('> excluding twitter.com, archive.org, megalodon.jp links')
	# exclude twitter.com links
	unique_df = unique_df[~unique_df['root_domain'].isin(['twitter.com', 'archive.org', 'megalodon.jp'])]

	print('> generating column')
	# generate column
	unique_df['archive_url'] = unique_df.apply(
		lambda x: 'https://web.archive.org/web/' + str(x['created_at'].year) + '%02d' % x['created_at'].month + '%02d' % x['created_at'].day + '/' + str(x['expanded_url']),
		axis=1,
	)
	return unique_df


def save_df(df, file_name, suffix, index=False):
	save_file_name = file_name.removesuffix('.csv') + suffix + '.csv'
	print(f'Saving data to {save_file_name}...')
	df.to_csv(save_file_name, mode='w+', index=index, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)


def expand_media_metrics(args):
	data_per_tweet_file_name = args['tweet_links_filename']
	processed_expanded_file_name = args['dictionary_filename']
	output_filename = args['output_filename']

	print(f'Reading tweet links csv from {data_per_tweet_file_name}...')
	tweet_data_df = pd.read_csv(data_per_tweet_file_name, encoding='utf-8')
	tweet_data_df.created_at = pd.to_datetime(tweet_data_df.created_at)

	print(f'Reading URL dictionary data from {processed_expanded_file_name}...')
	expanded_df = pd.read_csv(processed_expanded_file_name, encoding='utf-8')

	merged_df = tweet_data_df.merge(expanded_df, how='left', on=['url', 'user_screen_name'])
	if 'total_tweets_in_set' in merged_df:
		merged_df = merged_df.drop(columns=['total_tweets_in_set'])

	archived_df = add_archive_links(merged_df)
	save_df(archived_df, output_filename, '_with_archived_links')

	merged_df['month'] = merged_df['created_at'].dt.month_name()
	merged_df['year'] = merged_df['created_at'].dt.year

	merged_df = merged_df.assign(total_tweets_in_set=1)
	print('Excluding all twitter.com data...')
	merged_df = merged_df[merged_df['root_domain'] != 'twitter.com']

	## ALL TIM
	# 1. group by URL, all time stats
	group_df = merged_df[['user_screen_name', 'tweet_retweet_count', 'total_tweets_in_set', 'expanded_url']]
	group_df = group_df.groupby('expanded_url').agg({'user_screen_name': 'nunique', 'tweet_retweet_count': sum, 'total_tweets_in_set': sum}).reset_index()
	save_df(group_df, output_filename, '_group_by_url_all_time')

	# 2. group by root domain, all time stats
	group_df = merged_df[['user_screen_name', 'tweet_retweet_count', 'total_tweets_in_set', 'root_domain']]
	group_df = group_df.groupby('root_domain').agg({'user_screen_name': 'nunique', 'tweet_retweet_count': sum, 'total_tweets_in_set': sum}).reset_index()
	save_df(group_df, output_filename, '_group_by_root_domain_all_time')

	# 3. group by sub domain, all time stats
	group_df = merged_df[['user_screen_name', 'tweet_retweet_count', 'total_tweets_in_set', 'sub_domain', 'root_domain']]
	group_df = group_df[group_df['sub_domain'].notna()]
	group_df['sub_domain'] = group_df.apply(lambda x: x['sub_domain'] + '.' +  x['root_domain'], axis=1)
	group_df = group_df.drop(columns=['root_domain'])
	group_df = group_df.groupby('sub_domain').agg({'user_screen_name': 'nunique', 'tweet_retweet_count': sum, 'total_tweets_in_set': sum}).reset_index()
	save_df(group_df, output_filename, '_group_by_subdomain_all_time')

	# ------------

	## BY MONTH


	# 4. group by root domain, over time stats
	group_df = merged_df[['user_screen_name', 'tweet_retweet_count', 'total_tweets_in_set', 'root_domain', 'month', 'year']]
	group_df = group_df.groupby(['root_domain', 'month', 'year']).agg({'user_screen_name': 'nunique', 'tweet_retweet_count': sum, 'total_tweets_in_set': sum}).reset_index()
	save_df(group_df, output_filename, '_group_by_root_domain_by_month_year')

	# 5. group by sub domain, all time stats
	group_df = merged_df[['user_screen_name', 'tweet_retweet_count', 'total_tweets_in_set', 'sub_domain', 'root_domain', 'month', 'year']]
	group_df = group_df[group_df['sub_domain'].notna()]
	group_df['sub_domain'] = group_df.apply(lambda x: x['sub_domain'] + '.' +  x['root_domain'], axis=1)
	group_df = group_df.drop(columns=['root_domain'])
	group_df = group_df.groupby(['sub_domain', 'month', 'year']).agg({'user_screen_name': 'nunique', 'tweet_retweet_count': sum, 'total_tweets_in_set': sum}).reset_index()
	save_df(group_df, output_filename, '_group_by_subdomain_by_month_year')

	# 6. group by URL, all time stats
	group_df = merged_df[['user_screen_name', 'tweet_retweet_count', 'total_tweets_in_set', 'expanded_url', 'month', 'year']]
	group_df = group_df.groupby(['expanded_url', 'month', 'year']).agg({'user_screen_name': 'nunique', 'tweet_retweet_count': sum, 'total_tweets_in_set': sum}).reset_index()
	save_df(group_df, output_filename, '_group_by_url_by_month_year')

	print('Done!')



if __name__ == '__main__':
	pd.options.mode.chained_assignment = None
	p = argparse.ArgumentParser(description='Get and aggregate data for Media URL metrics (more granular than get_metrics.py)')
	p.add_argument(
		'-lf',
		'--tweet-links-filename',
		type=str,
		required=True,
		help='Full or relative path to the tweet links csv file from extract_media.py. E.g. results/my_data.csv',
	)
	p.add_argument(
		'-df',
		'--dictionary-filename',
		type=str,
		required=True,
		help='Full or relative path to the processed URL dictionary csv file from process_url_dictionary.py. E.g. results/my_data.csv',
	)
	p.add_argument(
		'-of',
		'--output-filename',
		type=str,
		required=True,
		help='Full or relative path store resulting csv files (will be edited with suffixes). E.g. results/my_data.csv',
	)
	args = vars(p.parse_args())
	expand_media_metrics(args)
