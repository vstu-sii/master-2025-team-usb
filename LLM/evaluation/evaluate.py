import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from rapidfuzz import fuzz
import re


class DatasetValidator:
    def __init__(self, semantic_threshold=0.3, fuzzy_threshold=60):
        self.semantic_threshold = semantic_threshold  # Понижаем порог для семантического сходства
        self.fuzzy_threshold = fuzzy_threshold
        # Загружаем модель для семантического сравнения категорий
        self.model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased')

    def load_data(self, true_data_path, pred_data_path):
        """Загрузка данных из JSON файлов"""
        with open(true_data_path, 'r', encoding='utf-8') as f:
            true_data = json.load(f)
        with open(pred_data_path, 'r', encoding='utf-8') as f:
            pred_data = json.load(f)
        return true_data, pred_data

    def compare_numerical(self, true_val, pred_val, tolerance=0.3):
        """Сравнение числовых значений с допуском"""
        if true_val == 0:
            return pred_val == 0
        return abs(true_val - pred_val) / true_val <= tolerance

    def normalize_text(self, text):
        """Нормализация текста для сравнения"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)  # Удаляем пунктуацию
        return text

    def compare_category_semantic(self, true_cat, pred_cat):
        """Семантическое сравнение категорий с либеральным подходом"""
        # Сначала проверяем точное совпадение после нормализации
        norm_true = self.normalize_text(true_cat)
        norm_pred = self.normalize_text(pred_cat)

        if norm_true == norm_pred:
            return True

        # Проверяем частичное вхождение
        if norm_true in norm_pred or norm_pred in norm_true:
            return True

        # Fuzzy matching
        fuzzy_score = fuzz.token_sort_ratio(norm_true, norm_pred)
        if fuzzy_score >= self.fuzzy_threshold:
            return True

        # Семантическое сходство (как последний вариант)
        try:
            true_embedding = self.model.encode([true_cat])
            pred_embedding = self.model.encode([pred_cat])
            similarity = cosine_similarity(true_embedding, pred_embedding)[0][0]
            return similarity >= self.semantic_threshold
        except:
            return False

    def calculate_semantic_similarity_score(self, true_cat, pred_cat):
        """Вычисление семантического сходства как числовой оценки"""
        try:
            true_embedding = self.model.encode([true_cat])
            pred_embedding = self.model.encode([pred_cat])
            similarity = cosine_similarity(true_embedding, pred_embedding)[0][0]
            return float(similarity)
        except:
            return 0.0

    def calculate_fuzzy_score(self, true_cat, pred_cat):
        """Вычисление fuzzy matching score"""
        return fuzz.token_sort_ratio(true_cat, pred_cat) / 100.0

    def validate_datasets(self, true_data, pred_data):
        """Основная функция валидации"""
        if len(true_data) != len(pred_data):
            raise ValueError("Датасеты должны иметь одинаковую длину")

        results = {
            'calories_accuracy': [],
            'protein_accuracy': [],
            'fats_accuracy': [],
            'carb_accuracy': [],
            'lac_int_accuracy': [],
            'category_accuracy': [],  # Бинарная accuracy категорий
            'category_semantic_score': [],  # Числовая оценка семантического сходства
            'category_fuzzy_score': [],  # Числовая оценка fuzzy matching
        }

        for true_item, pred_item in zip(true_data, pred_data):
            # Проверка числовых полей
            results['calories_accuracy'].append(
                self.compare_numerical(true_item['calories'], pred_item['calories'])
            )
            results['protein_accuracy'].append(
                self.compare_numerical(true_item['protein'], pred_item['protein'])
            )
            results['fats_accuracy'].append(
                self.compare_numerical(true_item['fats'], pred_item['fats'])
            )
            results['carb_accuracy'].append(
                self.compare_numerical(true_item['carb'], pred_item['carb'])
            )

            # Проверка lac_int (строгое совпадение)
            results['lac_int_accuracy'].append(
                true_item['lac_int'] == pred_item['lac_int']
            )

            # Проверка категории
            category_match = self.compare_category_semantic(
                true_item['category'], pred_item['category']
            )
            results['category_accuracy'].append(category_match)

            # Числовые оценки для категорий
            results['category_semantic_score'].append(
                self.calculate_semantic_similarity_score(
                    true_item['category'], pred_item['category']
                )
            )
            results['category_fuzzy_score'].append(
                self.calculate_fuzzy_score(true_item['category'], pred_item['category'])
            )

        # Вычисляем итоговые метрики
        metrics = {
            'calories_accuracy': np.mean(results['calories_accuracy']),
            'protein_accuracy': np.mean(results['protein_accuracy']),
            'fats_accuracy': np.mean(results['fats_accuracy']),
            'carb_accuracy': np.mean(results['carb_accuracy']),
            'lac_int_accuracy': np.mean(results['lac_int_accuracy']),
            'category_accuracy': np.mean(results['category_accuracy']),
            'category_semantic_score': np.mean(results['category_semantic_score']),
            'category_fuzzy_score': np.mean(results['category_fuzzy_score']),
            'overall_numerical_accuracy': np.mean([
                np.mean(results['calories_accuracy']),
                np.mean(results['protein_accuracy']),
                np.mean(results['fats_accuracy']),
                np.mean(results['carb_accuracy'])
            ]),
            'overall_accuracy': np.mean([
                np.mean(results['calories_accuracy']),
                np.mean(results['protein_accuracy']),
                np.mean(results['fats_accuracy']),
                np.mean(results['carb_accuracy']),
                np.mean(results['lac_int_accuracy']),
                np.mean(results['category_accuracy'])
            ])
        }

        return metrics, results


def main():
    # Пример использования
    validator = DatasetValidator(semantic_threshold=0.3, fuzzy_threshold=60)

    # Загрузка данных (замените пути на ваши файлы)
    true_data, pred_data = validator.load_data('../data/FoodData_test.json', 'FoodData_answers.json')

    # Валидация
    metrics, detailed_results = validator.validate_datasets(true_data, pred_data)

    print("=== МЕТРИКИ КАЧЕСТВА ===")
    print(f"Accuracy calories: {metrics['calories_accuracy']:.3f}")
    print(f"Accuracy protein: {metrics['protein_accuracy']:.3f}")
    print(f"Accuracy fats: {metrics['fats_accuracy']:.3f}")
    print(f"Accuracy carb: {metrics['carb_accuracy']:.3f}")
    print(f"Общая accuracy числовых полей: {metrics['overall_numerical_accuracy']:.3f}")
    print(f"Accuracy lac_int: {metrics['lac_int_accuracy']:.3f}")
    print(f"Accuracy категорий: {metrics['category_accuracy']:.3f}")
    print(f"Семантическое сходство категорий (среднее): {metrics['category_semantic_score']:.3f}")
    print(f"Fuzzy similarity категорий (среднее): {metrics['category_fuzzy_score']:.3f}")
    print(f"ОБЩАЯ ACCURACY: {metrics['overall_accuracy']:.3f}")

    # Детальные результаты по каждому элементу
    print("\n=== ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ (первые 5) ===")
    for i in range(min(5, len(true_data))):
        print(f"Элемент {i + 1}:")
        print(f"  Категория (истина): {true_data[i]['category']}")
        print(f"  Категория (предсказание): {pred_data[i]['category']}")
        print(f"  Calories: {detailed_results['calories_accuracy'][i]}")
        print(f"  Protein: {detailed_results['protein_accuracy'][i]}")
        print(f"  Fats: {detailed_results['fats_accuracy'][i]}")
        print(f"  Carb: {detailed_results['carb_accuracy'][i]}")
        print(f"  Lac_int: {detailed_results['lac_int_accuracy'][i]}")
        print(f"  Category match: {detailed_results['category_accuracy'][i]}")
        print(f"  Category semantic: {detailed_results['category_semantic_score'][i]:.3f}")
        print(f"  Category fuzzy: {detailed_results['category_fuzzy_score'][i]:.3f}")
        print()


if __name__ == "__main__":
    main()
