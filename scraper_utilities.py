from bs4 import BeautifulSoup
import logger_setup
import math
import os
import random
import re
import requests
import settings
import shutil
import sqlite3
import time

logger = logger_setup.create_logger(__name__)

def create_session():
	"""Return a requests' session object."""

	with requests.Session() as session:

		logger.debug('Session established')
		return session

def login(session, username, password):
	"""
	Return HTTP status code -> 200 if logged in correctly.

	Arguments:
	session -- a requests' session object
	username -- your username on quizarchief.be
	password -- your password on quizarchief.be

	"""

	credentials = {
		'name': username,
		'pass': password
	}

	login_response = session.post('https://www.quizarchief.be/login.php', data=credentials)

	login_status = login_response.status_code
	logger.debug(f'Your attempt to log in, resulted in HTTP status code: {login_status}')

	return login_status


def create_category_dictionary():
	"""
	Return a dicionary consisting of:
	    keys: category_identifier
	    values: number of pages for category_identifier
	"""
	url = 'https://www.quizarchief.be/categorie/'

	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html5lib', from_encoding='UTF-8')

	category_dict = {}


	category_overview = soup.find('div', {'class': 'col-lg-8'})
	all_categories = category_overview.find_all('div', {'style': 'padding:8px;float:left;width:250px;'})

	# category:
	# 
	# <div style="padding:8px;float:left;width:250px;">
	# 	<a href="categorie/architectuur-bouwkunde">
	# 		<big>Architectuur</big>
	# 	</a>
	# 	 (1447)
	# </div>

	for category in all_categories:

		category_name = category.find('a').find('big').text
		category_identifier = category.find('a').get('href')[10:]
		
		category_question_amount_dirty = category.contents[1]
		
		number_pattern = re.compile('(?P<question_amount>\d+)')
		category_question_amount = re.search(number_pattern, category_question_amount_dirty).group('question_amount')

		category_dict[category_identifier] = int(category_question_amount)

		logger.debug(f'#questions for {category_name} ({category_identifier}): {category_question_amount}')

	return category_dict


def is_valid_category(category, category_dict):
	""""Check whether provided category is indeed one of the possible categories."""
	is_valid = False

	if category in category_dict.keys():
		is_valid = True
		logger.debug('Provided category is indeed one of the possible categories.')

	return is_valid


def compute_pages_for_category(category, category_dict, questions_per_page=20):
	"""
	Return the maximum amount of pages that can be retrieved for a category
	say there are 250 questions for a category

	e.g. 
	category_dict = {'literatuur': 6806}
	'literatuur' has 6806 registered questions 
	if there are 20 questions per page -> 341  pages
	== ceiling(6806/20)
	"""
	
	number_of_questions_for_category = category_dict.get(category, 0)
	total_pages_for_category = math.ceil((number_of_questions_for_category/questions_per_page))
	logger.debug(f'For category {category}, there can be {total_pages_for_category} retrieved.')

	return total_pages_for_category


def validate_end_page(end_page, pages_for_category):
	"""
	Ensure that provided end_page does not exceed the possible range of pages that can be retrieved.
	If the provided number of pages to be scraped is larger than possible, set it equal to the maximum amount.
	"""

	if end_page == 'ALL':
		validated_end_page = pages_for_category

	else:
		validated_end_page = min(end_page, pages_for_category)

	return validated_end_page


def validate_start_page(start_page, end_page):
	"""Return end_page if start_page is higher than the end_page."""

	if start_page > end_page:
		return end_page

	return start_page


def construct_url(categorie, page):
	"""
	Return constructed url.

	Arguments:
	categorie -- a thematic category, for a list of all available options, see below
	page -- pagenumber

	The url is composed of multiple parts:
	https://www.quizarchief.be/categorie/cat/pn/aoqpp/so/pt

	protocol: https://
	subdomain: www
	domain name: quizarchief.be
	path: categorie

	query and parameters:

	cat -- category
	    aardrijkskunde
		architectuur-bouwkunde
		binnenland
		biologie-fauna
		biologie-flora
		economie-business
		gastronomie-keuken-eten-drinken
		film
		filosofie
		foto
		games-ontspanning
		geloof-religie-godsdienst
		geneeskunde-menselijk-lichaam
		geschiedenis
		informatica-internet
		kunst-cultuur
		literatuur
		media-showbizz
		mode-lifestyle
		muziek
		mythologie
		politiek-binnenland
		politiek-buitenland
		puzzels-raadsels-breinbrekers
		sport
		strips
		taal
		televisie
		varia
		wetenschap-techniek

	pn -- pagenumber
	
	aoqpp -- amount of questions per page:
	    1: 1 vraag
	    3: 3 vragen
	    5: 5 vragen
	    10: 10 vragen
	    15: 15 vragen
	    20: 20 vragen

	    (note that choosing a value that is not in this predefined list, will NOT work)

	so -- sorting order
	    1: van nieuw naar oud
	    2: van oud naar nieuw
	    3: makkelijkste eerst
	    4: moeilijkste eerst
	    5: heel makkelijk
	    6: makkelijk
	    7: eerder makkelijk
	    8: eerder moeilijk
	    9: moeilijk
	    10: heel moeilijk
	    11: meeste likes
	
	pt -- page template
		0: base html page where questions are set upon


	e.g. https://www.quizarchief.be/categorie/film/807/10/1/0
	retrieves pagenumber 807 for category film, with 10 questions per page, sorted on descending datetime

	"""

	url = f'https://www.quizarchief.be/categorie/{categorie}/{page}/20/1/0'
	logger.debug(f'url constructed as: \n {url}')
	
	return url

def get_questionpage(url, session):
	"""
	Return questionpage.

	Arguments:
	url -- a constructed quizarchief url
	session -- a request's session object
	"""

	questionpage = session.get(url)
	questionpage.encoding = 'utf-8'

	logger.debug(f'Questionpage was fetched with status code: {questionpage.status_code}')
	
	return questionpage

def make_soup(questionpage):
	"""Return constructed BeautifulSoup object, from provided questionpage"""

	soup = BeautifulSoup(questionpage.content, 'html5lib')

	#delete all <br/> elements, otherwise this will confuse question parser
	for br in soup.find_all('br'):
		br.extract()

	logger.debug('Soup is very hot, bon appetit! :)')
	
	return soup

def find_all_questionrows(soup):
	"""
	Return questionrows.

	Arguments:
	soup -- a BeautifulSoup object

	Every question is embedded in a questionrow, which is a div-element, with an id that is composed out of two parts:
	vragenrij_ + question_number

	A questionrow contains other information besides: question_text, answer_text, image and tags.
	e.g. information about the name/date/... of the quiz the question belongs to
	"""

	vragenrij_regex = re.compile('vragenrij_\d+')
	questionrows = soup.find_all('div', {'id': vragenrij_regex})

	logger.debug(f'There are {len(questionrows)} questionrows found on the given page.')
	return questionrows

def find_question_number(questionrow):
	"""
	Extract question_number for a given questionrow.
	
	A questionrow is a div with an id, composed out of two parts:
	vragenrij_ + question_number

	e.g. vragenrij_82096
	We want to extract the question_number, here: 82096.
	"""

	dirty_question_number = questionrow.get('id')
	clean_question_number = re.search('(?:vragenrij_)(\d+)', dirty_question_number).group(1)

	question_number = clean_question_number
	logger.debug(f'The question_number that was extracted for the questionrow is: {question_number}.')

	return question_number

def find_question(questionrow, question_number):
	"""
	Return question_text.
	Return '' (empty string) if no question_text could be extracted.

	If there are tags available, the html structure is as follows:

	<div id="vragenrij_81790">
		<div class="vragenrij">
			<span>
				<a href="tags/cycling">cycling</a>
				<a href="tags/sporty">sporty</a>
			</span>
			We zijn op zoek naar een de beste wielrenner ter wereld...
		</div>
	</div>

	However, sometimes no tags are provided.

	The question_text itself is not wrapped in any html tag, which is why we will rely on BeautifulSoup.contents[]
	this is more prone to changes in the mark-up & thus should be changed to a tag-finder instead, 
	in case the website would provide a tag-wrapper in the future.
	"""
	question_text = ''

	try:
		question_div = questionrow.find('div', {'class': 'vragenrij'})
		
		#sometimes no tags are provided, then the question_text moves up in the html structure
		#first check if there are tags
		tag_regex = re.compile('tag_\d+')
		
		if len(questionrow.find_all('a', {'id': tag_regex})) > 0:
			#if there are tags available, apply contents[1]
			question_text = question_div.contents[1].strip()
		else:
			#if there is no tag, it is directly under the div, so contents[0]
			question_text = question_div.contents[0].strip()

		logger.info(f'The question_text for question nr. {question_number}: \n {question_text}')

	except Exception as e:
		logger.error(f'An unexpected exception occured while parsing question with id: {question_number}, with exception message: \n {e}')
		
	finally:
		return question_text

def find_tags(questionrow, question_number):
	"""
	Return tags as a list.
	Return [] (empty list) if none are provided.

	If there are tags available, they are positioned as follows:

	<div id="vragenrij_81790">
		<div class="vragenrij">
			<span>
				<a href="tags/cycling">cycling</a>
				<a href="tags/sporty">sporty</a>
			</span>
			We zijn op zoek naar een de beste wielrenner ter wereld...
		</div>
	</div>

	Here, find_tags will return ['cycling', 'sporty']
	"""

	tags = []

	try:
		tag_regex = re.compile('tag_\d+')

		taglinks = questionrow.find_all('a', {'id': tag_regex})
		tags = [tag.text for tag in taglinks]

		logger.info(f'Tags for question_number {question_number}: {tags}')


	except Exception as e:
		logger.error(f'An exception occured while parsing tags for question_number: {question_number}, with exception message: \n {e}')

	finally:
		return tags

def find_image(questionrow, question_number, categorie, session):
	"""
	if image: Return image_filename
	+ Download the image to a folder relatively located at ./{categorie}/

	if no image: Return None

	if there is an image accompanying the question, this function will return the image_filename
	the image_filename is the combination of the question_number with an extension
	this extension can take multiple formats (jpg, jpeg, png, ...) & should be saved accordingly

	"""

	class ImageNotFound(Exception):
		"""Exception which handles the lack of an image in a questionrow."""

	class YoutubeInsteadOfImage(Exception):
		"""This exception should be raised when the embedded visual is a youtube video and NOT an image."""

	try:
		question_image_centerdiv = questionrow.find('center')

		if not question_image_centerdiv:
			raise ImageNotFound

		question_img = question_image_centerdiv.find('img')

		if not question_img:
			raise YoutubeInsteadOfImage

	except ImageNotFound:
		logger.info(f'Question_number: {question_number}. No image was found for this questionrow.')
		return None

	except YoutubeInsteadOfImage:
		logger.info(f'Question_number: {question_number}. The embedded visual is a youtube link, not an image.')
		return None

	except Exception as e:
		logger.error(f'Question_number: {question_number}. An unexpected exception occurred while parsing the embedded visual with the following exception message: \n {e}.')
		return None

	"""
	images have a src-attribute with a certain naming pattern from which we want to extract information
	
	e.g. src="prodgfx/vragen/q/972d66f98fa6ccb0573b07d549ac3b76_131365.jpg"
	
	image absolute source: https://www.quizarchief.be/prodgfx/vragen/q/972d66f98fa6ccb0573b07d549ac3b76_131365.jpg
	image belonging to question_number: 131365
	image extension: jpg
	"""

	#construct the absolute image source
	base_url = 'https://www.quizarchief.be/'
	image_relative_url = question_img.get('src')

	image_url = os.path.join(base_url, image_relative_url)
	logger.debug(f'image_url constructed: {image_url}')

	#set up connection to the image source
	image = session.get(image_url, stream=True)

	#construct filename

	#first get basename e.g. 972d66f98fa6ccb0573b07d549ac3b76_131365.jpg
	dirty_filename = os.path.basename(image_url)

	#there are multiple extensions at use for images on the site, so we cannot use a default, extract it
	filename, extension = os.path.splitext(dirty_filename)

	filename_regex = re.compile('(?:[\w\d]+_)?(\d+)')
	question_number = re.search(filename_regex, filename).group(1)
	
	image_filename = question_number + extension
	logger.debug(f'image_filename composed: {image_filename}')

	#make a folder to which the image will be downloaded
	directory = f'./{categorie}/'
	filepath = ''.join((directory, image_filename))

	os.makedirs(directory, exist_ok=True)

	#download the image to the folder
	with open(filepath, 'wb') as imagefile:
		shutil.copyfileobj(image.raw, imagefile)
		logger.debug(f'{image_filename} downloaded to {filepath}')
	del image

	return image_filename

def find_answer(question_number, session):
	"""
	Return answer_text.
	Return '' (empty string) if no answer_text could be extracted

	To get the answer for a given question, quizarchief performs an xhr-request to the following url:
	https://www.quizarchief.be/beantwoordevragen.php?vraagid={question_number}&page=categorie
	"""

	answer_text = ''

	try:
		answer_url = f'https://www.quizarchief.be/beantwoordevragen.php?vraagid={question_number}&page=categorie'
		answer_page = session.get(answer_url)
		answer_page.encoding = 'utf-8'

		soup = BeautifulSoup(answer_page.content, 'html5lib', from_encoding='UTF-8')

		answer_text = soup.find('b').text.strip()

		logger.info(f'Answer found for question_number {question_number}: \n {answer_text}')

	except Exception as e:
		logger.error(f'An exception occured while parsing answer for question with id: {question_number}, with exception message: \n {e}')
		
	finally:
		return answer_text


def find_quiz_info(questionrow, question_number):
	"""
	Return Quiz Information Dictionary
	{
		'quiz_name': '<quizname>',
		'quiz_year': '<year>',
		'quiz_url': '<quiz url>',
		'quiz_roundinfo': '<round, questionnumber (in round)>',
		'quiz_organiser': '<quiz organiser/designer>'
	}

	Each questionrow -even for non-organized quizzes, like photoquizzes-
	includes some information about the quiz:
		- quizname
		- year
		- round, questionnumber (in round)
		- organiser/designer

	e.g.

	<div id="toonbron_132242">
		<div>
			<span>
				"Uit: "
				<a href="quiz/fothemaquiz-34-2016">
					<strong>FothemaQuiz 34</strong>
					" (2016)"
				</a>
				", "
				<a href="quiz/fothemaquiz-34-2016/1">
					<strong>ronde 1, vraag 11</strong>
				</a>
				", door "
				<a href="quizteam/pepeq">
					<strong>PépéQ</strong>
				</a>
			</span>
		</div>
	</div>

		-> question_number = 132242
		-> quizname = FothemaQuiz 34
		-> round = 1
		-> questionnumber in round = 11
		-> organiser/designer: PépéQ
	"""

	quizinfo_pattern = ''.join(('toonbron_', question_number))

	try:
		quizinfo_div = questionrow.find('div', {'id': quizinfo_pattern})
		quizinfo_links = quizinfo_div.find_all('a')

		quiz_name = quizinfo_links[0].find('strong').text.strip()

		# " (2016)"  -->   2016
		year_pattern = re.compile('(?P<year>\d{4})')
		quiz_year = re.search(year_pattern, quizinfo_links[0].contents[1].strip()).group('year')

		quiz_url = ''.join(('https://www.quizarchief.be/speel', quizinfo_links[0].get('href')))
		quiz_roundinfo = quizinfo_links[1].find('strong').text.strip()
		quiz_organiser = quizinfo_links[2].find('strong').text.strip()


		quiz_info_dictionary = {}

		quiz_info_dictionary['quiz_name'] = quiz_name
		quiz_info_dictionary['quiz_year'] = quiz_year
		quiz_info_dictionary['quiz_url'] = quiz_url
		quiz_info_dictionary['quiz_roundinfo'] = quiz_roundinfo
		quiz_info_dictionary['quiz_organiser'] = quiz_organiser
		logger.info(f'quiz_info_dictionary for question {question_number}: \n {quiz_info_dictionary}')

		return quiz_info_dictionary

	except Exception as e:
		logger.error(f'No information about the quiz could be found for question_number: {question_number}, with exception: \n {e}')

		return None

def sleep_randomly(max_sleeptime, min_sleeptime=1):
	"""
	Return a random pause in seconds of maximum max_sleeptime.

	Arguments:
	max_sleeptime -- the maximum #seconds you want to wait before fetching a new question

	To prevent overloading of the server, this method provides a way to pause the execution for a given number of seconds.
	To make the interaction seem more human, we add some randomness.
	"""

	#The method sleep() suspends execution for the given number of seconds.
	sleeptime = random.randint(min_sleeptime, max_sleeptime)
	logger.info(f'I will be sleeping for {sleeptime} seconds. :) \n')
	
	time.sleep(sleeptime)

	return sleeptime

def find_page_for_question(requested_question_number, category):
	"""
	Return page_url & position on page for a given requested_question_number as a list: [page_url, question_position]

	Quizarchief.be does not apply a REST-interface,
	hence if we want to look up a specific question, we need to travel through all questions.

	To avoid to do this linearly, we apply a binary search algorithm.

	!the amount of questions displayed is different for logged in users.
	So make sure you log in when viewing the returned url in a browser.
	"""

	requested_question_number = int(requested_question_number)

	session = create_session()
	login(session, username=settings.CREDENTIALS.get('username', None), password=settings.CREDENTIALS.get('password', None))

	category_dictionary = create_category_dictionary()
	pages_for_category = compute_pages_for_category(category, category_dictionary)

	start_page = 0
	end_page = pages_for_category

	page_url = ''
	question_position = 0

	found = False

	while(not found):

		page_range = [start_page, end_page]
		logger.info(f'page_range {page_range}')

		requested_pagenr = math.ceil((page_range[1] - page_range[0])/2) + page_range[0]
		logger.info(f'requested_pagenr: {requested_pagenr} as ceiling of ((({page_range[1]} - {page_range[0]})/2) + {page_range[0]})')

		page_url = construct_url(category, requested_pagenr)
		logger.info(f'constructed page_url: {page_url}')
		page = session.get(page_url)
		soup = BeautifulSoup(page.content, 'html5lib', from_encoding='UTF-8')
		questionrows = find_all_questionrows(soup)

		questionrows_length = len(questionrows)
		logger.info(f'Length questionrows: {questionrows_length}')

		for question_position, questionrow in enumerate(questionrows):
			question_number_in_row = find_question_number(questionrow)
			logger.info(f'question_number in questionrow: {question_number_in_row}')
			int_question_number_in_row = int(question_number_in_row)
			logger.info(f'int(question_number): {int_question_number_in_row}')


			if requested_question_number == int_question_number_in_row:
				logger.info(f'{requested_question_number} == {int_question_number_in_row}')
				logger.info(f'*******************************************\nFound question {requested_question_number}:  \n page {requested_pagenr} - question {question_position+1} on the screen with page_url: \n {page_url} \n\nMake sure you are logged in when viewing the result in the browser!\n*******************************************')

				found = True

				break

			elif requested_question_number > int_question_number_in_row:
				logger.info(f'{requested_question_number} > {int_question_number_in_row}')
				logger.info(f'Hence, your requested question is on a page before this one.')
				end_page = requested_pagenr
				logger.info(f'Renewed search range: [{start_page}, {end_page}]')

			elif requested_question_number < int_question_number_in_row:
				logger.info(f'{requested_question_number} < {int_question_number_in_row}')
				logger.info(f'Hence, your requested question is on a page after this one.')
				start_page = requested_pagenr
				logger.info(f'Renewed search range: [{start_page}, {end_page}]')

		else:
			sleep_randomly(5, 0)

	question_location = [page_url, question_position]
	return question_location