from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Секретный ключ для работы с сессиями

# Загружаем данные из CSV
df = pd.read_csv('data/music_data.csv')

# Заполнение пропусков в столбце 'tags' пустыми строками
df['tags'] = df['tags'].fillna('')

# Подготовка TF-IDF для рекомендаций
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['tags'])  # Используем 'tags' для векторизации

# Пример вывода размерности полученной матрицы
print(tfidf_matrix.shape)  # Выведет размерность полученной матрицы

# Функция для подключения к базе данных SQLite
def get_db_connection():
    conn = sqlite3.connect('data/music_recommendations.db')
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация базы данных
def init_db():
    with sqlite3.connect('data/music_recommendations.db') as conn:
        cursor = conn.cursor()
        # Таблица для пользователей
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE,
                            password TEXT)''')
        # Таблица для истории рекомендаций
        cursor.execute('''CREATE TABLE IF NOT EXISTS recommendations (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            track_title TEXT,
                            track_artist TEXT,
                            recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.commit()

init_db()

# Функция для получения истории рекомендаций пользователя
def get_recommendations_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recommendations WHERE user_id = ? ORDER BY recommended_at DESC', (user_id,))
    history = cursor.fetchall()
    conn.close()
    return history

# Главная страница
@app.route('/')
def index():
    if 'user_id' in session:
        # Загружаем историю рекомендаций для текущего пользователя
        recommendations_history = get_recommendations_history(session['user_id'])
        return render_template('index.html', recommendations_history=recommendations_history)  # Передаем историю рекомендаций
    return render_template('choose_login_or_register.html')  # Страница выбора, если не авторизован

# Регистрация пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return 'Пользователь с таким именем уже существует.'
        finally:
            conn.close()

    return render_template('register.html')

# Логин пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            return 'Неверное имя пользователя или пароль.'
    
    return render_template('login.html')

# Выход пользователя
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Рекомендации
@app.route('/recommend', methods=['POST'])
def recommend():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_input = request.form['preferences']
    selected_genre = request.form['genre']
    selected_mood = request.form['mood']

    # Вычисление сходства
    user_tfidf = vectorizer.transform([user_input])
    user_cosine_sim = cosine_similarity(user_tfidf, tfidf_matrix)

    # Сортировка по сходству
    sim_scores = list(enumerate(user_cosine_sim[0]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

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

            # Запись в историю рекомендаций
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO recommendations (user_id, track_title, track_artist) VALUES (?, ?, ?)', 
                           (session['user_id'], track['title'], track['artist']))
            conn.commit()
            conn.close()

            if len(recommendations) >= 3:  # Ограничим количество рекомендаций
                break

    return render_template('index.html', recommendations=recommendations)


if __name__ == '__main__':
    app.run(debug=True)
