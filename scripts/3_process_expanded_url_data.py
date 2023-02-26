"""
STEP THREE IN MEDIA PIPELINE
"""
import argparse
import csv
from urllib.parse import urlparse, parse_qs, urljoin, urlencode

import pandas as pd
import tldextract

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
	'ref',
]

def get_domain(url):
	extracted = tldextract.extract(url)
	return f'{extracted.domain}.{extracted.suffix}'


def get_subdomain(url):
	subdomain = tldextract.extract(url).subdomain
	return subdomain if subdomain != 'www' else ''


def clean_queries(row):
	url = row['expanded_url']
	parsed_url = urlparse(url)
	query = parse_qs(parsed_url.query)

	# 1. youtube
	if 'youtube' in row['root_domain'] and 'v' in query:
		v_id = query['v'][0]
		return f'https://youtube.com/watch?v={v_id}'

	# 2. Campaign info
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
	file_name = args['expanded_url_filename']
	sep = args['csv_sep']

	print(f'Reading expanded URL data from {file_name}...')
	expanded_df = pd.read_csv(file_name, encoding='utf-8', sep=sep)

	print(f'Getting root domains...')
	expanded_df['root_domain'] = expanded_df['expanded_url'].apply(get_domain)

	print(f'Getting subdomains...')
	expanded_df['sub_domain'] = expanded_df['expanded_url'].apply(get_subdomain)

	print(f'Cleaning links...')
	expanded_df['clean_expanded_url'] = expanded_df.apply(clean_queries, axis=1)
	expanded_df = expanded_df[['url', 'expanded_url', 'clean_expanded_url', 'domain', 'root_domain', 'sub_domain']]
	
	save_file_name = file_name.removesuffix('.csv') + '_processed' + '.csv'
	print(f'Saving processed expanded URL data to {save_file_name}...')
	expanded_df.to_csv(save_file_name, mode='w+',index=False, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)

	print('Done!')



if __name__ == '__main__':
	pd.options.mode.chained_assignment = None
	p = argparse.ArgumentParser(description='Get and aggregate data for Media URL metrics (more granular than get_metrics.py)')
	p.add_argument(
		'-euf',
		'--expanded-url-filename',
		type=str,
		required=True,
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
	process_expanded_df(args)
