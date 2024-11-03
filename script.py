import os
import requests
import pandas as pd
import openai
from datetime import datetime
from IPython.display import display

TOKEN_USER = ''
VERSION = '5.199'
DOMAIN = ''
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

files_to_remove = ['vk_analysis_notebook.ipynb']

for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
        print(f"Удален старый файл: {file}")

response = requests.get(
    'https://api.vk.com/method/wall.get',
    params={
        'access_token': TOKEN_USER,
        'v': VERSION,
        'domain': DOMAIN,
        'count': 150,
        'filter': 'owner'
    }
)

data = response.json().get('response', {}).get('items', [])
display(data)

def classify_post_with_openai(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a useful assistant, trained to classify VK posts by category, if there is no text, then use it as a photo or video: мем, новость, реклама, фото, видео, гифка, репост."},
            {"role": "user", "content": f"К какой категории относится следующий пост: '{text}'?"}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

post_category_list = []
post_date_list = []
post_link_list = []

for post in data:
    post_text = post.get('text', '')
    post_category = classify_post_with_openai(post_text)

    post_category_list.append(post_category)
    post_date_list.append(datetime.fromtimestamp(post['date']))
    post_link_list.append(f"https://vk.com/{DOMAIN}?w=wall{post['from_id']}_{post['id']}")

df_categories = pd.DataFrame({
    'date': post_date_list,
    'category': post_category_list,
    'link': post_link_list
})

display(df_categories)

notebook_content = f"""
# Анализ типов постов в VK

## Данные
Данный ноутбук содержит анализ постов со стены ВКонтакте.

### Результаты анализа:
{df_categories.to_markdown(index=False)}
"""

notebook_filename = 'vk_analysis_notebook.ipynb'
with open(notebook_filename, 'w', encoding='utf-8') as f:
    f.write(notebook_content)

print(f"Данные успешно сохранены в {notebook_filename}")

exit()
