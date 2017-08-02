from bs4 import BeautifulSoup
import os
import random
import re
import requests
import shutil
import sqlite3
import time

from logger_setup import create_logger

logger = create_logger(__name__)


def createSession():
	"""Return a requests' session object."""

	with requests.Session() as session:

		logger.debug('Session established')
		return session

def login(session, username, password):
	"""
	Return HTTP status code -> 200 if logged in correctly.

	Keyword arguments:
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
	logger.info(f'Your attempt to log in, resulted in HTTP status code: {loging_status}')

	return login_status

def construct_url(categorie, page):
	"""
	Return constructed url.

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

	pn -- page number
	
	aoqpp -- amount of questions per page:
	    1: 1 vraag
	    3: 3 vragen
	    5: 5 vragen
	    10: 10 vragen
	    15: 15 vragen
	    20: 20 vragen

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
	categorie = categorie
	page = page

	url = 'https://www.quizarchief.be/categorie/{categorie}/{page}/20/1/0'.format(categorie=categorie, page=page)
	
	print('url constructed as: \n {url}'.format(url=url))
	return url

def get_questionpage(url, session):
	s = session
	url = url

	questionpage = s.get(url)
	questionpage.encoding = 'utf-8'

	print('Questionpage was fetched with status code: {status_code}'.format(status_code=questionpage.status_code))
	return questionpage

def make_soup(page):
	questionpage = page

	soup = BeautifulSoup(questionpage.content, 'html5lib')

	#delete all <br/> elements, otherwise this will confuse question parser
	for br in soup.find_all('br'):
		br.extract()

	print('Soup is very hot, bon appetit!')
	return soup

def find_all_questionrows(soup):
	vragenrij_regex = re.compile('vragenrij_\d+')
	questionrows = soup.find_all('div', {'id': vragenrij_regex})

	print('There were {questionrows_amount} questionrows found on the given page.'.format(questionrows_amount=len(questionrows)))
	return questionrows

def find_question_id(questionrow):
	dirty_question_number = questionrow.get('id')
	clean_question_number = re.search('(?:vragenrij_)(\d+)', dirty_question_number).group(1)

	question_id = clean_question_number
	return question_id

def find_question(questionrow, question_id):
	question = ""
	questionrow = questionrow
	question_id = question_id

	try:
			#if there is no tag, it is directly under the div, so contents[0]
			tag_regex = re.compile('tag_\d+')

			if len(questionrow.find_all('a', {'id': tag_regex})) > 0:

				question_div = questionrow.find('div', {'class': 'vragenrij'})
				question = question_div.contents[1].encode('utf-8').strip()
				
				print('Question: \n')
				print(question)
				print('\n')

			else:
				question_div = questionrow.find('div', {'class': 'vragenrij'})
				question = question_div.contents[0].encode('utf-8').strip()
				
				print('Question:')
				print(question)
				print('\n')

			return question

	except Exception as e:
		print("An exception occured while parsing question with id: {question_id}".format(question_id=question_id))
		print("With exception message: \n {exception_message}".format(exception_message=e))
		
		return question

		pass	

def find_tags(questionrow):
	questionrow = questionrow
	tags = []

	try:
		#if there is no tag, it is directly under the div, so contents[0]
		tag_regex = re.compile('tag_\d+')

		taglinks = questionrow.find_all('a', {'id': tag_regex})
		tags = [tag.text for tag in taglinks]

		print('Tags:')
		print(tags)
		print('\n')

		return tags

	except Exception as e:
		print("An exception occured while parsing tags for question with id: {question_id}".format(question_id=question_id))
		print("With exception message: \n {exception_message}".format(exception_message=e))
		
		return tags

		pass	
	
	

def find_image(questionrow, categorie, session):
	"""
	if image: find_image(questionrow, categorie, session) -> image_filename
	+ downloads the image to a folder relatively located at ./{categorie}/

	if no image: find_image(questionrow, categorie, session) -> None

	if there is an image accompanying the question, this function will return the image_filename
	the image_filename is the combination of the question_number with an extension
	this extension can take multiple formats (jpg, jpeg, png, ...) & should be saved accordingly

	if there is no image, find_image() returns None
	"""

	class ImageNotFound(Exception):
		"""
		Exception which handles the lack of an image in a questionrow.
		"""

	class YoutubeInsteadOfImage(Exception):
		"""
		This exception should be raised when the embedded visual is a youtube video and NOT an image.
		"""

	try:
		question_image_centerdiv = questionrow.find('center')

		if not question_image_centerdiv:
			raise ImageNotFound

		question_img = question_image_centerdiv.find('img')

		if not question_img:
			raise YoutubeInsteadOfImage

	except ImageNotFound:
		logger.info(f'Questionrow: {questionrow}. No image was found for this questionrow.')
		return None

	except YoutubeInsteadOfImage:
		logger.info(f'Questionrow: {questionrow}. The embedded visual is a youtube link, not an image.')
		return None

	except Exception as e:
		logger.error(f'Questionrow: {questionrow}. An unexpected exception occurred while parsing the embedded visual with the following exception message: \n {e}.')
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
	directory = './{categorie}/'.format(categorie=categorie)
	filepath = os.path.join(directory, image_filename)

	os.makedirs(directory, exist_ok=True)

	#download the image to the folder
	with open(filepath, 'wb') as imagefile:
		shutil.copyfileobj(image.raw, imagefile)
		logger.debug(f'{image_filename} downloaded to {filepath}')
	del image

	return image_filename


def find_answer(questionrow, question_id, session):
	answer = ""
	questionrow = questionrow
	question_id = question_id
	s = session

	try:
		answer_url = 'https://www.quizarchief.be/beantwoordevragen.php?vraagid={question_id}&page=categorie'.format(question_id=question_id)
		answer_page = s.get(answer_url)
		answer_page.encoding = 'utf-8'

		soup = BeautifulSoup(answer_page.content, 'html5lib')

		answer = soup.find('b').text.strip()

		print('Answer:')
		print(answer)
		print('\n')

		return answer

	except Exception as e:
		print("An exception occured while parsing answer for question with id: {question_id}".format(question_id=question_id))
		print("With exception message: \n {exception_message}".format(exception_message=e))
		
		return answer
		
		pass

def write_to_databse(cursor, question_id, question, answer, image):
	cursor = cursor
	question_id = question_id
	question = question
	answer = answer
	image = image

	question_row = (question_id, question, answer, image)

	try:
		cursor.execute('INSERT OR REPLACE INTO QUESTION(Question_ID, Question, Answer, Image) VALUES (?,?,?,?)', question_row)

	except Exception as e:
		print("An exception occured while writing the answer to the database for question with id: {question_id}".format(question_id=question_id))
		print("With exception message: \n {exception_message}".format(exception_message=e))
		pass	

def sleep_randomly(max_sleeptime):
	max_sleeptime = max_sleeptime

	# The method sleep() suspends execution for the given number of seconds.
	seconds = random.randint(1, max_sleeptime)
	print('I will be sleeping for {seconds} seconds. :)'.format(seconds=seconds))
	time.sleep(seconds)