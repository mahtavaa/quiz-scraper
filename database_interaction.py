import sqlite3

def make_connection(database_url):

	connection = sqlite3.connect(database_url)
	return connection

def create_cursor(connection):

	cursor = connection.cursor()
	return cursor

def insert_question(question_number, question_text, answer_text, category_id, quiz_id, cursor):

	cursor.execute('''
		INSERT INTO question (question_number, question_text, answer_text, category_id, quiz_id)
		VALUES (?, ?, ?, ?, ?)
	''', (question_number, question_text, answer_text, category_id, quiz_id,))

	lastrowid = cursor.lastrowid
	return lastrowid

def insert_quiz(quiz_name, quiz_year, quiz_url, quiz_organiser, cursor):

	cursor.execute('''
		INSERT INTO quiz (quiz_name, quiz_year, quiz_url, quiz_organiser)
		VALUES (?, ?, ?, ?)
	''', (quiz_name, quiz_year, quiz_url, quiz_organiser))

	lastrowid = cursor.lastrowid
	return lastrowid

def get_tag_id(tag_name, cursor):

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

def get_category_id(category_name, cursor):

	cursor.execute('''
		SELECT category_id
		FROM category
		WHERE category_name = ?
	''', (category_name,))

	category_id = cursor.fetchone()
	return category_id

def get_question_id(question_number, cursor):

	cursor.execute('''
		SELECT question_id
		FROM question
		WHERE question_number = ?
	''', (question_number,))

	question_id = cursor.fetchone()
	return question_id

def get_questions_with_image_for_category(category_id, cursor):

	cursor.execute('''
		SELECT *
		FROM question q LEFT JOIN image i ON q.question_id = i.question_id
		WHERE q.category_id = ?
	''', (category_id,))

	questions_with_image = cursor.fetchall()
	return questions_with_image


def get_question_with_question_id(question_id, cursor):

	cursor.execute('''
		SELECT *
		FROM question q
		WHERE question_id = ?
	''', (question_id,))

	question = cursor.fetchone()
	return question


def get_question_with_question_number(question_number, cursor):

	cursor.execute('''
		SELECT *
		FROM question
		WHERE question_number = ?
	''', (question_number,))

	question = cursor.fetchall()
	return question


def get_quiz_id_with_quiz_url(quiz_url, cursor):

	cursor.execute('''
		SELECT quiz_id
		FROM quiz
		WHERE quiz_url = ?
	''', (quiz_url,))

	quiz_id = cursor.fetchone()
	return quiz_id


def get_category_name_for_question_number(question_number, cursor):

	cursor.execute('''
		SELECT category_name
		FROM category
		WHERE category_id = (
			SELECT category_id
			FROM question
			WHERE question_number = ?
		)
	''', (question_number,))

	question_number = cursor.fetchone()
	return question_number


def insert_youtube_fragment(youtube_id, youtube_watch, question_id, cursor):

	cursor.execute('''
		INSERT INTO youtube_fragment (youtube_id, youtube_watch, question_id)
		VALUES (?, ?, ?)
	''', (youtube_id, youtube_watch, question_id))

	lastrowid = cursor.lastrowid
	return lastrowid


def get_questions_with_image_and_youtube_fragment_for_category(category_id, cursor):

	cursor.execute('''
		SELECT q.question_id, q.question_number, q.question_text, q.answer_text, q.category_id, q.quiz_id, i.img_id, i.img_filename, yf.youtube_id, yf.youtube_watch
		FROM question q 
		LEFT JOIN image i ON q.question_id = i.question_id
		LEFT JOIN youtube_fragment yf ON q.question_id = yf.question_id
		WHERE q.category_id = ?
	''', (category_id,))

	questions_with_image_and_youtube_fragment = cursor.fetchall()
	return questions_with_image_and_youtube_fragment


def get_tags_for_question_id(question_id, cursor):

	cursor.execute('''
		SELECT t.tag_name
		FROM tag t
		WHERE t.tag_id in (
			SELECT qt.tag_id
			FROM question_tag qt
			WHERE qt.question_id	in (
				SELECT q.question_id
				FROM question q
				WHERE q.question_id = ?
			)
		);
	''', (question_id,))

	tags = cursor.fetchall()
	return tags

def get_tags_for_question_number(question_number, cursor):

	cursor.execute('''
		SELECT t.tag_name
		FROM tag t
		WHERE t.tag_id in (
			SELECT qt.tag_id
			FROM question_tag qt
			WHERE qt.question_id	in (
				SELECT q.question_id
				FROM question q
				WHERE q.question_number = ?
			)
		);
	''', (question_number,))

	tags = cursor.fetchall()
	return tags