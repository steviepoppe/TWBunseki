"""
Categorize text using keywords (if keyword in text, text belongs to category).

Run:
- Install requirements (`$ pip install pandas`)
- Have json file ready with categories in the following format:
    ```json
    {
        "categories": {
            "category_1": ["keyword1", "keyword2"],
            "category_2": ["keyword3"]
        }
    }
    ```
- Have csv file ready with text column at least (other columns allowed + preserved)
- Run `$ python categorize.py --help` for exact arguments
"""

import argparse
import json
from csv import QUOTE_NONNUMERIC

import pandas as pd


def clean_keywords(categories):
    for category in categories:
        categories[category] = [x.strip().lower() for x in categories[category]]
    return categories


def belongs(category, keywords, freq, text):
    belongs = 0
    for keyword in keywords:
        freq[keyword] = freq.get(keyword, 0)
        if keyword in text.lower():
            freq[keyword] += 1
            belongs = 1
    return belongs


def categorize(categories, df, text_col):
    categories = clean_keywords(categories)
    freq = {}
    df[text_col] = df[text_col].astype(str)

    for category in categories:
        df[category] = df[text_col].apply(lambda x: belongs(category, categories[category], freq, x))


    freq_data = [{'keyword': k, 'frequency': v} for k, v in freq.items()]
    freq_df = pd.DataFrame(freq_data)
    return df, freq_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Categorize a csv file using keywords')
    parser.add_argument(
        '-c',
        '--categories',
        type=str,
        required=True,
        help='Path to JSON file with categories (see categories.json.example)',
    )
    parser.add_argument(
        '-i',
        '--input-data',
        type=str,
        required=True,
        help='Path to input data csv file with rows',
    )
    parser.add_argument(
        '-o',
        '--output-data',
        type=str,
        default='results/categorize_output.csv',
        help='Path to save output data csv file. Default: "results/categorize_output.csv"',
    )
    parser.add_argument(
        '-of',
        '--output-frequencies',
        type=str,
        default='results/keyword_frequencies.csv',
        help='Path to save output data csv file. Default: "results/keyword_frequencies.csv"',
    )
    parser.add_argument(
        '-t',
        '--text-column',
        type=str,
        default='text',
        help='Name of the column with the text data. Default: "text"',
    )

    args = vars(parser.parse_args())

    categories = {}
    with open(args['categories'], encoding='utf-8') as f:
        categories = json.loads(f.read())['categories']

    df = pd.read_csv(args['input_data'])
    print('Categorizing...')
    df, freq_df = categorize(categories=categories, df=df, text_col=args['text_column'])
    df.to_csv(args['output_data'], mode='w+', encoding='utf-8', index=False, quoting=QUOTE_NONNUMERIC)
    freq_df.to_csv(args['output_frequencies'], mode='w+', encoding='utf-8', index=False, quoting=QUOTE_NONNUMERIC)
    print('Done!')
