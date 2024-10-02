from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
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

    
        data = {
            'title': title,
            'author': author,
            'narrator': narrator_text,
            'length': length,
            'rating': rating,
            'category': category_text
        }
        return render_template('index.html', data=data)

    return render_template('index.html', data=None)

if __name__ == '__main__':
    app.run(debug=True)
