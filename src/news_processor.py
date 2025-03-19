import json
import requests
import google.generativeai as genai
import sqlite3
import time
import concurrent.futures
from threading import Lock, Semaphore
import multiprocessing
import os
from gnews import GNews
from datetime import datetime, timedelta
from gemma_model import GemmaModel, GemmaResponse

# Import your existing functions and constants here
# (get_news, get_concerning_headlines, get_positive_headlines,
#  get_prayer_requests, get_gratefulness_reasons, remove_specific_chars_translate, country_map, etc.)
# Cache for API calls
news_cache = {}
country_cache = {}

GEMINI_API_KEY='XXXX'

language = 'English'

country_map = {
    "Afghanistan": "Afghanistan",
    "Angola": "Angola",
    "Albania": "Albania",
    "United Arab Emirates": "United Arab Emirates",
    "Argentina": "Argentina",
    "Armenia": "Armenia",
    "Antarctica": "Antarctica",
    "Fr. S. Antarctic Lands": "French Southern and Antarctic Lands",
    "Australia": "Australia",
    "Austria": "Austria",
    "Azerbaijan": "Azerbaijan",
    "Burundi": "Burundi",
    "Belgium": "Belgium",
    "Benin": "Benin",
    "Burkina Faso": "Burkina Faso",
    "Bangladesh": "Bangladesh",
    "Bulgaria": "Bulgaria",
    "Bahamas": "Bahamas",
    "Bosnia and Herz.": "Bosnia and Herzegovina",
    "Belarus": "Belarus",
    "Belize": "Belize",
    "Bolivia": "Bolivia",
    "Brazil": "Brazil",
    "Brunei": "Brunei",
    "Bhutan": "Bhutan",
    "Botswana": "Botswana",
    "Central African Rep.": "Central African Republic",
    "Canada": "Canada",
    "Switzerland": "Switzerland",
    "Chile": "Chile",
    "China": "China",
    "Côte d'Ivoire": "Ivory Coast",
    "Cameroon": "Cameroon",
    "Dem. Rep. Congo": "DR Congo",
    "Congo": "Republic of the Congo",
    "Colombia": "Colombia",
    "Costa Rica": "Costa Rica",
    "Cuba": "Cuba",
    "N. Cyprus": "North Cyprus",
    "Cyprus": "Cyprus",
    "Czechia": "Czechia",
    "Germany": "Germany",
    "Djibouti": "Djibouti",
    "Denmark": "Denmark",
    "Dominican Rep.": "Dominican Republic",
    "Algeria": "Algeria",
    "Ecuador": "Ecuador",
    "Egypt": "Egypt",
    "Eritrea": "Eritrea",
    "Spain": "Spain",
    "Estonia": "Estonia",
    "Ethiopia": "Ethiopia",
    "Finland": "Finland",
    "Fiji": "Fiji",
    "Falkland Is.": "Falkland Islands",
    "France": "France",
    "Gabon": "Gabon",
    "United Kingdom": "United Kingdom",
    "Georgia": "Georgia",
    "Ghana": "Ghana",
    "Guinea": "Guinea",
    "Gambia": "Gambia",
    "Guinea-Bissau": "Guinea-Bissau",
    "Eq. Guinea": "Equatorial Guinea",
    "Greece": "Greece",
    "Greenland": "Greenland",
    "Guatemala": "Guatemala",
    "Guyana": "Guyana",
    "Honduras": "Honduras",
    "Croatia": "Croatia",
    "Haiti": "Haiti",
    "Hungary": "Hungary",
    "Indonesia": "Indonesia",
    "India": "India",
    "Ireland": "Ireland",
    "Iran": "Iran",
    "Iraq": "Iraq",
    "Iceland": "Iceland",
    "Israel": "Israel",
    "Italy": "Italy",
    "Jamaica": "Jamaica",
    "Jordan": "Jordan",
    "Japan": "Japan",
    "Kazakhstan": "Kazakhstan",
    "Kenya": "Kenya",
    "Kyrgyzstan": "Kyrgyzstan",
    "Cambodia": "Cambodia",
    "South Korea": "South Korea",
    "Kosovo": "Kosovo",
    "Kuwait": "Kuwait",
    "Laos": "Laos",
    "Lebanon": "Lebanon",
    "Liberia": "Liberia",
    "Libya": "Libya",
    "Sri Lanka": "Sri Lanka",
    "Lesotho": "Lesotho",
    "Lithuania": "Lithuania",
    "Luxembourg": "Luxembourg",
    "Latvia": "Latvia",
    "Morocco": "Morocco",
    "Moldova": "Moldova",
    "Madagascar": "Madagascar",
    "Mexico": "Mexico",
    "Macedonia": "North Macedonia",
    "Mali": "Mali",
    "Myanmar": "Myanmar",
    "Montenegro": "Montenegro",
    "Mongolia": "Mongolia",
    "Mozambique": "Mozambique",
    "Mauritania": "Mauritania",
    "Malawi": "Malawi",
    "Malaysia": "Malaysia",
    "Namibia": "Namibia",
    "New Caledonia": "New Caledonia",
    "Niger": "Niger",
    "Nigeria": "Nigeria",
    "Nicaragua": "Nicaragua",
    "Netherlands": "Netherlands",
    "Norway": "Norway",
    "Nepal": "Nepal",
    "New Zealand": "New Zealand",
    "Oman": "Oman",
    "Pakistan": "Pakistan",
    "Panama": "Panama",
    "Peru": "Peru",
    "Philippines": "Philippines",
    "Papua New Guinea": "Papua New Guinea",
    "Poland": "Poland",
    "Puerto Rico": "Puerto Rico",
    "North Korea": "North Korea",
    "Portugal": "Portugal",
    "Paraguay": "Paraguay",
    "Palestine": "Palestine",
    "Qatar": "Qatar",
    "Romania": "Romania",
    "Russia": "Russia",
    "Rwanda": "Rwanda",
    "W. Sahara": "Western Sahara",
    "Saudi Arabia": "Saudi Arabia",
    "Sudan": "Sudan",
    "S. Sudan": "South Sudan",
    "Senegal": "Senegal",
    "Solomon Is.": "Solomon Islands",
    "Sierra Leone": "Sierra Leone",
    "El Salvador": "El Salvador",
    "Somaliland": "Somaliland",
    "Somalia": "Somalia",
    "Serbia": "Serbia",
    "Suriname": "Suriname",
    "Slovakia": "Slovakia",
    "Slovenia": "Slovenia",
    "Sweden": "Sweden",
    "Swaziland": "Eswatini",
    "Syria": "Syria",
    "Chad": "Chad",
    "Togo": "Togo",
    "Thailand": "Thailand",
    "Tajikistan": "Tajikistan",
    "Turkmenistan": "Turkmenistan",
    "Timor-Leste": "Timor-Leste",
    "Trinidad and Tobago": "Trinidad and Tobago",
    "Tunisia": "Tunisia",
    "Turkey": "Turkey",
    "Taiwan": "Taiwan",
    "Tanzania": "Tanzania",
    "Uganda": "Uganda",
    "Ukraine": "Ukraine",
    "Uruguay": "Uruguay",
    "United States of America": "United States",
    "Uzbekistan": "Uzbekistan",
    "Venezuela": "Venezuela",
    "Vietnam": "Vietnam",
    "Vanuatu": "Vanuatu",
    "Yemen": "Yemen",
    "South Africa": "South Africa",
    "Zambia": "Zambia",
    "Zimbabwe": "Zimbabwe",
    "South Georgia": "South Georgia",
    "Grenada": "Grenada",
    "Sierra Leone": "Sierra Leone",
    "Taiwan": "Taiwan",
    "Wallis and Futuna": "Wallis and Futuna",
    "Barbados": "Barbados",
    "Pitcairn Islands": "Pitcairn Islands",
    "Ivory Coast": "Ivory Coast",
    "Cape Verde": "Cape Verde",
    "Saint Kitts and Nevis": "Saint Kitts and Nevis",
    "Caribbean Netherlands": "Caribbean Netherlands",
    "Andorra": "Andorra",
    "Saint Barthélemy": "Saint Barthélemy",
    "Guernsey": "Guernsey",
    "Solomon Islands": "Solomon Islands",
    "Svalbard and Jan Mayen": "Svalbard and Jan Mayen",
    "Faroe Islands": "Faroe Islands",
    "Réunion": "Réunion",
    "North Korea": "North Korea",
    "Mauritius": "Mauritius",
    "Montserrat": "Montserrat",
    "United States Virgin Islands": "United States Virgin Islands",
    "Saint Pierre and Miquelon": "Saint Pierre and Miquelon",
    "Macau": "Macau",
    "San Marino": "San Marino",
    "Mayotte": "Mayotte",
    "Norfolk Island": "Norfolk Island",
    "Bouvet Island": "Bouvet Island",
    "São Tomé and Príncipe": "São Tomé and Príncipe",
    "Antarctica": "Antarctica",
    "British Virgin Islands": "British Virgin Islands",
    "Niue": "Niue",
    "Christmas Island": "Christmas Island",
    "Tokelau": "Tokelau",
    "Guam": "Guam",
    "Heard Island and McDonald Islands": "Heard Island and McDonald Islands",
    "Isle of Man": "Isle of Man",
    "Saint Lucia": "Saint Lucia",
    "Montserrat": "Montserrat",
    "Andorra": "Andorra",
    "Caribbean Netherlands": "Caribbean Netherlands",
    "British Indian Ocean Territory": "British Indian Ocean Territory",
    "Samoa": "Samoa",
    "Comoros": "Comoros",
    "Martinique": "Martinique",
    "Hong Kong": "Hong Kong",
    "Micronesia": "Micronesia",
    "Åland Islands": "Åland Islands",
    "Cocos (Keeling) Islands": "Cocos (Keeling) Islands",
    "Bouvet Island": "Bouvet Island",
    "Bermuda": "Bermuda",
    "Vatican City": "Vatican City",
    "Anguilla": "Anguilla",
    "Guernsey": "Guernsey",
    "Niue": "Niue",
    "Pitcairn Islands": "Pitcairn Islands",
    "Tokelau": "Tokelau",
    "Guam": "Guam",
    "Heard Island and McDonald Islands": "Heard Island and McDonald Islands",
    "Isle of Man": "Isle of Man",
    "Cayman Islands": "Cayman Islands",
    "Saint Kitts and Nevis": "Saint Kitts and Nevis",
    "Saint Lucia": "Saint Lucia"
}


def select_random_country():
    countries = [
        "Afghanistan", "Albania", "Algeria", "Angola", "Antarctica", 
        "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
        "Ecuador", "Egypt", "El Salvador", "Eq. Guinea", "Eritrea", 
        "Estonia", "Ethiopia", "India", "Indonesia", "Iran", 
        "Iraq", "Ireland", "Israel", "Italy", "Uganda", 
        "Ukraine", "United Arab Emirates", "United Kingdom", "United States of America", "Uruguay", 
        "Uzbekistan", "Bahamas", "Bangladesh", "Belarus", "Belgium", 
        "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herz.",
        "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", 
        "Burundi", "Cambodia", "Cameroon", "Canada", "Central African Rep.",
        "Chile", "China", "Colombia", "Congo", "Costa Rica", 
        "Croatia", "Cuba", "Cyprus", "Czechia", "Dem. Rep. Congo", 
        "Denmark", "Djibouti", "Dominican Rep.", "Falkland Is.", "Fiji", 
        "Finland", "Fr. S. Antarctic Lands", "France", "Gabon", "Gambia", 
        "Georgia", "Germany", "Ghana", "Greece", "Greenland", 
        "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", 
        "Honduras", "Hungary", "Iceland", "Jamaica", "Japan", 
        "Jordan", "Kazakhstan", "Kenya", "Kosovo", "Kuwait", 
        "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", 
        "Liberia", "Libya", "Lithuania", "Luxembourg", "Macedonia", 
        "Madagascar", "Malawi", "Malaysia", "Mali", "Mauritania", 
        "Mexico", "Moldova", "Mongolia", "Montenegro", "Morocco", 
        "Mozambique", "Myanmar", "N. Cyprus", "Namibia", "Nepal", 
        "Netherlands", "New Caledonia", "New Zealand", "Nicaragua", "Niger", 
        "Nigeria", "North Korea", "Norway", "Oman", "Pakistan", 
        "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", 
        "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", 
        "Romania", "Russia", "Rwanda", "Saudi Arabia", "Senegal", 
        "Serbia", "Sierra Leone", "Slovakia", "Slovenia", "Solomon Is.",
        "Somalia", "Somaliland", "South Africa", "South Korea", "Spain", 
        "Sri Lanka", "Sudan", "Suriname", "Swaziland", "Sweden", 
        "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", 
        "Thailand", "Timor-Leste", "Togo", "Trinidad and Tobago", "Tunisia", 
        "Turkey", "Turkmenistan", "Venezuela", "Vanuatu", "Vietnam", 
        "W. Sahara", "Yemen", "Zambia", "Zimbabwe"
    ]


    # Select a random country
    random_country = random.choice(countries)

    return random_country

def get_news(query, max_results=40):
    google_news = GNews(language='en', country='US', period='7d', max_results=max_results)
    news_items = google_news.get_news(query)
    
    # Transform the data to match the structure we were using before
    transformed_news = []
    for item in news_items:
        transformed_item = {
            'title': item['title'],
            'description': item['description'],
            'url': item['url'],
            'publishedAt': item['published date'],
            'source': {
                'name': item['publisher']['title'],
                'url': item['publisher']['href']
            }
        }
        transformed_news.append(transformed_item)
    
    return transformed_news

def get_concerning_headlines(articles, location, language='English'):
    #articles = get_news()
    #print(articles[0])
    titles = [article['title'] for article in articles if article['title'] is not None]
    urls = [article['url'] for article in articles if article['url'] is not None]
    
    
    
    #title_to_url = {article['title']: article['url'] for article in articles if article['title'] is not None and article['url'] is not None}
    #country_news = [item for item in country_news if item is not None]
    
    #print(titles)

    prompt = """You are an expert news analyst with extensive experience in analysing news sources from across the globe. Your ultimate goal is to help people spread peace and positivity in the world by best informing them on how they can pray for {location}. Your role is to rank this series of articles from more concerning to less concerning based on their titles. I know that ranking levels of concern might be a subjective task. So, Please use criterias such as urgency, potential negative impact, and global significance, wars, civil unrest, acts of terror, epidemics, political unrest, violence, natural disasters, technology failures, and related topics you might find concerning. Please remember that your goal is to bring peace by informing people around the world on how to pray for {location} in the midst of these terrible events. Also, use your understanding to make sure that your top articles are truly about {location} and not just vaguely mentioning {location}. Please return only the sorted (from most to least concerning) and numbered list of titles, with no additional explanation and no markdown formatting. Here are the titles:
    
    {titles}
    
    Sorted titles (from most concerning to least concerning): 
    """
    
    #print(location, language, titles)
    #Il est TRES IMPORTANT que tu fournisses TOUTES tes reponses en FRANCAIS afin d'ameliorer l'experience utilisateur. 
    
    # format prompt and make a call to the Gemini api
    formatted_prompt = prompt.format(titles="\n".join(titles), location=location, language=language)
    
    
    #model = GemmaModel()
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    text_response = model.generate_content(formatted_prompt).text
    
    #print(text_response)
    
    text_response = model.generate_content(f"Please TRANSLATE the following to {language}, keeping all formatting of the original text, DO NOT add any explanation or introduction: {text_response}").text        
    
    #print(text_response)
    sorted_titles = arrayfy_response(text_response)
    
    indexed_titles = list(enumerate(titles))
    sorted_indices = [i for i, title in indexed_titles if title in sorted_titles]
    
    #sorted_urls = [title_to_url[title] for title in sorted_titles]
    sorted_urls = [urls[i] for i in sorted_indices]

    headlines = sorted_titles[:20]
    urls = sorted_urls[:20]
    #print(headlines[:5])
    #print(urls[:5])

    return headlines, urls

def get_prayer_requests(headlines, location, language='English'):
    #print(language)
    prompt_pray = """You are a person of faith, a Man or a Woman of God who believes and trusts in the Lord Jesus for the betterment of the World. Given today's concerning headlines about {location}, you would like to help people around the World to pray for {location}. You have the opportunity, given the headlines, to succinctly formulate three prayer requests letting people know what they can pray for today about {location} and its populations affected by the events related in the headlines. Peace think deeply about the headlines, and make your prayer requests specific to them, such that someone can easily relate them to the headlines. Formulate each prayer request in one short sentence, starting with 'Pray for' each. Remove all formating. Here are the headlines:
        
        {headlines}
    """
    
    formatted_prompt = prompt_pray.format(headlines="\n".join(headlines), location=location, language=language)
        
    #model = GemmaModel()
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')   
    text_response = model.generate_content(formatted_prompt).text
    
    text_response = model.generate_content(f"Please TRANSLATE the following to {language}, keeping all formatting of the original text, DO NOT add any explanation or introduction: {text_response}").text

    prayers = text_response.split('\n')
    filtered_prayers = [prayer for prayer in prayers if prayer][:3]
    
    #print(text_response.split('\n'))
    #print(prayers)
    #print(filtered_prayers)
    

    return(filtered_prayers)

def get_positive_headlines(articles, location, language='English'):
    #titles = [article['title'] for article in articles]
    titles = [article['title'] for article in articles if article['title'] is not None]

    prompt = """
    You are an expert news analyst with extensive experience in analysing news sources from across the globe. Your ultimate goal is to help people spread peace and positivity in the world by best informing them on how they can be thankful for {location}. Your role is to rank this series of articles from positive to negative based on their titles. I know that ranking levels of positivity might be a subjective task. So, Please use factors that may have national or global significance such as cultural events, acts of generosity, national celebration(s), crisis or tragedy avoided, peaceful political transition, crisis resolution, new infrastructure, and related topics you might deem worthy of evoking gratefulness. Please remember that your goal is to get people to be positive and grateful by informing them about positive events and happenings in {location}. Also, use your understanding to make sure that your top articles are truly about {location} and not just vaguely mentioning {location}. Please return only the sorted and numbered list of titles, with no additional explanation and no markdown formatting. Here are the titles:
    
    {titles}

    Sorted titles (from most positive to least positive):
    """
    #Sorted titles (from most positive to least positive):
    #"It is VERY IMPORTANT that every single line of your answer is in {language}. DO SEE IT to translate every line of your text to {language}."
    
    # format prompt and make a call to the Gemini api
    formatted_prompt = prompt.format(titles="\n".join(titles), location=location, language=language)    
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    text_response = model.generate_content(formatted_prompt).text
    
    #print(text_response)
    
    text_response = model.generate_content(f"Please TRANSLATE the following to {language}, keeping all formatting of the original text, DO NOT add any explanation or introduction: {text_response}").text

    sorted_titles = arrayfy_response(text_response)

    headlines = sorted_titles[:20]

    return headlines

def get_gratefulness_reasons(headlines, location, language='English'):
    prompt_thankful = """You are a person of faith, a Man or a Woman of God who believes and trusts in the Lord Jesus for the betterment of the World. Given today's positive headlines about {location}, you would like to help people around the World be thankful about {location} and its people, and by doing so spread productivity and a spirit of gratitude in the world. You have the opportunity, given the headlines, to succinctly formulate three reasons why people can be thankful today about what is going on in {location}. Don't worry, we will also cover negative news, but for now, we are focused on positivity and giving people reasons to be thankful and hopeful. Please think deeply about the headlines, and make your reasons specific to them, such that someone can easily relate them to the headlines, but don't repeat the headlines in your answers. Avoid controversial subjects ! Formulate each reason in a short sentence, starting with 'Be grateful'. Remove all formating. Here are the headlines:
    
        {headlines}
    """

    formatted_prompt = prompt_thankful.format(headlines="\n".join(headlines), location=location, language=language)
        
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        
    text_response = model.generate_content(formatted_prompt).text
    
    text_response = model.generate_content(f"Please TRANSLATE the following to {language}, keeping all formatting of the original text, DO NOT add any explanation or introduction: {text_response}").text

    reasons = text_response.split('\n')
    filtered_reasons = [reason for reason in reasons if reason][:3]
    
    #print(text_response.split('\n'))
    #print(reasons)
    #print(filtered_reasons)

    return(filtered_reasons)

def arrayfy_response(text_response):
    # Split the text into lines and remove the introductory text
    lines = text_response.split('\n')
    title_lines = [line for line in lines if '.' in line]#lines[0:]

    # Extract titles by removing the numbering
    array_items = [line.split('. ', 1)[1].strip() for line in title_lines if line.strip()]

    return array_items

def get_country_info(country_name):
    if country_name in country_cache:
        return country_cache[country_name]
    
    url = f"https://restcountries.com/v3.1/name/{country_map[country_name]}"
    response = requests.get(url)
    data = response.json()
    
    #print(country_name, country_map[country_name], data)
    #print(data)
    if data:
        country_info = {
            'name': country_name,#data[0]['name']['common'],
            'capital': data[0]['capital'][0] if 'capital' in data[0] else 'N/A',
            'population': data[0]['population'],
            'region': data[0]['region'],
            'subregion': data[0]['subregion'] if 'subregion' in data[0] else 'N/A',
            'alpha2Code': data[0]['cca2'].lower()
        }
        country_cache[country_name] = country_info
        return country_info
    return None

def remove_specific_chars_translate(string, chars_to_remove):
    return string.translate(str.maketrans('', '', chars_to_remove))

# Global variables
db_lock = Lock()
api_semaphore = Semaphore(5)  # Limit concurrent API calls
PROCESS_COUNT = max(1, os.cpu_count() - 1)  # Use all but one CPU core
THREAD_POOL_SIZE = 5  # Threads per process, adjust based on your workload

def create_database():
    conn = sqlite3.connect('news_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS country_data
                 (country TEXT PRIMARY KEY, data JSON, timestamp DATETIME)''')
    conn.commit()
    return conn

def create_database_de():
    conn = sqlite3.connect('news_data_de.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS country_data
                 (country TEXT PRIMARY KEY, data JSON, timestamp DATETIME)''')
    conn.commit()
    return conn

def create_database_fr():
    conn = sqlite3.connect('news_data_fr.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS country_data
                 (country TEXT PRIMARY KEY, data JSON, timestamp DATETIME)''')
    conn.commit()
    return conn

def create_database_es():
    conn = sqlite3.connect('news_data_es.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS country_data
                 (country TEXT PRIMARY KEY, data JSON, timestamp DATETIME)''')
    conn.commit()
    return conn

def process_country(name, mapped_name):
    try:
        with api_semaphore:
            country_info = get_country_info(name)
            if not country_info:
                print(f"Could not get country info for {name}")
                return None

            country_news = get_news(mapped_name)
            neg_headlines, neg_urls = get_concerning_headlines(country_news, mapped_name, 'English')
            pos_headlines = get_positive_headlines(country_news, mapped_name, 'English')
            prayers = get_prayer_requests(neg_headlines, mapped_name, 'English')
            reasons = get_gratefulness_reasons(pos_headlines, mapped_name, 'English')

        prayers = [remove_specific_chars_translate(prayer, "#*") for prayer in prayers]
        reasons = [remove_specific_chars_translate(reason, "#*") for reason in reasons]
        neg_headlines = [remove_specific_chars_translate(headline, "#*") for headline in neg_headlines[:5]]

        data = {
            'country_info': country_info,
            'news': neg_headlines,
            'urls': neg_urls,
            'prayers': prayers,
            'reasons': reasons
        }

        return (name, data)

    except Exception as e:
        print(f"Error processing {name}: {str(e)}")
        return None

def worker_process(country_chunk):
    genai.configure(api_key=GEMINI_API_KEY)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
        futures = [executor.submit(process_country, name, mapped_name) for name, mapped_name in country_chunk]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    return results

def update_database2(db_conn, db_cursor, results):
    with db_lock:
        for name, data in results:
            db_cursor.execute('''INSERT OR REPLACE INTO country_data (country, data, timestamp)
                         VALUES (?, ?, ?)''', (name, json.dumps(data), datetime.now()))
        db_conn.commit()

def update_database(db_conn, db_cursor, results):
    with db_lock:
        for name, data in results:
            db_cursor.execute('''UPDATE country_data 
                                 SET data = ?, timestamp = ?
                                 WHERE country = ?''', 
                              (json.dumps(data), datetime.now(), name))
            
            # If no rows were updated, it means the country doesn't exist, so we insert it
            if db_cursor.rowcount == 0:
                db_cursor.execute('''INSERT INTO country_data (country, data, timestamp)
                                     VALUES (?, ?, ?)''', 
                                  (name, json.dumps(data), datetime.now()))
        
        db_conn.commit()        


SEPARATOR = " ||| "  # Unique separator for splitting translated text
ENTRY_SEPARATOR = " ### "  # Separator between countries
BATCH_SIZE = 15  # Process 16 countries at a time

languages = ["German", "French", "Spanish"]
databases = ["news_data_de.db", "news_data_fr.db", "news_data_es.db"]

def translate(text: str, language: str):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    #model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    prompt = f"Translate the following text to {language}. Please make sure to keep all formatting characters as they will be indispensable for parsing the translated text. Here is the text: {text}"
    response = model.generate_content(prompt)
    return response.text

def prepare_batches(cursor, batch_size):
    """Retrieve data and prepare batches for translation."""
    cursor.execute("SELECT country, data FROM country_data")
    rows = cursor.fetchall()

    combined_texts = []
    batch_starts = range(0, len(rows), batch_size)

    for batch_start in batch_starts:
        batch = rows[batch_start:batch_start + batch_size]

        entries = []
        for _, data_json in batch:
            data = json.loads(data_json)
            #entry_text = SEPARATOR.join(
            #    [data['country_info']] + data['news'] + data['prayers'] + data['reasons']
            #)
            entry_text = SEPARATOR.join(
                [str(data['country_info'])] + 
                [str(news_item) for news_item in data['news']] + 
                [str(prayer) for prayer in data['prayers']] + 
                [str(reason) for reason in data['reasons']]
            )

            entries.append(entry_text)

        combined_texts.append(ENTRY_SEPARATOR.join(entries))  # Store batch text

    return combined_texts, rows

def translate_and_update(cursor, batches, rows, batch_size, language):
    """Translate each batch and update the database."""
    for batch_idx, batch_text in enumerate(batches):
        translated_text = translate(batch_text, language)  # Single call per batch

        # Split translated text back into country-specific sections
        translated_entries = translated_text.split(ENTRY_SEPARATOR)
        
        

        # Update database for this batch
        batch_start = batch_idx * batch_size
        batch_rows = rows[batch_start:batch_start + batch_size]

        for i, (country, data_json) in enumerate(batch_rows):
            
            #print(i, len(batch_rows), len(translated_entries))
            
            data = json.loads(data_json)
            translated_parts = translated_entries[i].split(SEPARATOR)

            translated_data = {
                'country_info': translated_parts[0],
                'news': translated_parts[1:1+len(data['news'])],
                'prayers': translated_parts[1+len(data['news']):1+len(data['news'])+len(data['prayers'])],
                'reasons': translated_parts[1+len(data['news'])+len(data['prayers']):]
            }
            
            #print(translated_data)

            updated_json = json.dumps(translated_data)

            cursor.execute(
                "UPDATE country_data SET data = ?, timestamp = ? WHERE country = ?",
                (updated_json, datetime.now(), country)
            )
            
            # If no rows were updated, it means the country doesn't exist, so we insert it
            if cursor.rowcount == 0:
                cursor.execute('''INSERT INTO country_data (country, data, timestamp)
                                     VALUES (?, ?, ?)''', 
                                  (country, updated_json, datetime.now()))
    
def handle_other_languages(db_conn, db_cursor):
    """Main function to prepare data, translate, and update the database."""
    
    #main_database = "news_data.db"
    
    #conn = sqlite3.connect(main_database)
    #cursor = conn.cursor()

    #batches, rows = prepare_batches(cursor, BATCH_SIZE)
    #conn.close()
    
    batches, rows = prepare_batches(db_cursor, BATCH_SIZE)
    #db_conn.close()
    
    for language, database in zip(languages, databases):
        print(f"############# {language} ############")
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        translate_and_update(cursor, batches, rows, BATCH_SIZE, language)

        conn.commit()
        conn.close()

def main():
    db_conn = create_database()
    db_cursor = db_conn.cursor()
    
    create_database_de()
    create_database_es()
    create_database_fr()

    try:
        while True:
            start_time = time.time()
            print("Starting database update... Start time: ", datetime.now().strftime("%H:%M:%S")) 
            
            #"""
            # Split countries into chunks for each process
            countries = list(country_map.items())
            chunk_size = len(countries) // PROCESS_COUNT + 1
            country_chunks = [countries[i:i + chunk_size] for i in range(0, len(countries), chunk_size)]

            # Process countries using multiple processes
            with multiprocessing.Pool(PROCESS_COUNT) as pool:
                all_results = pool.map(worker_process, country_chunks)

            # Flatten results and update database
            flattened_results = [item for sublist in all_results for item in sublist if item]
            update_database(db_conn, db_cursor, flattened_results)

            end_time = time.time()
            print(f"Database update complete. Stop time: {datetime.now().strftime('%H:%M:%S')}. Time taken: {end_time - start_time:.2f} seconds")
            print(f"Processed {len(flattened_results)} countries")
            #"""
            
            print(f"Translating to other languages")
            handle_other_languages(db_conn, db_cursor)
            
            print("Sleeping for 24 hours...")
            time.sleep(86400)#28800)  # Sleep for 24 hours before the next update

    finally:
        db_conn.close()        

def main2():
    db_conn = create_database()
    db_cursor = db_conn.cursor()

    try:
        while True:
            start_time = time.time()
            print("Starting database update... Start time: ", datetime.now().strftime("%H:%M:%S")) 
            
            # Split countries into chunks for each process
            countries = list(country_map.items())
            chunk_size = len(countries) // PROCESS_COUNT + 1
            country_chunks = [countries[i:i + chunk_size] for i in range(0, len(countries), chunk_size)]

            # Process countries using multiple processes
            with multiprocessing.Pool(PROCESS_COUNT) as pool:
                all_results = pool.map(worker_process, country_chunks)

            # Flatten results and update database
            flattened_results = [item for sublist in all_results for item in sublist if item]
            update_database(db_conn, db_cursor, flattened_results)

            end_time = time.time()
            print(f"Database update complete. Stop time: {datetime.now().strftime('%H:%M:%S')}. Time taken: {end_time - start_time:.2f} seconds")
            print(f"Processed {len(flattened_results)} countries")
            print("Sleeping for 24 hours...")
            time.sleep(86400)#28800)  # Sleep for 24 hours before the next update

    finally:
        db_conn.close()

if __name__ == '__main__':
    main()