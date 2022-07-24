"""
This python script accesses the Twitter Search API using the third-party python plug-in tweepy
When running from the command prompt, it expects at least one argument: the search query
(optionally, just input the search query in the global variable search_query)
Results are saved as csv in a './results/' subdirectory (contains a ton of valuable meta-data)
Names of the saved files are based on the search query
The process can be terminated at any time using ctrl-c; the last ID will be printed before exit

Use the last ID as earliest_id to continue mining tweets tweeted 
before the max time span collected until process termination

"""
import sys
import os
from pathlib import Path
from csv import QUOTE_NONNUMERIC
from datetime import datetime, timedelta
import tweepy

import pandas as pd

from settings import BEARER_TOKEN


# SETTINGS
# --------

# SET EITHER OF THESE IF WANTING TO RESUME PROGRESS else set to None
earliest_id = None  # Optional: Until which ID?
most_recent_id = None  # Optional: From which ID onward?

# Different query when having an academic account
academic = True  # non-academic, recent-search has a limit of 450 calls per 15 minute, x100 = 4500 tweets. Academic = 3000

# Other settings
keep_rt = True
max_results_per_page = 500 #default = 100, academic = 500 (suspended content gets filtered after retrieval, so per page you may get fewer results)

save_file_name = 'retrieved_tweets'

search_query = 'spaghetti'

#format: YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339)
fromdate = None
todate = None

# ==========================================

# SCRIPT AUTOMATED VARIABLES; DO NOT TOUCH
# To Check whether we have stored keys
keys_exists = False

## EXTRA DO NOT TOUCH
session_earliest_id = None
session_most_recent_id = None

# ==========================================

def search_tweets(sys_args):

	global earliest_id
	global most_recent_id
	global search_query
	global keys_exists
	global save_file_name

	# overwrite script settings with sys arguments

	#Search queries can be single terms or more intricate queries. 
	#When passing queries from the command prompt, they should be formatted within double quotation marks, with exact terms of several words in single quotes
	# e.g. Multiple keywords (AND): "apple banana" | "'apple cake' 'banana bread' 'orange juice'"
	# OR expressions: "banana OR carrot" | "'banana bread' OR 'ginger ale'"
	# for more, see http://t.co/operators and https://developer.twitter.com/en/docs/twitter-api/premium/search-api/api-reference/premium-search
	if len(sys_args) > 1:
		search_query = str(sys_args[1]).replace('\'', '\"')
		print(search_query)
	if len(sys_args) > 2:
		save_file_name = sys_args[2]
#	else:
#		save_file_name = search_query
	if len(sys_args) > 3:
		earliest_id = sys_args[3]
	if len(sys_args) > 4:
		most_recent_id = sys_args[4]


	client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True)

	Path('./results/').mkdir(parents=True, exist_ok=True)

	key_file_name = f'./results/{save_file_name}_ID_keys.csv'
	keys_exists = os.path.isfile(key_file_name)
	
	if keys_exists:
		with open(key_file_name, mode='r') as file:
			temp_earliest_id, temp_most_recent_id = file.read().split(',')

	tweet_total_count = process_tweets(client, search_query, save_file_name)
	
	print(f"Finished process. Downloaded {tweet_total_count} total tweets. This session's oldest tweet ID was {session_earliest_id} and most recent tweet ID was {session_most_recent_id}")

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

def process_tweets(client, search_query, save_file_name):

	first_page = True

	global session_earliest_id
	global session_most_recent_id

	search_endpoint = client.search_recent_tweets if not academic else client.search_all_tweets

	tweet_count = 0
	try:
		for page in tweepy.Paginator(
				search_endpoint, search_query,
				user_fields='verified,description,username,created_at,public_metrics',	
				expansions='author_id,referenced_tweets.id,referenced_tweets.id.author_id',
				tweet_fields='created_at,lang,public_metrics,conversation_id,entities,attachments,referenced_tweets,in_reply_to_user_id',
                max_results=max_results_per_page, since_id=most_recent_id, until_id=earliest_id,
                start_time=fromdate, end_time=todate,
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
					if keep_rt:
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
				if earliest_id != tweet["id"]:
					session_earliest_id = tweet["id"]
				
				tweet_count += 1

			tweet_csv = pd.DataFrame(tweet_list)	
			if first_page and not keys_exists:
				tweet_csv.to_csv(f'./results/{save_file_name}.csv', index=False, mode="w+", encoding="utf-8", quoting=QUOTE_NONNUMERIC)
			else:
				# should edit header stuff here for adding to the file later
				tweet_csv.to_csv(f'./results/{save_file_name}.csv', header=False, index=False, mode="a", encoding="utf-8", quoting=QUOTE_NONNUMERIC)

			print("Downloaded %d tweets" % tweet_count)	
			first_page = False

	except KeyboardInterrupt:
		print("Process terminated. Downloaded %d total tweets. This session's oldest tweet ID was %s and most newest tweet ID was %s" % (tweet_count, session_earliest_id, session_most_recent_id))
	except tweepy.errors.TweepyException as exception:
		print("Error: %s. Downloaded %d total tweets. This session's oldest tweet ID was %s and most newest tweet ID was %s" % (tweet_count, session_earliest_id, session_most_recent_id))

	return tweet_count

if __name__ == '__main__':
	search_tweets(sys.argv)
