import csv
import database_interaction as db_inter
import datetime
import logger_setup
import os
import re
import sqlite3

logger = logger_setup.create_logger(__name__)
date_now = datetime.datetime.now()

CATEGORY = 'muziek'
DATABASE_URL = 'quizarchief_v003.sqlite'
EXPORT_FOLDER = f'./anki-export/{CATEGORY}/'
EXPORT_FILE = f'./{EXPORT_FOLDER}/({date_now:%Y-%m-%d}) {CATEGORY}.csv'

connection = db_inter.make_connection(DATABASE_URL)
logger.info(f'Connection made @{connection}')
cursor = db_inter.create_cursor(connection)
logger.info(f'Cursor created as {cursor}')


category_id = db_inter.get_category_id(CATEGORY, cursor)[0]
logger.info(f'Your category "{CATEGORY} has a category_id of {category_id}')

questions_with_image_and_youtube_fragment = db_inter.get_questions_with_image_and_youtube_fragment_for_category(category_id, cursor)
logger.info(f'The query db_inter.get_questions_with_image_for_category({category_id}, cursor) returned {len(questions_with_image_and_youtube_fragment)} rows.')
logger.info(f'Here are the first 5 first rows of your query: \n {questions_with_image_and_youtube_fragment[:5]}')

image_directory = f'./{CATEGORY}/'

os.makedirs(EXPORT_FOLDER, exist_ok=True)

with open(EXPORT_FILE, 'a', newline='', encoding='utf-8') as csv_file:
	fieldnames = ['question', 'answer']
	writer = csv.DictWriter(csv_file, delimiter='|', fieldnames=fieldnames, quotechar="'")

	"""
	questions_with_image_and_youtube_fragment
	0: q.question_id
	1: q.question_number
	2: q.question_text
	3: q.answer_text
	4: q.category_id
	5: q.quiz_id
	6: i.img_id
	7: i.img_filename
	8: yf.youtube_id
	9: yf.youtube_watch
	"""

	for row in questions_with_image_and_youtube_fragment:

		question_number = row[1]
		question = row[2]

		# question_text used to be stored as an encoded value (bytes)
		# in newer version it is stored as str
		if type(question) == bytes:
			question = question.decode('utf-8')

		question_html = f'<p>{question}</p>'

		imagefile = row[7]
		if imagefile:
			image_basename = imagefile
			imagefile = os.path.join(image_directory, image_basename)
			image_html = f'<img src=\"{imagefile}\" />'
		else:
			image_html = ''


		youtube_html = ''

		# embedded youtube iframe is not supported on windows
		# see: https://www.reddit.com/r/Anki/comments/507bns/question_can_i_embed_youtube_videos_into_the_cards/

		# youtube_id = row[8]
		# if youtube_id:
		# 	youtube_id_html = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{youtube_id}" frameborder="0" allowfullscreen></iframe>'
		# else:
		# 	youtube_id_html = ''

		youtube_watch = row[9]
		if youtube_watch:
			youtube_watch_html = f'<p style="font-size: small; color: #3e3e40;"><a href=\"{youtube_watch}\">This question contains a youtube fragment, which you can watch by clicking on this link.</a></p>'

		# youtube_html = f'<div>{youtube_id_html}{youtube_watch_html}</div>'
		youtube_html = f'{youtube_watch_html}'

		question_card = f'{question_html}{image_html}{youtube_html}'

		answer = row[3]

		# answer_text used to be stored as an encoded value (bytes)
		# in newer version it is stored as str
		if type(answer)	== bytes:
			answer = answer.decode('utf-8')

		newline_pattern = re.compile('\n')
		html_br = '<br>'
		
		answer = re.sub(newline_pattern, html_br, answer)

		writer.writerow({'question': question_card, 'answer': answer})

connection.commit()
connection.close()