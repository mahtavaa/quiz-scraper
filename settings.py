"""
CREDENTIALS

Arguments:

username:	valid username for https://www.quizarchief.be
password:	valid password for https://www.quizarchief.be
"""
CREDENTIALS = {
	'username': '',
	'password': ''
}

DATABASE_URL = 'quizarchief_v003.sqlite'
"""
CATEGORY

Arguments:
	Iterate over all available categories:
		ALL

	Select a single category:
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

	The list above might change over time, for the most recent overview, use:

	from scraper_utilities import create_category_dictionary()
	create_category_dicionary()
"""
CATEGORY = 'ALL'


""" FROM_PAGE: page to start from """
FROM_PAGE = 1

"""
TO_PAGE: 

Arguments:

<page_number> (integer):  	scrape till <page_number> (<page_number> excluded)

'ALL':						scrape till the last available page for the particular category
							(last page included)

Please note: use quotes around 'ALL', but not for the pagenumber
e.g.
TO_PAGE = 137
TO_PAGE = 'ALL'
"""
TO_PAGE = 'ALL'


"""
SLEEP_TIME:
    time between 2 requests to the server
    it is strongly discouraged to set this very low, 
    since this will put a heavy load on the server for a non-urgency process
"""
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
ONLY_NEW = True