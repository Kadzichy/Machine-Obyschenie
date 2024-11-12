import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecommenderSystem:
    def __init__(self):
        # Загрузка данных
        self.data = pd.read_csv('data/music_data.csv')
        self.data['features'] = self.data[['genre', 'artist', 'mood']].fillna('').agg(' '.join, axis=1)
        self.vectorizer = TfidfVectorizer()
        self.feature_matrix = self.vectorizer.fit_transform(self.data['features'])

    def get_recommendations(self, user_preferences):
        # Преобразуем предпочтения пользователя в вектор
        user_vec = self.vectorizer.transform([user_preferences])
        similarity = cosine_similarity(user_vec, self.feature_matrix)
        
        # Сортируем треки по сходству
        similar_indices = similarity[0].argsort()[::-1]
        recommendations = self.data.iloc[similar_indices[:5]]
        
        # Возвращаем список рекомендованных треков
        return recommendations[['title', 'artist']].to_dict(orient='records')
