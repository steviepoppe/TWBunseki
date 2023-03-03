"""
STEP THREE IN MEDIA PIPELINE
"""
import argparse
import csv
from urllib.parse import urlparse, parse_qs, urljoin, urlencode

import pandas as pd
import tldextract
from tqdm import tqdm
import requests

UNWANTED_QUERIES = [
	'utm_source',
	'utm_medium',
	'utm_campaign',
	'utm_term',
	'utm_content',
	'utm_int',
	'_utm_source',
	'_utm_medium',
	'_utm_campaign',
	'_utm_term',
	'_utm_content',
	'_utm_int',
	'fbclid',
	'gclid',
	'ocid',
	'ref',
	'language',
	'from',
	'device',
	'_gl',
	'iref',
	'locale',
	'reflink',
	'cx_fm',
	'cx_ml',
	'cx_mdate',
	'source',
	'display',
	'fm',
	'tag',
	'recruiter',
	'sns',
	'igshid',
	'dicbo',
	'vlang',
	'share_id',
]

REDIRECTS = [
	('https://approach.yahoo.co.jp', 'src'),
	('https://pt.afl.rakuten.co.jp/c/', 'pc'),
	('https://hb.afl.rakuten.co.jp', 'pc'),
	('https://al.dmm.com/', 'lurl'),
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
	if row['root_domain'] == 'youtu.be':
		v_id = url.path[1:]
		return f'https://youtube.com/watch?v={v_id}'

	# 2. direct redirect from URL
	if row['root_domain'] == 'ampshare.org' and 'ampshare' in query:
		url = query['ampshare'][0]
		parsed_url = urlparse(url)
		query = parse_qs(parsed_url.query)
	for prefix, query_keyword in REDIRECTS:
		if url.startswith(prefix) and query_keyword in query:
			url = query[query_keyword][0]
			parsed_url = urlparse(url)
			query = parse_qs(parsed_url.query)
			break

	# 3. Remove Campaign info
	if url == parsed_url.path:
		queryless_url = url
	else:
		queryless_url = urljoin(url, parsed_url.path)
	if row['root_domain'].startswith('amazon.') or row['root_domain'] ín ['twitcasting.tv','nikkei.com','sankei.com', 'tiktok.com']:
		return queryless_url
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
	expanded_df = pd.read_csv(file_name, encoding='utf-8')

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
	expanded_df['clean_expanded_url'] = expanded_df['clean_expanded_url'].apply(requests.utils.unquote)
	expanded_df = expanded_df[['url', 'expanded_url',  'user_screen_name', 'clean_expanded_url', 'domain', 'root_domain', 'sub_domain', 'suffix', 'total_tweets_in_set']]
	
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
