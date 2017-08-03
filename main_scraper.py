from database_interaction import make_connection, create_cursor, insert_question, get_tagid, insert_tag, insert_question_tag, insert_image, insert_category, get_categoryid, get_questionid
from scraper_utilities import createSession, login, construct_url, get_questionpage, make_soup, find_all_questionrows, find_question_number, find_question, find_tags, find_image, find_answer, sleep_randomly
from logger_setup import create_logger
import settings

logger = create_logger(__name__)

DATABASE_URL = settings.DATABASE_URL
CATEGORY = settings.CATEGORY
FROM_PAGE = settings.FROM_PAGE
TO_PAGE = settings.TO_PAGE
SLEEP_TIME = settings.SLEEP_TIME
CREDENTIALS = settings.CREDENTIALS

connection = make_connection(DATABASE_URL)
cursor = create_cursor(connection)

session = createSession()
login(session, username=CREDENTIALS.get('username', None), password=CREDENTIALS.get('password', None))

for pagenr in range(FROM_PAGE, TO_PAGE):
	
	url = construct_url(CATEGORY, pagenr)
	
	logger.info(f'Fetching results for page {pagenr}. \n')

	questionpage = get_questionpage(url, session)
	soup = make_soup(questionpage)
	questionrows = find_all_questionrows(soup)

	for i, questionrow in enumerate(questionrows):
		
		question_number = find_question_number(questionrow)

		is_already_in_database = get_questionid(question_number, cursor)
		
		if is_already_in_database:
			logger.info(f'Question {question_number} is already in database.')
			
			if settings.ONLY_NEW == True:
				logger.info(f'You set settings.ONLY_NEW to True, so downloading will stop.')
				
				# For details about ONLY_NEW, see settings.py
				break

			# Take a sleeptime of 0 or 1 seconds between the parsing of each question
			# by doing so, it will take 10 seconds on average for 1 page which is still reasonable
			# otherwise: in scenario you already downloaded the first 100 pages, but need page 101
			# the 100 pages would be asked without a pause (or only with pause = time to retrieve question_id * 20)
			sleep_randomly(1, 0)
			continue

		category_name = CATEGORY
		category_id = get_categoryid(category_name, cursor)

		if not category_id:
			category_id = insert_category(category_name, cursor)

		else:
			category_id = category_id[0]

		
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

	# for the following trick, check Markus Janderot's answer on StackOverflow
	# https://stackoverflow.com/questions/653509/breaking-out-of-nested-loops
	#
	# basically, if the question_number is already in the database && settings.ONLY_NEW = True
	# we want to stop all operations of the scraper
	# if settings.ONLY_NEW = False, the loop continues digging for more questions
	else:
		continue # executed when inner-for-loop executes without breaking

	break # if else-clause is not triggered, i.e. in case of breaking out of innerloop

connection.close()