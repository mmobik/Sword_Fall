# Build Tools

Инструменты для сборки игры "Падение Меча" в исполняемый файл.

## Файлы

- **build_exe.py** - Основной скрипт сборки с помощью PyInstaller
- **build.bat** - Batch-файл для быстрого запуска сборки

## Использование

### Через Python:
```bash
python build_exe.py
```

### Через batch-файл:
```bash
build.bat
```

## Результат

После сборки в корне проекта появится папка `installer/` с готовой игрой:
- `Падение_Меча.exe` - исполняемый файл игры
- `README.txt` - инструкции по установке

## Требования

- Python 3.9+
- Pygame
- PyInstaller
- Pillow (для обработки иконок) 