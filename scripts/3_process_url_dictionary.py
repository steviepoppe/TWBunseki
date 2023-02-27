"""
STEP THREE IN MEDIA PIPELINE
"""
import argparse
import csv
from urllib.parse import urlparse, parse_qs, urljoin, urlencode

import pandas as pd
import tldextract
from tqdm import tqdm

UNWANTED_QUERIES = [
	'utm_source',
	'utm_medium',
	'utm_campaign',
	'utm_term',
	'utm_content',
	'_utm_source',
	'_utm_medium',
	'_utm_campaign',
	'_utm_term',
	'_utm_content',
	'fbclid',
	'gclid',
	'ref',
]

def get_domain(url):
	extracted = tldextract.extract(url)
	return f'{extracted.domain}.{extracted.suffix}'


def get_subdomain(url):
	subdomain = tldextract.extract(url).subdomain
	return subdomain if subdomain != 'www' else ''


def get_suffix(url):
	extracted = tldextract.extract(url)
	return extracted.suffix


def follow_google(url):
	parsed_url = urlparse(url)
	query = parse_qs(parsed_url.query)
	domain = get_domain(url)

	if domain.startswith('google.com') and (parsed_url.path == '/url' or parsed_url.path == '/news/url') and 'url' in query:
		return query['url'][0]

	return url

def clean_queries(row):
	url = row['expanded_url']
	parsed_url = urlparse(url)
	query = parse_qs(parsed_url.query)

	# 1. youtube
	if 'youtube' in row['root_domain'] and 'v' in query:
		v_id = query['v'][0]
		return f'https://youtube.com/watch?v={v_id}'

	# 2. Remove Campaign info
	queryless_url = urljoin(url, parsed_url.path)
	if not queryless_url.endswith('/'):
		queryless_url += '/'
	if query:
		for unwanted_query in UNWANTED_QUERIES:
			if unwanted_query in query:
				query.pop(unwanted_query)
		if 'page' in query and query['page'][0] == '1':
			query.pop('page')
		if query:
			querystring = urlencode(query, doseq=True)
			return queryless_url + f'?{querystring}'
	return queryless_url


def process_expanded_df(args):
	file_name = args['dictionary_filename']

	print(f'Reading expanded URL data from {file_name}...')
	expanded_df = pd.read_csv(file_name, encoding='utf-8', sep=sep)

	print(f'Following Google redirect URLs...')
	expanded_df['expanded_url'] = expanded_df['expanded_url'].apply(follow_google)

	print(f'Getting root domains...')
	expanded_df['root_domain'] = expanded_df['expanded_url'].apply(get_domain)

	print(f'Getting subdomains...')
	expanded_df['sub_domain'] = expanded_df['expanded_url'].apply(get_subdomain)

	print(f'Getting suffixes...')
	expanded_df['suffix'] = expanded_df['expanded_url'].apply(get_suffix)

	print(f'Cleaning links...')
	expanded_df['clean_expanded_url'] = expanded_df.apply(clean_queries, axis=1)
	expanded_df = expanded_df[['url', 'expanded_url', 'clean_expanded_url', 'domain', 'root_domain', 'sub_domain', 'suffix', 'total_tweets_in_set']]
	
	save_file_name = file_name.removesuffix('.csv') + '_processed_for_expand_media_metrics' + '.csv'
	print(f'Saving URL dictionary data to {save_file_name}...')
	expanded_df.to_csv(save_file_name, mode='w+',index=False, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)

	print('Done!')



if __name__ == '__main__':
	pd.options.mode.chained_assignment = None
	p = argparse.ArgumentParser(description='Get and aggregate data for Media URL metrics (more granular than get_metrics.py)')
	p.add_argument(
		'-df',
		'--dictionary-filename',
		type=str,
		required=True,
		help='Full or relative path to the dictionary csv file. E.g. results/my_data.csv',
	)
	args = vars(p.parse_args())
	process_expanded_df(args)
