import csv
import datetime
import os
import sqlite3
from database_interaction import make_connection, create_cursor, get_categoryid, get_questions_with_image_for_category
from logger_setup import create_logger

logger = create_logger(__name__)
date_now = datetime.datetime.now()

CATEGORY = 'kunst-cultuur'
EXPORT_FOLDER = f'./anki-export/{CATEGORY}/'
EXPORT_FILE = f'./{EXPORT_FOLDER}/({date_now:%Y-%m-%d}) {CATEGORY}.csv'

connection = make_connection('quizarchief.sqlite')
logger.info(f'Connection made @{connection}')
cursor = create_cursor(connection)
logger.info(f'Cursor created as {cursor}')


category_id = get_categoryid(CATEGORY, cursor)[0]
logger.info(f'Your category "{CATEGORY} has a category_id of {category_id}')

questions_with_image_for_category = get_questions_with_image_for_category(category_id, cursor)
logger.info(f'The query get_questions_with_image_for_category({category_id}, cursor) returned {len(questions_with_image_for_category)} rows.')
# logger.info(f'Here are the first 5 first rows of your query: \n {questions_with_image_for_category[:5]}')

image_directory = f'./{CATEGORY}/'

os.makedirs(EXPORT_FOLDER, exist_ok=True)

with open(EXPORT_FILE, 'a', newline='', encoding='utf-8') as csv_file:
	fieldnames = ['question', 'answer']
	writer = csv.DictWriter(csv_file, delimiter='|', fieldnames=fieldnames, quotechar="'")

	"""
	questions_with_image_for_category lay-out:
	(question_id, question_number, question_text, answer_text, category_id, img_id, img_filename, question_)

	CREATE TABLE question (
		question_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		question_number INTEGER,
		question_text TEXT,
		answer_text TEXT,

		category_id INTEGER,
		FOREIGN KEY (category_id) REFERENCES category(category_id)
	);

	CREATE TABLE image (
		img_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		img_filename TEXT,

		question_id INTEGER,
		FOREIGN KEY (question_id) REFERENCES question(question_id)
	);

	cursor.execute('''
		SELECT *
		FROM question q LEFT JOIN image i ON q.question_id = i.question_id
		WHERE q.category_id = ?
	''', (category_id,))
	"""

	for row in questions_with_image_for_category:

		question = row[2].decode('utf-8')

		question_html = f'<p>{question}</p>'

		imagefile = row[6]

		if imagefile:
			image_basename = imagefile
			imagefile = os.path.join(image_directory, image_basename)
			image_html = f'<img src=\"{imagefile}\" />'
		else:
			image_html = ''

		question_card = f'{question_html}{image_html}'

		answer = row[3]

		writer.writerow({'question': question_card, 'answer': answer})

connection.commit()
connection.close()