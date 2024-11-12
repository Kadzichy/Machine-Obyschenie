from flask import Flask, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Загружаем и подготавливаем данные
df = pd.read_csv('data/music_data.csv')
# Удаление кавычек из столбца 'tags'
df['tags'] = df['tags'].str.replace('"', '', regex=False)
# Сохранение данных в новый CSV
df.to_csv('data/music_data_cleaned.csv', index=False)
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['tags'])

# Страница главного интерфейса
@app.route('/')
def index():
    return render_template('index.html')

# Страница рекомендаций
@app.route('/recommend', methods=['POST'])
def recommend():
    user_input = request.form['preferences']
    selected_genre = request.form['genre']
    selected_mood = request.form['mood']

    user_tfidf = vectorizer.transform([user_input])
    user_cosine_sim = cosine_similarity(user_tfidf, tfidf_matrix)

    # Сортируем треки по сходству
    sim_scores = list(enumerate(user_cosine_sim[0]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Фильтруем треки по жанру и настроению, если они выбраны
    recommendations = []
    for idx, score in sim_scores:
        track = df.iloc[idx]
        if (not selected_genre or track['genre'] == selected_genre) and \
           (not selected_mood or track['mood'] == selected_mood):
            recommendations.append({
                'title': track['title'],
                'artist': track['artist'],
                'year': track['year'],
                'album': track['album']
            })
            if len(recommendations) >= 3:  # Ограничение на 3 рекомендации
                break

    # Отправляем данные в шаблон
    return render_template('index.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
