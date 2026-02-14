"""
Скрипт для обработки изображений: обрезка белого фона, удаление черного и белого фона, изменение размера до 103x132
"""
import os
from PIL import Image
import numpy as np

def crop_white_background(image):
    """
    Обрезает белый фон по краям изображения.
    Определяет белые пиксели и обрезает до первого небелого пикселя с каждой стороны.
    """
    # Конвертируем в RGB если нужно
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Преобразуем в numpy массив
    data = np.array(image)
    
    # Определяем белые пиксели (RGB близко к 255,255,255)
    # Порог для определения белого цвета (можно настроить)
    white_threshold = 240  # Пиксели с яркостью выше этого считаются белыми
    r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]
    
    # Белый пиксель: все каналы должны быть выше порога
    is_white = (r >= white_threshold) & (g >= white_threshold) & (b >= white_threshold)
    
    # Находим границы: ищем первую строку/столбец, где есть небелые пиксели
    height, width = is_white.shape
    
    # Верхняя граница
    top = 0
    for y in range(height):
        if not np.all(is_white[y, :]):  # Если в строке есть небелые пиксели
            top = y
            break
    
    # Нижняя граница
    bottom = height
    for y in range(height - 1, -1, -1):
        if not np.all(is_white[y, :]):
            bottom = y + 1
            break
    
    # Левая граница
    left = 0
    for x in range(width):
        if not np.all(is_white[:, x]):
            left = x
            break
    
    # Правая граница
    right = width
    for x in range(width - 1, -1, -1):
        if not np.all(is_white[:, x]):
            right = x + 1
            break
    
    # Обрезаем изображение
    if top < bottom and left < right:
        cropped = image.crop((left, top, right, bottom))
        return cropped
    
    return image

def remove_background(image):
    """
    Удаляет белый и черный фон, делая их прозрачными.
    Использует аккуратные пороги, чтобы не задеть предметы.
    """
    # Конвертируем в RGBA
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    data = np.array(image)
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    
    # Определяем белые пиксели (RGB близко к 255,255,255)
    # Используем более строгий порог для белого, чтобы не задеть светлые части предметов
    white_threshold = 250  # Только очень белые пиксели
    is_white = (r >= white_threshold) & (g >= white_threshold) & (b >= white_threshold)
    
    # Определяем черные пиксели (RGB близко к 0,0,0)
    # Используем более строгий порог для черного, чтобы не задеть темные части предметов
    black_threshold = 10  # Только очень черные пиксели
    is_black = (r <= black_threshold) & (g <= black_threshold) & (b <= black_threshold)
    
    # Объединяем маски фона
    is_background = is_white | is_black
    
    # Делаем фон прозрачным
    data[:, :, 3] = np.where(is_background, 0, 255)
    
    return Image.fromarray(data)

def resize_to_target(image, target_width, target_height):
    """
    Изменяет размер изображения до целевого размера с сохранением пропорций.
    Добавляет прозрачный фон если нужно.
    """
    # Конвертируем в RGBA для поддержки прозрачности
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Вычисляем масштаб для вписывания в целевой размер
    img_width, img_height = image.size
    scale_w = target_width / img_width
    scale_h = target_height / img_height
    scale = min(scale_w, scale_h)
    
    # Новый размер с сохранением пропорций
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    
    # Изменяем размер
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Создаем новое изображение с целевым размером и прозрачным фоном
    result = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
    
    # Центрируем изображение
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    
    result.paste(resized, (x_offset, y_offset), resized)
    
    return result

def process_image(input_path, output_path, target_width=103, target_height=132):
    """
    Обрабатывает одно изображение: обрезает белый фон, удаляет черный и белый фон, изменяет размер.
    """
    try:
        # Загружаем изображение
        img = Image.open(input_path)
        original_size = img.size
        print(f"Обработка: {os.path.basename(input_path)} ({original_size[0]}x{original_size[1]})")
        
        # Шаг 1: Обрезаем белый фон по краям
        img_cropped = crop_white_background(img.copy())
        cropped_size = img_cropped.size
        print(f"  Обрезано до: {cropped_size[0]}x{cropped_size[1]}")
        
        # Шаг 2: Удаляем белый и черный фон (делаем прозрачным)
        img_no_bg = remove_background(img_cropped)
        print(f"  Фон удален (белый и черный)")
        
        # Шаг 3: Изменяем размер до целевого с сохранением пропорций
        img_final = resize_to_target(img_no_bg, target_width, target_height)
        
        # Сохраняем
        img_final.save(output_path, 'PNG')
        print(f"  ✓ Сохранено: {os.path.basename(output_path)} ({target_width}x{target_height})")
        
    except Exception as e:
        print(f"  ✗ Ошибка при обработке {input_path}: {e}")
        import traceback
        traceback.print_exc()

def main():
    # Пути
    input_dir = r"C:\Users\hak18\OneDrive\Desktop\projects\Sword_Fall\Game\assets\Новая папка (3)"
    output_dir = r"C:\Users\hak18\OneDrive\Desktop\projects\Sword_Fall\Game\assets\Items\processed"
    
    # Создаем выходную папку если её нет
    os.makedirs(output_dir, exist_ok=True)
    
    # Обрабатываем все PNG файлы
    png_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]
    png_files.sort(key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else 0)
    
    print(f"Найдено {len(png_files)} изображений для обработки\n")
    
    for filename in png_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        process_image(input_path, output_path)
    
    print(f"\n✓ Обработка завершена! Результаты сохранены в: {output_dir}")

if __name__ == "__main__":
    main()

