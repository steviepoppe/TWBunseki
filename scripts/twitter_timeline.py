"""
Run:
0. Fill BEARER_TOKEN in a file called settings.py
1. Install pandas and tweepy (`$ pip install pandas tweepy`)
2. Get all arguments from `$ python twitter_timeline.py --help`
"""
import argparse
import sys
import time
import os
import traceback
from pathlib import Path
from csv import QUOTE_NONNUMERIC
from datetime import datetime, timedelta

import tweepy
import pandas as pd

from settings import BEARER_TOKEN


def search_tweets(args):
	client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True)

	Path('./results/').mkdir(parents=True, exist_ok=True)

	filename = args['filename']
	key_file_name = f'./results/{filename}_ID_keys.csv'
	keys_exists = os.path.isfile(key_file_name)
	
	if keys_exists:
		with open(key_file_name, mode='r') as file:
			temp_earliest_id, temp_most_recent_id = file.read().split(',')

	tweet_total_count, session_earliest_id, session_most_recent_id = process_tweets(client, args, keys_exists)
	
	print(f"Finished process. Downloaded {tweet_total_count} total tweets. This session's oldest tweet ID was {session_earliest_id} and most newest tweet ID was {session_most_recent_id}")

	earliest_id = args['until_id']
	most_recent_id = args['from_id']
	with open(key_file_name, mode='w+') as file:
		if earliest_id is not None:
			most_recent_id = temp_most_recent_id
			earliest_id = session_earliest_id
		elif most_recent_id is not None:
			most_recent_id = session_most_recent_id
			earliest_id = temp_earliest_id	
		else:
			most_recent_id = session_most_recent_id
			earliest_id = session_most_recent_id	

		file.write(f'{earliest_id},{most_recent_id}')

def process_tweets(client, args, keys_exists):

	first_page = True
	session_most_recent_id, session_earliest_id = None, None


	tweet_count = 0
	try:
		for page in tweepy.Paginator(
				client.get_users_tweets, args['user_id'],
				user_fields='verified,description,username,created_at,public_metrics',	
				expansions='author_id,referenced_tweets.id,referenced_tweets.id.author_id',
				tweet_fields='created_at,lang,public_metrics,conversation_id,entities,attachments,referenced_tweets,in_reply_to_user_id',
                max_results=min(args['max_per_page'], 100), since_id=args['from_id'], until_id=args['until_id'],
                start_time=args['from_date'], end_time=args['to_date'],
            ):

			tweets = page[0]
			tweet_list = list()
			if not tweets:
				print('No tweets found.')
				continue

			users = {str(x.id): x.data for x in page[1].get('users', [])}
			referenced_tweets = {str(x.id): x.data for x in page[1].get('tweets', [])}

			for tweet_obj in tweets:
				tweet = tweet_obj.data
				user = users[tweet['author_id']]

				tweet_row = {}

				# meta
				tweet_row["tweet_id"] = str(tweet["id"])
				tweet_row["text"] = tweet["text"]
				tweet_row["created_at"] = tweet["created_at"]
				tweet_row["lang"] = tweet["lang"]

				# entities
				tweet_row["hashtags"] = ""
				tweet_row["user_mentions"] = ""
				tweet_row["urls"] = ""

				if "entities" in tweet:
					if 'hashtags' in tweet["entities"]:
						tweet_row["hashtags"] = ','.join([x['tag'] for x in tweet["entities"]["hashtags"]])
					if 'user_mentions' in tweet["entities"]:
						tweet_row["user_mentions"] = ','.join([x['username'] for x in tweet["entities"]["mentions"]])
					if 'urls' in tweet["entities"]:
						for x in tweet["entities"]["urls"]:
							urls = []
							if 'unwound_url' in x:
								urls.append(x['unwound_url'])
							elif 'expanded_url' in x:
								urls.append(x['expanded_url'])
							else:
								urls.append(x['url'])

						tweet_row["urls"] = ','.join(urls)
						
				# user data
				tweet_row["user_screen_name"] = user["username"]
				tweet_row["user_id"] = user["id"]
				tweet_row["user_description"] = user["description"]
				tweet_row["user_following_count"] = user["public_metrics"]["following_count"]
				tweet_row["user_followers_count"] = user["public_metrics"]["followers_count"]
				tweet_row["user_total_tweets"] = user["public_metrics"]["tweet_count"]
				tweet_row["user_created_at"] = user["created_at"]
				tweet_row["user_verified"] = user["verified"]

				# public metrics per tweet
				tweet_row["tweet_favorite_count"] = tweet["public_metrics"]["like_count"]
				tweet_row["tweet_retweet_count"] = tweet["public_metrics"]["retweet_count"]
				tweet_row["tweet_reply_count"] = tweet["public_metrics"]["reply_count"]
				tweet_row["tweet_quote_count"] = tweet["public_metrics"]["quote_count"]

				# retweets and replies
				tweet_row["is_retweet"] = False
				tweet_row["retweet_id"] = ""
				tweet_row["retweet_created_at"] = ""
				tweet_row["is_quote"] = False
				tweet_row["quote_id"] = ""
				tweet_row["is_reply"] = False
				tweet_row["replied_to_tweet_id"] = "" 
				tweet_row["conversation_id"] = str(tweet["conversation_id"])
				tweet_row["in_reply_to_user_id"] = ""
				tweet_row["possibly_sensitive"] = ""

				if 'in_reply_to_user_id' in tweet:
					tweet_row["in_reply_to_user_id"] = str(tweet["in_reply_to_user_id"])
				if 'possibly_sensitive' in tweet:
					tweet_row["possibly_sensitive"] = tweet["possibly_sensitive"]

				if "referenced_tweets" in tweet:
					if args['keep_rt']:
						retweets = [x for x in tweet["referenced_tweets"] if x["type"] == "retweeted"]
						if len(retweets) > 0:
							retweet_id = retweets[0]["id"]  # there can only be 1 retweeted ref tweet
							retweet = referenced_tweets[retweet_id]
							retweet_user = users[retweet['author_id']]
							tweet_row["is_retweet"] = True
							tweet_row["retweet_id"] = str(retweet_id)
							tweet_row["retweet_created_at"] = retweet['created_at']	
							tweet_row["text"] = "RT @" + retweet_user['username'] + ": " + retweet['text']

					quotes = [x for x in tweet["referenced_tweets"] if x["type"] == "quoted"]
					if len(quotes) > 0:
						tweet_row["quote_id"] = str(quotes[0]["id"])
						tweet_row["is_quote"] = True

					replied_to = [x for x in tweet["referenced_tweets"] if x["type"] == "replied_to"]
					if len(replied_to) > 0:
						tweet_row["replied_to_tweet_id"] = str(replied_to[0]["id"])
						tweet_row["is_reply"] = True

				tweet_row["text"] = tweet_row["text"].strip()
				tweet_list.append(tweet_row)

				if tweet_count == 0:
					session_most_recent_id = tweet["id"]
				if args['until_id'] != tweet["id"]:
					session_earliest_id = tweet["id"]
				
				tweet_count += 1

			tweet_csv = pd.DataFrame(tweet_list)
			filename = args['filename']
			if first_page and not keys_exists and args['is_first']:
				tweet_csv.to_csv(f'./results/{filename}.csv', index=False, mode="w+", encoding="utf-8", quoting=QUOTE_NONNUMERIC)
			else:
				# should edit header stuff here for adding to the file later
				tweet_csv.to_csv(f'./results/{filename}.csv', header=False, index=False, mode="a", encoding="utf-8", quoting=QUOTE_NONNUMERIC)

			print("Downloaded %d tweets" % tweet_count)	
			first_page = False

	except KeyboardInterrupt:
		print("Process terminated. Downloaded %d total tweets. This session's oldest tweet ID was %s and most newest tweet ID was %s" % (tweet_count, session_earliest_id, session_most_recent_id))
	except:
		print(traceback.exc_info())
		print("Downloaded %d total tweets. This session's oldest tweet ID was %s and most newest tweet ID was %s" % (tweet_count, session_earliest_id, session_most_recent_id))

	return tweet_count, session_earliest_id, session_most_recent_id

if __name__ == '__main__':
	p = argparse.ArgumentParser(description='Fetch data from Twitter using search params and save to csv')
	p.add_argument(
		'-uids',
		'--user_ids',
		type=str,
		required=True,
	)
	p.add_argument(
		'-f',
		'--filename',
		type=str,
		help='Required if you want to resume in a specific file. Default: search query + timestamp',
	)
	p.add_argument(
		'-ui',
		'--until-id',
		type=str,
		help='Until which ID do you want to fetch/resume fetching tweets? If not specified, no limits',
	)
	p.add_argument(
		'-fi',
		'--from-id',
		type=str,
		help='From which ID do you want to fetch/resume fetching tweets? If not specified, no limits',
	)
	p.add_argument(
		'--no-keep-rt',
		action='store_true',
		help='Use this to NOT store retweet-related data',
	)
	p.add_argument(
		'-m',
		'--max-per-page',
		type=int,
		default=100,
		help='Default is 100 which is max'
	)
	p.add_argument(
		'-fd',
		'--from-date',
		type=str,
		help='Format: YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339)'
	)
	p.add_argument(
		'-td',
		'--to-date',
		type=str,
		help='Format: YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339)'
	)
	# default filename here
	args = vars(p.parse_args())

	if args['filename'] is None:
		args['filename'] = args['user_ids'] + '_' + str(int(time.time()))

	args['keep_rt'] = not args['no_keep_rt']

	args['is_first'] = True
	for user_id in args['user_ids'].split(','):
		args['user_id'] = user_id.strip()
		search_tweets(args)
		args['is_first'] = False
