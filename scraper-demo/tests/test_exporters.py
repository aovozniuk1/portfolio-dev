import csv
import json
import sqlite3

import pytest

from exporters.csv_exporter import CsvExporter
from exporters.json_exporter import JsonExporter
from exporters.sqlite_exporter import SqliteExporter
from models.items import Quote


def _sample_quotes():
    return [
        Quote(text='Be yourself', author='Oscar Wilde', tags=['life']),
        Quote(text='Stay hungry', author='Steve Jobs', tags=['motivation', 'tech']),
        Quote(text='Why not?', author='Unknown', tags=[]),
    ]


class TestCsvExporter:
    def test_creates_valid_csv(self, tmp_path):
        out = str(tmp_path / 'quotes.csv')
        exporter = CsvExporter(out)
        exporter.export(_sample_quotes())

        with open(out, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        assert 'text' in rows[0]
        assert 'author' in rows[0]

    def test_empty_items_returns_path(self, tmp_path):
        out = str(tmp_path / 'empty.csv')
        result = CsvExporter(out).export([])
        assert result == out


class TestJsonExporter:
    def test_creates_valid_json(self, tmp_path):
        out = str(tmp_path / 'quotes.json')
        JsonExporter(out).export(_sample_quotes())

        with open(out, encoding='utf-8') as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]['author'] == 'Oscar Wilde'


class TestSqliteExporter:
    def test_inserts_correct_rows(self, tmp_path):
        db_path = str(tmp_path / 'test.db')
        SqliteExporter(db_path, table_name='quotes').export(_sample_quotes())

        conn = sqlite3.connect(db_path)
        cursor = conn.execute('SELECT COUNT(*) FROM quotes')
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 3

    def test_rejects_invalid_table_name(self):
        with pytest.raises(ValueError, match='Invalid table name'):
            SqliteExporter('dummy.db', table_name='DROP TABLE; --')
