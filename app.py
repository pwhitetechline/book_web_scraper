from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Gsq:OW493iJau%Hvf>4m-Wsh16~Atp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    author = db.Column(db.String(250), nullable=True)
    narrator = db.Column(db.String(250), nullable=True)
    length = db.Column(db.String(100), nullable=True)
    rating = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(250), nullable=True)
    notes = db.Column(db.String(500), nullable=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        data = scrape_data(url)
        session['data'] = data
        return render_template('display.html', data=data)
    return render_template('index.html')

@app.route('/add_to_database', methods=['POST'])
def add_to_database():
    data = session.get('data', None)
    if data:
        new_book = Book(**data)
        db.session.add(new_book)
        db.session.commit()
        session.pop('data', None)  # Clear the data from session
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    books = Book.query.all()
    return render_template('dashboard.html', books=books)

def scrape_data(url):
       response = requests.get(url)
       soup = BeautifulSoup(response.content, 'html.parser')
       # Extracting the title
       title_tag = soup.find('h1', class_='bc-heading bc-color-base bc-size-large bc-text-bold')
       title = title_tag.get_text(strip=True) if title_tag else "N/A"
        
        # Extracting the author
       author_tag = soup.find('li', class_='bc-list-item authorLabel')
       author = author_tag.find('a').get_text(strip=True) if author_tag else "N/A"

        # Extracting the narrator
       narrator_tag = soup.find('li', class_='bc-list-item narratorLabel')
       narrator_link = narrator_tag.find_all('a')
        # narrator_list = [narrator_link.get_text(strip=True) for narrator in narrator_link]
       narrator_text = ', '.join([narrator.get_text(strip=True) for narrator in narrator_link])

        # Extracting the length
       length_tag = soup.find('li', class_='bc-list-item runtimeLabel')
       length = length_tag.get_text(strip=True).replace('Length:', '').strip() if length_tag else "N/A"

        # Extracting the rating (approximated by counting full stars)
       rating_tag = soup.find('span', class_='bc-text', string=lambda s: s and "out of 5 stars" in s)
       rating = rating_tag.next_element.get_text(strip=True) if rating_tag else "N/A"

       category_tag = soup.find_all('span', class_='bc-chip-text')
        # Using list comprehension to create the list
       category_list = [categoryTag.get_text(strip=True) for categoryTag in category_tag]

        # Join the list items into a single string, separated by commas (or any separator you choose)
       category_text = ', '.join(category_list)
       return {
            'title': title,
            'author': author,
            'narrator': narrator_text,
            'length': length,
            'rating': rating,
            'category': category_text,
            'notes': 'Example Notes'
        }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

