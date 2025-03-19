from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import google.generativeai as genai
import random
import ast

GEMINI_API_KEY='XXXX'

app = Flask(__name__, static_folder='static')

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

def get_country_data(name, language='English'):
    if language == 'French':    
        conn = sqlite3.connect('news_data_fr.db')
    elif language == 'German':    
        conn = sqlite3.connect('news_data_de.db')
    elif language == 'Spanish':    
        conn = sqlite3.connect('news_data_es.db')
    else:    
        conn = sqlite3.connect('news_data.db')
        
    c = conn.cursor()
    c.execute('SELECT data FROM country_data WHERE country = ?', (name,))
    result = c.fetchone()
    conn.close()

    if result:
        data = json.loads(result[0])
        #print(data['country_info'])
        #data['country_info'] = ast.literal_eval(data['country_info'])
        #data['country_info'] = jsonify(data['country_info'])
        if language == 'English' and language == 'German' and language == 'Spanish':
            data['country_info'] = ast.literal_eval(data['country_info'])
        #    data = translate_data(data, language)
        return data
    return None

def translate_data(data, language):
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    
    for key in ['news', 'prayers', 'reasons']:
        translated_items = []
        for item in data[key]:
            prompt = f"Translate the following to {language}: {item}"
            response = model.generate_content(prompt)
            translated_items.append(response.text)
        data[key] = translated_items
    
    return data

@app.route('/')
def index():
    name = select_random_country()
    data = get_country_data(name)
    return render_template('index.html', data=data)

@app.route('/api/country/<name>')
@app.route('/api/country/<name>/<language>')
def api_country(name, language='English'):
    data = get_country_data(name, language)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Country not found'}), 404



########### Prayer Chain ###########
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


#app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prayer_chain.db'
db = SQLAlchemy(app)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

def init_db():
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
        print(f"Database created at {db_path}")
    else:
        print(f"Database already exists at {db_path}")

@app.route('/24/get_events', methods=['GET'])
def get_events():
    bookings = Booking.query.all()
    
    #print(bookings)
    if not bookings:
        print("No bookings found in the database.")
    
    events = []
    for booking in bookings:
        events.append({
            'title': booking.name,
            'start': booking.start_time.isoformat(),
            'end': booking.end_time.isoformat()
        })
        #print(booking.name)
    return jsonify(events)

@app.route('/24/add_event', methods=['POST'])
def add_event():
    data = request.json
    name = data.get('title')
    start = datetime.fromisoformat(data.get('start'))
    end = datetime.fromisoformat(data.get('end'))
    
    new_booking = Booking(name=name, start_time=start, end_time=end)
    db.session.add(new_booking)
    db.session.commit()
    
    return jsonify({"status": "success", "id": new_booking.id})
    
@app.route('/24/')
def t24():
    #name = select_random_country()
    #data = get_country_data(name)
    data = jsonify([])
    return render_template('24.html', data=data)

#if __name__ == '__main__':
#    with app.app_context():
#        db.create_all()
#    app.run(debug=True)

if __name__ == '__main__':
    #with app.app_context():
    #    db.create_all()
    init_db()
    genai.configure(api_key=GEMINI_API_KEY)
    app.run(debug=False, host='0.0.0.0', port=5000)

# templates/calendar.html