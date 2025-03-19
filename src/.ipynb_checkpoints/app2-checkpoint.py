import json
import random
import requests
from datetime import datetime
import google.generativeai as genai
from flask import Flask, render_template, jsonify

app = Flask(__name__, static_folder='static')

# Cache for API calls
news_cache = {}
country_cache = {}

NEWS_API_KEY = '23ac68a4979a428aac149b8da1b86455'
GEMINI_API_KEY='AIzaSyD4rf0IR3vMQbZZRvg2EdQvdioqZKkXrvE'

BASE_URL = 'https://newsapi.org/v2/'

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

def get_news(query, max_results=40, from_date=None, to_date=None, sort_by='publishedAt'):

    cache_key = f'news_{query}'
    if cache_key in news_cache and (datetime.now() - news_cache[cache_key]['timestamp']).seconds < 3600:
        return news_cache[cache_key]['data']

    endpoint = f'{BASE_URL}everything'
    
    params = {
        'q': query,
        'apiKey': NEWS_API_KEY,
        'sortBy': sort_by,
        'pageSize': min(max_results, 100)
    }
    
    if from_date:
        params['from'] = from_date
    if to_date:
        params['to'] = to_date
    
    response = requests.get(endpoint, params=params)
    data = response.json()
    news = data.get('articles', [])

    news_cache[cache_key] = {
        'data': news,
        'timestamp': datetime.now()
    }
    
    if response.status_code == 200:
        return news
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def get_concerning_headlines(articles, location, language='English'):
    #articles = get_news()
    titles = [article['title'] for article in articles if article['title'] is not None]
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
    
    
    
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    text_response = model.generate_content(formatted_prompt).text
    
    #print(text_response)
    
    text_response = model.generate_content(f"Please TRANSLATE the following to {language}, keeping all formatting of the original text, DO NOT add any explanation or introduction: {text_response}").text        
    
    
    #print(text_response)
    sorted_titles = arrayfy_response(text_response)

    headlines = sorted_titles[:20]
    #print(headlines)
    

    return headlines

def get_prayer_requests(headlines, location, language='English'):
    #print(language)
    prompt_pray = """You are a person of faith, a Man or a Woman of God who believes and trusts in the Lord Jesus for the betterment of the World. Given today's concerning headlines about {location}, you would like to help people around the World to pray for {location}. You have the opportunity, given the headlines, to succinctly formulate three prayer requests letting people know what they can pray for today about {location} and its populations affected by the events related in the headlines. Peace think deeply about the headlines, and make your prayer requests specific to them, such that someone can easily relate them to the headlines. Formulate each prayer request in one short sentence, starting with 'Pray for' each. Remove all formating. Here are the headlines:
        
        {headlines}
    """
    
    formatted_prompt = prompt_pray.format(headlines="\n".join(headlines), location=location, language=language)
        
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        
    text_response = model.generate_content(formatted_prompt).text
    
    text_response = model.generate_content(f"Please TRANSLATE the following to {language}, keeping all formatting of the original text, DO NOT add any explanation or introduction: {text_response}").text

    prayers = text_response.split('\n')
    filtered_prayers = [prayer for prayer in prayers if prayer][:3]
    
    return(filtered_prayers)

def get_positive_headlines(articles, location, language='English'):
    titles = [article['title'] for article in articles]
    titles = [article['title'] for article in articles if article['title'] is not None]

    prompt = """
    You are an expert news analyst with extensive experience in analysing news sources from across the globe. Your ultimate goal is to help people spread peace and positivity in the world by best informing them on how they can be thankful for {location}. Your role is to rank this series of articles from positive to negative based on their titles. I know that ranking levels of positivity might be a subjective task. So, Please use factors that may have national or global significance such as cultural events, acts of generosity, national celebration(s), crisis or tragedy avoided, peaceful political transition, crisis resolution, new infrastructure, and related topics you might deem worthy of evoking gratefulness. Please remember that your goal is to get people to be positive and grateful by informing them about positive events and happenings in {location}. Also, use your understanding to make sure that your top articles are truly about {location} and not just vaguely mentioning {location}. Please return only the sorted and numbered list of titles, with no additional explanation and no markdown formatting. Here are the titles:
    
    {titles}

    Sorted titles (from most positive to least positive):
    """
    # format prompt and make a call to the Gemini api
    formatted_prompt = prompt.format(titles="\n".join(titles), location=location, language=language)    
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    text_response = model.generate_content(formatted_prompt).text
    
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

# @app.route('/')
# def index():
#    news = get_news()[:5]
#    return render_template('index.html', news=news)

@app.route('/')
def index():
    
    name = select_random_country()
    country_info = get_country_info(name)

    country_news = get_news(name)#country_info['alpha2Code'])
    #country_news = [item for item in country_news if item is not None]
    #print(country_news[0])
    
    #language = 'French'
    #language = 'English'
    
    print(name, language)
    
    neg_headlines = get_concerning_headlines(country_news, country_map[name], language)
    pos_headlines = get_positive_headlines(country_news, country_map[name], language)
    prayers = get_prayer_requests(neg_headlines, country_map[name], language)
    reasons = get_gratefulness_reasons(pos_headlines, country_map[name], language)
    
    prayers = [remove_specific_chars_translate(prayer, "#*") for prayer in prayers]
    reasons = [remove_specific_chars_translate(reason, "#*") for reason in reasons]
    neg_headlines = [remove_specific_chars_translate(reason, "#*") for reason in neg_headlines]

    #return jsonify({'country_info': country_info, 'news': country_news})
    #data = jsonify({'country_info': country_info, 'news': neg_headlines[:5], 'prayers': prayers, 'reasons': reasons})
    data = {}
    data['country_info'] = country_info
    data['news'] = neg_headlines[:5]
    data['prayers'] = prayers
    data['reasons'] = reasons

    return render_template('index.html', data=data)

@app.route('/api/country/<name>')
@app.route('/api/country/<name>/<language>')
def api_country(name, language='English'):
    #print(name)
    country_info = get_country_info(name)
    
    if country_info:
        country_news = get_news(name)#country_info['alpha2Code'])
        neg_headlines = get_concerning_headlines(country_news, country_map[name], language)
        pos_headlines = get_positive_headlines(country_news, country_map[name], language)
        prayers = get_prayer_requests(neg_headlines, country_map[name], language)
        reasons = get_gratefulness_reasons(pos_headlines, country_map[name], language)
        
        prayers = [remove_specific_chars_translate(prayer, "#*") for prayer in prayers]
        reasons = [remove_specific_chars_translate(reason, "#*") for reason in reasons]
        neg_headlines = [remove_specific_chars_translate(reason, "#*") for reason in neg_headlines]

        #return jsonify({'country_info': country_info, 'news': country_news})
        return jsonify({'country_info': country_info, 'news': neg_headlines[:5], 'prayers': prayers, 'reasons': reasons})
    
    return jsonify({'error': 'Country not found'}), 404

if __name__ == '__main__':
    genai.configure(api_key=GEMINI_API_KEY)
    app.run(debug=False, host='0.0.0.0', port=5000)
