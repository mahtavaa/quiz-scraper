from database_interaction import make_connection, create_cursor, insert_question, get_tagid, insert_tag, insert_question_tag, insert_image, insert_category, get_categoryid
from scraper_utilities import createSession, login, construct_url, get_questionpage, make_soup, find_all_questionrows, find_question_number, find_question, find_tags, find_image, find_answer, sleep_randomly
from logger_setup import create_logger

logger = create_logger(__name__)

DATABASE_URL = 'quizarchief.sqlite'
CATEGORIE = 'kunst-cultuur'
FROM_PAGE = 1
TO_PAGE = 328
SLEEP_TIME = 20
CREDENTIALS = {
	'username': 'KolonelKappa',
	'password': 'g9f6a4zp'
}

connection = make_connection(DATABASE_URL)
cursor = create_cursor(connection)

session = createSession()
login(session, username=CREDENTIALS.get('username', None), password=CREDENTIALS.get('password', None))

for pagenr in range(FROM_PAGE, TO_PAGE):
	
	url = construct_url(CATEGORIE, pagenr)
	
	logger.info(f'Fetching results for page {pagenr}. \n')

	questionpage = get_questionpage(url, session)
	soup = make_soup(questionpage)
	questionrows = find_all_questionrows(soup)

	for i, questionrow in enumerate(questionrows):

		category_name = CATEGORIE
		category_id = get_categoryid(category_name, cursor)

		if not category_id:
			category_id = insert_category(category_name, cursor)

		else:
			category_id = category_id[0]

		
		question_number = find_question_number(questionrow)
		question_text = find_question(questionrow, question_number)
		answer_text = find_answer(questionrow, question_number, session)

		question_id = insert_question(question_number, question_text, answer_text, category_id, cursor)

		img_filename = find_image(questionrow, question_number, category_name, session)

		if img_filename:
			img_id = insert_image(img_filename, question_id, cursor)
		

		tag_names = find_tags(questionrow, question_number)
		
		tag_id = ''
		
		if len(tag_names) > 0:

			for tag_name in tag_names:

				tag_id = get_tagid(tag_name, cursor)

				if not tag_id:
					tag_id = insert_tag(tag_name, cursor)

				else:
					tag_id = tag_id[0]
			
				insert_question_tag(question_id, tag_id, cursor)

		connection.commit()
		logger.info(f'All information for question_number {question_number} was written to the database. \n')

		sleep_randomly(SLEEP_TIME)

connection.close()