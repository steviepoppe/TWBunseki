"""
STEP 2 IN MEDIA PIPELINE
"""
import asyncio
import argparse
import csv
import re
import requests
from urllib.parse import urlparse

import aiohttp
import pandas as pd


async def reanalyze(args):

	file_name = args['filename']
	max_redirect_depth = args['max_redirect_depth']
	chunksize = args['chunk_size']
	sep = args['csv_sep']

	df = pd.read_csv(file_name, encoding='utf-8', sep=sep)

	if 'url' not in df:
		print('URL column is required to re-analyze. Aborting.')
		return

	df_records = df.to_dict(orient='records')
	print('Re-analyzing media URLs for error_expanding == True')

	tmp_file_name = file_name + '.tmp'
	mode = 'w+'
	expanded_df_records = []
	for i in range(0, len(df_records), chunksize):
		print(f'Analyzing rows from {i} to {i+chunksize}')
		chunk = df_records[i:i+chunksize]
		expanded_chunk = await expand_media_urls(chunk, max_redirect_depth)
		expanded_df_records.extend(expanded_chunk)
		print('--> writing tmp data...')
		tmp_df = pd.DataFrame.from_records(expanded_chunk)
		tmp_df.to_csv(tmp_file_name, mode=mode, index=False, encoding='utf-8', errors='backslashreplace', quoting=csv.QUOTE_NONNUMERIC)
		mode = 'a'
	print('Done processing!')
	print('Overwriting original file..')
	result_df = pd.DataFrame.from_records(expanded_df_records)
	print(f'Writing raw data to {file_name}...')
	result_df.to_csv(file_name, mode='w+',index=False, encoding='utf-8', errors='backslashreplace', quoting=csv.QUOTE_NONNUMERIC)

	grouped_filename = file_name.removesuffix('.csv') + '_grouped' + '.csv'
	print(f'Writing grouped data by URL to {grouped_filename}...')
	result_df.groupby("expanded_url").sum().reset_index().to_csv(f'{grouped_filename}', mode='w+',index=False, errors='backslashreplace', encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)

	errors_before = len(df[df.error_expanding == True])
	errors_after = len(result_df[result_df.error_expanding == True])
	print(f'Done! Errors before: {errors_before} & errors after: {errors_after}.')


async def expand_media_urls(df_records, max_redirect_depth):
	result_records = []
	async with aiohttp.ClientSession() as session:
		tasks = []
		for row in df_records:
			if str(row['error_expanding']).lower() == 'true':
				tasks.append(asyncio.ensure_future(expand_url(session, row, max_redirect_depth)))
			else:
				result_records.append(row)
		skipped = len(result_records)
		print(f'Skipped re-analysis for {skipped} rows as error_expanding == False')
		expanded_rows = await asyncio.gather(*tasks)
	result_records.extend(expanded_rows)
	return result_records


async def expand_url(session, row, max_redirect_depth):
	url = row['url']
	expanded = ''
	domain = ''
	redirect = 0
	next_url = url
	try:
		while redirect < max_redirect_depth:
			async with session.head(next_url, allow_redirects=False) as res:
				next_url = res.headers.get('location', res.headers.get('X-Redirect-To',''))
			if next_url == '':
				break
			if next_url.startswith('/'):
				next_url =  'https://' + domain + next_url
			expanded = next_url
			domain = urlparse(expanded).netloc or domain  # if no domain, keep last known domain
			redirect += 1
	except Exception:
		pass
	error = expanded == ''
	expanded_row = row
	expanded_row['error_expanding'] = error
	expanded_row['expanded_url'] = expanded
	expanded_row['domain'] = domain
	return expanded_row


if __name__ == '__main__':
	p = argparse.ArgumentParser(description='Analyze metrics for a Twitter corpus w/ format compatible with twitter_search.py')
	p.add_argument(
		'-f',
		'--filename',
		type=str,
		required=True,
		help='Full or relative path to the csv file. E.g. results/my_data.csv',
	)
	p.add_argument(
		'-c',
		'--chunk-size',
		type=int,
		default=10000,
		help='Size of processing chunk. Default: 10K rows'
	)
	p.add_argument(
		'--max-redirect-depth',
		type=int,
		default=1,
		help='Max depth to follow redirects when analyzing URLs. Default is the minimum: 1 (get link after t.co). WARNING: exponentially slower with each added layer of depth'
	)
	p.add_argument(
		'--csv-sep',
		type=str,
		default=',',
		choices=[',', ';', '\\t', '|'],
		help='Separator for your csv file. Default: ","',
	)

	args = vars(p.parse_args())
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
	asyncio.run(reanalyze(args))
