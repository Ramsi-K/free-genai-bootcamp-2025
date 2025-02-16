import sqlite3
import json
from flask import g

class Db:
    def __init__(self, database='words.db'):
        self.database = database
        self.connection = None

    def get(self):
        if 'db' not in g:
            g.db = sqlite3.connect(self.database)
            g.db.row_factory = sqlite3.Row  # Return rows as dictionaries
        return g.db

    def commit(self):
        self.get().commit()

    def cursor(self):
        connection = self.get()
        return connection.cursor()

    def close(self):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def sql(self, filepath):
        with open('sql/' + filepath, 'r') as file:
            return file.read()

    def load_json(self, filepath):
        with open(filepath, 'r') as file:
            return json.load(file)

    def setup_tables(self, cursor):
        tables = [
            'setup/create_table_words.sql',
            'setup/create_table_word_reviews.sql',
            'setup/create_table_word_review_items.sql',
            'setup/create_table_groups.sql',
            'setup/create_table_word_groups.sql',
            'setup/create_table_study_activities.sql',
            'setup/create_table_study_sessions.sql'
        ]
        for table in tables:
            cursor.execute(self.sql(table))
            self.get().commit()

    def import_study_activities_json(self, cursor, data_json_path):
        study_activities = self.load_json(data_json_path)
        for activity in study_activities:
            cursor.execute('''
                INSERT INTO study_activities (name, url, preview_url) 
                VALUES (?, ?, ?)
            ''', (activity['name'], activity['url'], activity['preview_url']))
        self.get().commit()

    def import_word_json(self, cursor, group_name, data_json_path):
        # ✅ Ensure the group exists before inserting words
        cursor.execute('INSERT OR IGNORE INTO groups (name) VALUES (?)', (group_name,))
        self.get().commit()

        cursor.execute('SELECT id FROM groups WHERE name = ?', (group_name,))
        core_words_group_id = cursor.fetchone()
        if core_words_group_id:
            core_words_group_id = core_words_group_id[0]  # ✅ Prevents `NoneType` error
        else:
            raise Exception(f"Error: Group '{group_name}' was not created properly.")

        words = self.load_json(data_json_path)
        for word in words:
            # ✅ Extract `example["korean"]` and `example["english"]` safely
            example_korean = word.get('example', {}).get('korean', '')
            example_english = word.get('example', {}).get('english', '')

            cursor.execute('''
                INSERT INTO words (hangul, romanization, english, type, parts, example_korean, example_english)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                word['hangul'], 
                word['romanization'], 
                ', '.join(word['english']),  # ✅ Converts list to string
                word['type'],  # ✅ Properly stores noun, verb, etc.
                json.dumps(word['parts']), 
                example_korean,  # ✅ Properly extracts from JSON
                example_english
            ))

            word_id = cursor.lastrowid  # ✅ Get the last inserted word's ID

            cursor.execute('INSERT INTO word_groups (word_id, group_id) VALUES (?, ?)', (word_id, core_words_group_id))
        self.get().commit()  # ✅ Ensures words & relationships are saved

        cursor.execute('''
            UPDATE groups
            SET words_count = (SELECT COUNT(*) FROM word_groups WHERE group_id = ?)
            WHERE id = ?
        ''', (core_words_group_id, core_words_group_id))
        self.get().commit()  # ✅ Updates word count after inserting words

        print(f"Successfully added {len(words)} words to the '{group_name}' group.")

    def init(self, app):
        with app.app_context():
            cursor = self.cursor()
            self.setup_tables(cursor)
 
            # ✅ Now properly imports Korean words (Handles `example["korean"]` and `example["english"]`)
            self.import_word_json(cursor, 'Core Korean', 'seed/data_korean.json')

            self.import_study_activities_json(cursor, 'seed/study_activities.json')

# Create an instance of the Db class
db = Db()
