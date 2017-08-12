import os
import sqlite3

connection = sqlite3.connect('quizarchief_v003.sqlite')
cursor = connection.cursor()

cursor.execute('PRAGMA foreign_keys = ON')

cursor.execute('''
	CREATE TABLE category (
		category_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		category_name TEXT
	);
''')

cursor.execute('''
	CREATE TABLE quiz (
		quiz_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		quiz_name TEXT,
		quiz_year TEXT,
		quiz_url TEXT,
		quiz_organiser TEXT
	);
''')

cursor.execute('''
	CREATE TABLE question (
		question_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		question_number INTEGER,
		question_text TEXT,
		answer_text TEXT,

		category_id INTEGER,
		quiz_id INTEGER,
		FOREIGN KEY (category_id) REFERENCES category(category_id)
		FOREIGN KEY (quiz_id) REFERENCES quiz(quiz_id)
	);
''')

cursor.execute('''
	CREATE TABLE tag (
		tag_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		tag_name TEXT
	);
''')

cursor.execute('''
	CREATE TABLE question_tag (
		question_id INTEGER,
		tag_id INTEGER,
		FOREIGN KEY (question_id) REFERENCES question(question_id),
		FOREIGN KEY (tag_id) REFERENCES tag(tag_id)
		PRIMARY KEY (question_id, tag_id)
	);
''')

cursor.execute('''
	CREATE TABLE image (
		img_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		img_filename TEXT,

		question_id INTEGER,
		FOREIGN KEY (question_id) REFERENCES question(question_id)
	);
''')

cursor.execute('''
	CREATE TABLE youtube_fragment (
		fragment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		youtube_id TEXT,
		youtube_watch TEXT,

		question_id INTEGER,
		FOREIGN KEY (question_id) REFERENCES question(question_id)
	);
''')

connection.commit()
connection.close()