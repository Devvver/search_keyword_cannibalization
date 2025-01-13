import streamlit as st
import pandas as pd

# Функция для анализа каннибализации ключевых запросов
def check_keyword_cannibalization(df, min_impressions):
    # Применяем фильтрацию по минимальному количеству показов
    df_filtered = df[df['Показы'] >= min_impressions]

    cannibalization_report = []

    # Проходим по каждому уникальному ключевому запросу
    for keyword in df_filtered['Ключевой запрос'].unique():
        urls = df_filtered[df_filtered['Ключевой запрос'] == keyword][['URL', 'Позиция']].values.tolist()

        # Проверяем, есть ли ключевое слово в нескольких URL
        if len(urls) > 1:
            clicks = df_filtered[df_filtered['Ключевой запрос'] == keyword]['Клики'].sum()
            impressions = df_filtered[df_filtered['Ключевой запрос'] == keyword]['Показы'].sum()
            avg_position = df_filtered[df_filtered['Ключевой запрос'] == keyword]['Позиция'].mean()

            # Для каждого набора URL добавляем его в отчет
            for i in range(len(urls) - 1):
                cannibalization_report.append({
                    'Ключевой запрос': keyword,
                    'URL1': urls[i][0],
                    'URL2': urls[i+1][0],
                    'Позиция 1': urls[i][1],
                    'Позиция 2': urls[i+1][1],
                    'Показы': impressions,
                })

    return cannibalization_report


# Streamlit интерфейс
st.title('Анализ каннибализации ключевых запросов')

st.markdown("""
    Загрузите CSV файл с результатами из Google Search Console для анализа каннибализации ключевых запросов.
    Программа проверит, повторяются ли ключевые запросы в разных URL и покажет количество кликов, показов и среднюю позицию.
""")

# Поле для ввода минимального количества показов (по умолчанию 100)
min_impressions = st.number_input('Минимальное количество показов', min_value=0, value=100, step=100)

# Загружаем CSV файл
uploaded_file = st.file_uploader("Загрузите CSV файл", type="csv")

if uploaded_file is not None:
    # Загружаем данные из CSV
    df = pd.read_csv(uploaded_file)

    # Проверка, что CSV содержит нужные столбцы
    required_columns = ['Ключевой запрос', 'URL', 'Клики', 'Показы', 'Позиция']
    if all(col in df.columns for col in required_columns):
        st.write("Данные успешно загружены.")

        # Анализ каннибализации
        cannibalization_report = check_keyword_cannibalization(df, min_impressions)

        # Выводим результаты анализа в таблице
        if cannibalization_report:
            cannibalization_df = pd.DataFrame(cannibalization_report)
            st.write("Результаты анализа каннибализации:")
            st.dataframe(cannibalization_df)
        else:
            st.write("Каннибализация ключевых запросов не обнаружена.")

        # Кнопка для экспорта результатов в новый CSV
        if st.button('Экспортировать результаты в CSV'):
            cannibalization_df.to_csv('cannibalization_report.csv', index=False)
            st.write("Результаты экспортированы в 'cannibalization_report.csv'.")
    else:
        st.error(f"CSV файл должен содержать столбцы: {', '.join(required_columns)}.")
