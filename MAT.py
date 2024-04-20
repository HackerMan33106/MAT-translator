import os
import json
import aiohttp
import asyncio
from tqdm import tqdm
from collections import OrderedDict
from aiogoogletrans import Translator

async def translate_single(key, value, target_lang='ru'):
    try:
        # Проверяем, является ли строка уже переведенной
        if value.strip().startswith("Translated:"):
            return key, value
        
        # Если строка уже на русском, пропускаем ее
        if value.strip().startswith("$(br)"):
            return key, value
        
        # Разделяем ключ и значение символом "="
        key_parts = key.split("=")
        if len(key_parts) > 1:
            translated_key = key_parts[0].strip()
            untranslated_value = "=".join(key_parts[1:]).strip()
        else:
            translated_key = key.strip()
            untranslated_value = value.strip()

        translator = Translator()
        translated_value = await translator.translate(untranslated_value, target_lang)
        return translated_key, translated_value.text
    except Exception as e:
        print(f"Ошибка при переводе строки: {str(e)}")
        print(f"Строка, вызвавшая ошибку: {key}: {value}")
        return key, value

async def translate_json(filename, output_folder, target_lang='ru'):
    try:
        print("Начало перевода...")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_filename = os.path.join(output_folder, f"translated_{filename}")

        print(f"Загрузка файла {filename}...")
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file, object_pairs_hook=OrderedDict)

        translated_data = OrderedDict()
        tasks = []
        for key, value in data.items():
            tasks.append(translate_single(key, value, target_lang))

        with tqdm(total=len(tasks), position=0, leave=False) as progress_bar:
            for task in asyncio.as_completed(tasks):
                key, translated_value = await task
                translated_data[key] = translated_value
                progress_bar.update(1)

        print("Запись в файл...")
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            json.dump(translated_data, output_file, ensure_ascii=False, indent=4)

        print("Перевод завершен.")
        return output_filename
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден.")
        return None
    except Exception as e:
        print(f"Произошла ошибка при переводе: {str(e)}")
        return None

# Пример использования
filename = input("Введите имя файла: ")
output_folder = input("Введите имя папки для сохранения переведенного файла: ")

asyncio.run(translate_json(filename, output_folder))
