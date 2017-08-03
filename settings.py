CREDENTIALS = {
	'username': '',
	'password': ''
}

DATABASE_URL = 'quizarchief.sqlite'
"""
CATEGORY

Arguments:
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
"""
CATEGORY = 'kunst-cultuur'

FROM_PAGE = 1
TO_PAGE = 328

SLEEP_TIME = 20

"""
ONLY_NEW

Arguments:

False:  scraper checks EVERY QUESTION on the page(s) between FROM_PAGE & TO_PAGE
        if the corresponding question_number is already in database, 
        the scraper will go to the next question

True:   scraper checks EVERY QUESTION on the page(s) between FROM_PAGE & TO_PAGE
        UNTIL IT FINDS a question_number that is already in the database
        when such question occurs, the scraper BREAKs its operations and downloading stops

Example:

question_numbers = [50, 47, 40, 32, 30, 28, 27, 21, 13, 7, 2]
database = [30, 28, 27, 21, 13]

def is_already_in_database(question_number):
	if question_number in database:
		return True

for question_number in question_numbers:
	if is_already_in_database(question_number):
		print(f'Question {question_number} is already present in database.')
		
		if settings.ONLY_NEW:
			break

		continue

	print(f'Downloading question {question_number}.')

ONLY_NEW = False:
	Downloading question 50.
	Downloading question 47.
	Downloading question 40.
	Downloading question 32.
	Question 30 is already present in database.
	Question 28 is already present in database.
	Question 27 is already present in database.
	Question 21 is already present in database.
	Question 13 is already present in database.
	Downloading question 7.
	Downloading question 2.

ONLY_NEW = True:
	Downloading question 50.
	Downloading question 47.
	Downloading question 40.
	Downloading question 32.
	Question 30 is already present in database.
"""
ONLY_NEW = False