import sqlite3

def make_connection(database_url):

	connection = sqlite3.connect(database_url)
	return connection

def create_cursor(connection):

	cursor = connection.cursor()
	return cursor

def insert_question(question_number, question_text, answer_text, category_id, cursor):

	cursor.execute('''
		INSERT INTO question (question_number, question_text, answer_text, category_id)
		VALUES (?, ?, ?, ?)
	''', (question_number, question_text, answer_text, category_id,))

	lastrowid = cursor.lastrowid
	return lastrowid

def get_tagid(tag_name, cursor):

	cursor.execute('''
		SELECT tag_id
		FROM tag
		WHERE tag_name = ?
	''', (tag_name,))

	tag_id = cursor.fetchone()
	return tag_id

def insert_tag(tag_name, cursor):

	cursor.execute('''
		INSERT INTO tag (tag_name)
		VALUES (?)
	''', (tag_name,))

	lastrowid = cursor.lastrowid
	return lastrowid

def insert_question_tag(question_id, tag_id, cursor):

	cursor.execute('''
		INSERT INTO question_tag (question_id, tag_id)
		VALUES (?, ?)
	''', (question_id, tag_id,))

	lastrowid = cursor.lastrowid
	return lastrowid

def insert_image(img_filename, question_id, cursor):

	cursor.execute('''
		INSERT INTO image (img_filename, question_id)
		VALUES (?, ?)
	''', (img_filename, question_id,))

	lastrowid = cursor.lastrowid
	return lastrowid

def insert_category(category_name, cursor):

	cursor.execute('''
		INSERT INTO category (category_name)
		VALUES (?)
	''', (category_name,))

	lastrowid = cursor.lastrowid
	return lastrowid

def get_categoryid(category_name, cursor):

	cursor.execute('''
		SELECT category_id
		FROM category
		WHERE category_name = ?
	''', (category_name,))

	category_id = cursor.fetchone()
	return category_id