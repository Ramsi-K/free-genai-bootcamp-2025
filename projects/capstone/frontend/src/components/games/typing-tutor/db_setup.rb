require 'sqlite3'
require 'json'
require 'fileutils'

# Stateless class for setting up the database and inserting data
class DatabaseSetup
  # Creates the SQLite database and required tables if they don't exist
  #
  # @param db_file [String] Path to the SQLite database file
  def self.create_database(db_file)
    begin
      db = SQLite3::Database.new(db_file)
      db.results_as_hash = true
      enable_foreign_keys(db)
      create_tables(db)
      puts "Database '#{db_file}' created or already exists."
    rescue SQLite3::Exception => e
      puts "Database creation failed: #{e.message}"
      exit 1
    ensure
      db.close if db
    end
  end

  # Inserts data from a JSON file into the 'words' table
  #
  # @param db_file [String] Path to the SQLite database file
  # @param json_file [String] Path to the JSON file containing word data
  def self.insert_words(db_file, json_file)
    unless File.exist?(json_file)
      puts "JSON file '#{json_file}' not found."
      exit 1
    end

    begin
      json_data = JSON.parse(File.read(json_file))
    rescue JSON::ParserError => e
      puts "Failed to parse JSON file: #{e.message}"
      exit 1
    end

    unless json_data.is_a?(Array)
      puts "JSON data should be an array of word objects."
      exit 1
    end

    begin
      db = SQLite3::Database.new(db_file)
      db.results_as_hash = true
      enable_foreign_keys(db)

      insert_words_into_db(db, json_data)
    rescue SQLite3::Exception => e
      puts "Database operation failed: #{e.message}"
      exit 1
    ensure
      db.close if db
    end
  end

  private

  # Enables foreign key constraints in SQLite
  #
  # @param db [SQLite3::Database] The database connection
  def self.enable_foreign_keys(db)
    db.execute("PRAGMA foreign_keys = ON;")
  rescue SQLite3::Exception => e
    puts "Failed to enable foreign keys: #{e.message}"
    exit 1
  end

  # Creates the 'words' and 'word_reviews' tables if they don't exist
  #
  # @param db [SQLite3::Database] The database connection
  def self.create_tables(db)
    create_words_table_sql = <<-SQL
      CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kanji TEXT NOT NULL,
        romaji TEXT NOT NULL,
        english TEXT NOT NULL,
        parts TEXT -- Stored as JSON string
      );
    SQL

    create_word_reviews_table_sql = <<-SQL
      CREATE TABLE IF NOT EXISTS word_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER NOT NULL,
        review_date TEXT,
        review_score INTEGER,
        FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
      );
    SQL

    db.execute(create_words_table_sql)
    db.execute(create_word_reviews_table_sql)
  rescue SQLite3::Exception => e
    puts "Failed to create tables: #{e.message}"
    exit 1
  end

  # Inserts words into the 'words' table from parsed JSON data
  #
  # @param db [SQLite3::Database] The database connection
  # @param json_data [Array<Hash>] Array of word objects
  def self.insert_words_into_db(db, json_data)
    insert_word_sql = <<-SQL
      INSERT INTO words (kanji, romaji, english, parts)
      VALUES (?, ?, ?, ?);
    SQL

    db.transaction
    stmt = db.prepare(insert_word_sql)

    json_data.each_with_index do |word, index|
      # Validate required fields
      unless word.key?('kanji') && word.key?('romaji') && word.key?('english') && word.key?('parts')
        puts "Skipping entry at index #{index}: Missing required fields."
        next
      end

      kanji = word['kanji']
      romaji = word['romaji']
      english = word['english']
      parts = word['parts'].to_json # Convert parts hash to JSON string

      begin
        stmt.execute(kanji, romaji, english, parts)
        puts "Inserted word: #{kanji} (#{romaji}) - #{english}"
      rescue SQLite3::Exception => e
        puts "Failed to insert word at index #{index}: #{e.message}"
        next
      end
    end

    stmt.close
    db.commit
  rescue SQLite3::Exception => e
    puts "Failed to insert data: #{e.message}"
    db.rollback
    exit 1
  end
end

# Example Usage
if __FILE__ == $0
  DB_FILE = 'words.db'
  JSON_FILE = 'words.json'

  # Create the database and tables
  DatabaseSetup.create_database(DB_FILE)

  # Insert words from JSON into the database
  DatabaseSetup.insert_words(DB_FILE, JSON_FILE)

  puts "Database setup and data insertion complete."
end