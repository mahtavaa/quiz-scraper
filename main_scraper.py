import database_interaction as db_inter
import logger_setup
import scraper_utilities as scraper_util
import settings

logger = logger_setup.create_logger(__name__)

DATABASE_URL = settings.DATABASE_URL
CATEGORY = settings.CATEGORY
FROM_PAGE = settings.FROM_PAGE
TO_PAGE = settings.TO_PAGE
SLEEP_TIME = settings.SLEEP_TIME
CREDENTIALS = settings.CREDENTIALS

category_dict = scraper_util.create_category_dictionary()
if scraper_util.is_valid_category(CATEGORY, category_dict):

	pages_for_category = scraper_util.compute_pages_for_category(CATEGORY, category_dict)
	end_page = scraper_util.validate_end_page(TO_PAGE, pages_for_category)
	start_page = scraper_util.validate_start_page(FROM_PAGE, end_page)

	connection = db_inter.make_connection(DATABASE_URL)
	cursor = db_inter.create_cursor(connection)

	session = scraper_util.create_session()
	scraper_util.login(session, username=CREDENTIALS.get('username', None), password=CREDENTIALS.get('password', None))


	for pagenr in range(start_page, end_page):
		
		url = scraper_util.construct_url(CATEGORY, pagenr)
		
		logger.info(f'Fetching results for page {pagenr}. \n')

		questionpage = scraper_util.get_questionpage(url, session)
		soup = scraper_util.make_soup(questionpage)
		questionrows = scraper_util.find_all_questionrows(soup)

		for i, questionrow in enumerate(questionrows):
			
			question_number = scraper_util.find_question_number(questionrow)

			is_already_in_database = db_inter.get_question_id(question_number, cursor)
			
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
				scraper_util.sleep_randomly(1, 0)
				continue

			quiz_info_dictionary = scraper_util.find_quiz_info(questionrow, question_number)
			quiz_name = quiz_info_dictionary.get('quiz_name')
			quiz_year = quiz_info_dictionary.get('quiz_year')
			quiz_url = quiz_info_dictionary.get('quiz_url')
			quiz_organiser = quiz_info_dictionary.get('quiz_organiser')

			quiz_id = db_inter.get_quiz_id_with_quiz_url(quiz_url, cursor)

			if not quiz_id:
				quiz_id = db_inter.insert_quiz(quiz_name, quiz_year, quiz_url, quiz_organiser, cursor)

			else:
				quiz_id = quiz_id[0]

			category_name = CATEGORY
			category_id = db_inter.get_category_id(category_name, cursor)

			if not category_id:
				category_id = db_inter.insert_category(category_name, cursor)

			else:
				category_id = category_id[0]

			
			question_text = scraper_util.find_question(questionrow, question_number)
			answer_text = scraper_util.find_answer(question_number, session)

			# logger.info(f'question_id = db_inter.insert_question(question_number, question_text, answer_text, category_id, quiz_id, cursor)')
			# logger.info(f'param 0: question_number: \n {question_number}')
			# logger.info(f'param 1: question_text: \n {question_text}')
			# logger.info(f'param 2: answer_text: \n {answer_text}')
			# logger.info(f'param 3: category_id: \n {category_id}')
			# logger.info(f'param 4: quiz_id: \n {quiz_id}')
			# logger.info(f'param 5: cursor: \n {cursor}')

			question_id = db_inter.insert_question(question_number, question_text, answer_text, category_id, quiz_id, cursor)

			img_filename = scraper_util.find_image(questionrow, question_number, category_name, session)

			if img_filename:
				img_id = db_inter.insert_image(img_filename, question_id, cursor)
			

			youtube_id = scraper_util.find_youtube_fragment(questionrow, question_number, session)

			if youtube_id:
				youtube_watch = scraper_util.get_youtube_watch_url(youtube_id)
				fragment_id = db_inter.insert_youtube_fragment(youtube_id, youtube_watch, question_id, cursor)


			tag_names = scraper_util.find_tags(questionrow, question_number)
			
			tag_id = ''
			
			if len(tag_names) > 0:

				for tag_name in tag_names:

					tag_id = db_inter.get_tag_id(tag_name, cursor)

					if not tag_id:
						tag_id = db_inter.insert_tag(tag_name, cursor)

					else:
						tag_id = tag_id[0]
				
					db_inter.insert_question_tag(question_id, tag_id, cursor)

			connection.commit()
			logger.info(f'All information for question_number {question_number} was written to the database. \n')

			scraper_util.sleep_randomly(SLEEP_TIME)

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