import argparse
from csv import QUOTE_NONNUMERIC
import itertools
import re

import pandas as pd


def filter_by_date(df, args):
    print('Filtering by date params..')
    date_col = args['date_col']
    require_tz_aware = args['timezone'] is not None
    df[date_col] = pd.to_datetime(df[date_col], utc=require_tz_aware)

    if args['timezone']:
        df[date_col] = df[date_col].dt.tz_convert(tz=args['timezone'])

    if args['from_date']:
        df = df[df[date_col] >= args['from_date']]

    if args['to_date']:
        df = df[df[date_col] <= args['to_date']]

    df[date_col] = df[date_col].apply(str)
    return df


def filter_by_cols(df, args):
    print('Filtering by provided columns..')
    cols = list(itertools.chain.from_iterable([x.split(',') for x in args['col']]))  # support comma sep values
    cols = [x.strip() for x in cols]
    df = df[cols]
    return df


def filter_by_text_query(df, args):
    def _or(first, second):
        return first | second

    def _and(first, second):
        return first & second

    def _not(first):
        return ~first

    print('Filtering by provided query..')
    query = args['query']

    # first, split
    queries = re.findall(r'\'.+?\'|".+?"|\w+' , query)
    queries = [x.strip().strip('\'').strip('"') for x in queries]

    select_prev = None
    op_prev = None
    not_prev = False
    # keyword, op, keyword
    for part in queries:
        is_op = part in ['OR', 'AND']
        if is_op:
            if not op_prev:
                op_prev = part
            else:
                raise Exception('Malformed query. Expected: KEYWORD AND/OR KEYWORD')
            not_prev = False
        elif part == 'NOT':
            not_prev = True
        else:
            select = df[args['text_col']].str.contains(part, case=False)
            if not_prev:
                select = _not(select)

            if select_prev is None:
                select_prev = select
            else:
                if op_prev == 'OR':
                    select_prev = _or(select_prev, select)
                elif op_prev == 'AND':
                    select_prev = _and(select_prev, select)
                else:
                    raise Exception('Malformed query. Expected: KEYWORD AND/OR KEYWORD')
                op_prev = None
            not_prev = False

    if select_prev is None:
        raise Exception('Malformed query. Expected: KEYWORD AND/OR KEYWORD')
    return df[select_prev]


def filter_data(args):
    print('Reading csv into dataframe..')
    df = pd.read_csv(args['filename'])

    if args['from_date'] or args['to_date'] or args['timezone']:
        df = filter_by_date(df, args)

    if args['query']:
        df = filter_by_text_query(df, args)

    if args['col']:  # has to be last in case other filtering involves excluded columns
        df = filter_by_cols(df, args)

    print(f"Finished filtering. Saving into {args['output_filename']}..")
    df.to_csv(args['output_filename'], encoding='utf-8', index=False, mode='w+', quoting=QUOTE_NONNUMERIC)

    print('Done.')

if __name__ == '__main__':
    pd.options.mode.chained_assignment = None
    p = argparse.ArgumentParser(description='Filter csv data with given parameters')

    p.add_argument(
        '-f',
        '--filename',
        type=str,
        required=True,
        help='Full or relative path to the csv file. E.g. results/my_data.csv',
    )
    p.add_argument(
        '-o',
        '--output-filename',
        type=str,
        default='output.csv',
        help='Full or relative path to the output/filtered csv file. Defualt: output.csv',
    )
    p.add_argument(
        '-c',
        '--col',
        type=str,
        nargs='+',
        help='Columns to keep. Separated with space or comma. If any are set, only those are saved. Applied after processing. Can be multiple. E.g. -c created_at text',
    )
    p.add_argument(
        '-tz',
        '--timezone',
        type=str,
        help='Timezone to convert time data to. If date col in input csv is not tz-aware, will assume UTC. e.g. Asia/Tokyo',
    )
    p.add_argument(
        '--date-col',
        type=str,
        default='created_at',
        help='Name of the column with the date to filter with. Required for date filtering/tz conversion. Default: created_at',
    )
    p.add_argument(
        '--text-col',
        type=str,
        default='text',
        help='Name of the column with the text to query. Required for query. Default: text',
    )
    p.add_argument(
        '-q',
        '--query',
        type=str,
        help='Query specified text column with given substrings. Can use boolean operators AND/OR and NOT. NO NESTED RULES/PARANTHESES. Wrap strings in single quotes if separated by space. E.g. -q "keyword1 AND keyword2 AND NOT keyword3"',
    )
    p.add_argument(
        '--from-date',
        type=str,
        help='Format: YYYY-MM-DD',
    )
    p.add_argument(
        '--to-date',
        type=str,
        help='Format: YYYY-MM-DD',
    )
    args = vars(p.parse_args())
    filter_data(args)
