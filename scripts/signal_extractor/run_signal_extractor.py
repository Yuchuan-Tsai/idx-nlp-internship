"""Run Week 6 signal extraction on full `rets_property` table."""

import json
import os
from itertools import chain

import mysql.connector
import pandas as pd

from scripts.data_extractor.entity_extractor import EntityExtractor
from scripts.data_loading.meaningful_taxonomy_json_builder import taxonomy_data
from scripts.signal_extractor.signal_extractor import SignalExtractor

def fetch_all_listings():
    conn = mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='root',
        database='real_estate'
    )

    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(
            """
            SELECT L_ListingID, L_Remarks
            FROM rets_property
            WHERE L_Remarks IS NOT NULL
              AND LENGTH(TRIM(L_Remarks)) > 0
            """
        )
        for row in cursor:
            yield row
    finally:
        cursor.close()
        conn.close()


def fetch_from_local_csv(csv_path='data/processed/listing_sample.csv'):
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        remarks = row.get('remarks')
        if isinstance(remarks, str) and remarks.strip():
            yield {
                'L_ListingID': row.get('L_ListingID'),
                'L_Remarks': remarks
            }


def run(output_path='data/processed/signal_extraction_full.json'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    extractor = EntityExtractor()
    signal_extractor = SignalExtractor(taxonomy_data, extractor)

    count = 0
    skipped = 0
    data_source = 'mysql.rets_property'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('[\n')
        first = True

        try:
            records = fetch_all_listings()
            first_record = next(records, None)
            if first_record is None:
                raise RuntimeError('No rows found in rets_property')
            records = chain([first_record], records)
        except Exception:
            data_source = 'data/processed/listing_sample.csv'
            records = fetch_from_local_csv()

        for record in records:
            try:
                result = signal_extractor.extract_signals(record)
            except Exception:
                skipped += 1
                continue
            if not first:
                f.write(',\n')
            f.write(json.dumps(result, ensure_ascii=False))
            first = False
            count += 1

        f.write('\n]\n')

    print(f'Processed {count} records')
    print(f'Skipped: {skipped} records')
    print(f'Source: {data_source}')
    print(f'Saved: {output_path}')


def main():
    run()


if __name__ == '__main__':
    main()
