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
    # Ensure the connection is valid before getting a cursor
    connection = self.get()
    return connection.cursor()

  def close(self):
    db = g.pop('db', None)
    if db is not None:
      db.close()

  # Function to load SQL from a file
  def sql(self, filepath):
    with open('sql/' + filepath, 'r') as file:
      return file.read()

  # Function to load the words from a JSON file
  def load_json(self, filepath):
    with open(filepath, 'r') as file:
      return json.load(file)

  def setup_tables(self,cursor):
    # Create the necessary tables
    cursor.execute(self.sql('setup/create_table_words.sql'))
    self.get().commit()

    cursor.execute(self.sql('setup/create_table_word_reviews.sql'))
    self.get().commit()

    cursor.execute(self.sql('setup/create_table_word_review_items.sql'))
    self.get().commit()

    cursor.execute(self.sql('setup/create_table_groups.sql'))
    self.get().commit()

    cursor.execute(self.sql('setup/create_table_word_groups.sql'))
    self.get().commit()

    cursor.execute(self.sql('setup/create_table_study_activities.sql'))
    self.get().commit()

    cursor.execute(self.sql('setup/create_table_study_sessions.sql'))
    self.get().commit()

  def import_study_activities_json(self,cursor,data_json_path):
    study_actvities = self.load_json(data_json_path)
    for activity in study_actvities:
      cursor.execute('''
      INSERT INTO study_activities (name,url,preview_url) VALUES (?,?,?)
      ''', (activity['name'],activity['url'],activity['preview_url'],))
    self.get().commit()

  def import_word_json(self,cursor,group_name,data_json_path):
      # Insert a new group
      cursor.execute('''
        INSERT INTO groups (name) VALUES (?)
      ''', (group_name,))
      self.get().commit()

      # Get the ID of the group
      cursor.execute('SELECT id FROM groups WHERE name = ?', (group_name,))
      core_verbs_group_id = cursor.fetchone()[0]

      # Insert some sample words (verbs) from JSON file and associate with the group
      words = self.load_json(data_json_path)

      for word in words:
        # Insert the word into the words table
        cursor.execute('''
          INSERT INTO words (kanji, romaji, english, parts) VALUES (?, ?, ?, ?)
        ''', (word['kanji'], word['romaji'], word['english'], json.dumps(word['parts'])))
        
        # Get the last inserted word's ID
        word_id = cursor.lastrowid

        # Insert the word-group relationship into word_groups table
        cursor.execute('''
          INSERT INTO word_groups (word_id, group_id) VALUES (?, ?)
        ''', (word_id, core_verbs_group_id))
      self.get().commit()

      # Update the words_count in the groups table by counting all words in the group
      cursor.execute('''
        UPDATE groups
        SET words_count = (
          SELECT COUNT(*) FROM word_groups WHERE group_id = ?
        )
        WHERE id = ?
      ''', (core_verbs_group_id, core_verbs_group_id))

      self.get().commit()

      print(f"Successfully added {len(words)} verbs to the '{group_name}' group.")

  # Initialize the database with sample data
  def init(self, app):
    with app.app_context():
      cursor = self.cursor()
      self.setup_tables(cursor)
      self.import_word_json(
        cursor=cursor,
        group_name='Core Verbs',
        data_json_path='seed/data_verbs.json'
      )
      self.import_word_json(
        cursor=cursor,
        group_name='Core Adjectives',
        data_json_path='seed/data_adjectives.json'
      )

      self.import_study_activities_json(
        cursor=cursor,
        data_json_path='seed/study_activities.json'
      )

# Create an instance of the Db class
db = Db()
