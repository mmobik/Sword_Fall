"""
Скрипт для сборки исполняемого файла игры.

Этот скрипт использует PyInstaller для создания .exe файла из Python-приложения.
Включает все необходимые ресурсы и зависимости.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def build_exe():
    """Сборка исполняемого файла игры."""

    print("🎮 Начинаем сборку исполняемого файла...")

    # Очистка предыдущих сборок
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("game.spec"):
        os.remove("game.spec")

    # Команда PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",  # Один файл
        "--windowed",  # Без консольного окна
        "--name=Падение_Меча",  # Имя исполняемого файла
        "--icon=assets/images/icons/icon_1.jpg",  # Иконка
        "--add-data=assets;assets",  # Включить папку assets
        "--add-data=userdata;userdata",  # Включить папку userdata
        "--add-data=dialogues;dialogues",  # Включить папку dialogues
        "--hidden-import=pygame",  # Явно включить pygame
        "--hidden-import=pygame.mixer",  # Включить pygame.mixer
        "--hidden-import=json",  # Включить json
        "--hidden-import=time",  # Включить time
        "--hidden-import=os",  # Включить os
        "--hidden-import=sys",  # Включить sys
        "--hidden-import=pathlib",  # Включить pathlib
        "--clean",  # Очистить кэш
        "--noconfirm",  # Не спрашивать подтверждения
        "game.py"  # Главный файл
    ]

    try:
        # Запуск сборки
        print("🔨 Запуск PyInstaller...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Сборка завершена успешно!")

        # Проверка результата
        exe_path = Path("dist/Падение_Меча.exe")
        if exe_path.exists():
            print(f"🎉 Исполняемый файл создан: {exe_path}")
            print(f"📁 Размер файла: {exe_path.stat().st_size / (1024 * 1024):.1f} MB")
        else:
            print("❌ Исполняемый файл не найден!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сборке: {e}")
        print(f"Вывод ошибки: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

    return True


def create_installer():
    """Создание простого установщика."""

    print("\n📦 Создание установщика...")

    # Создание папки для установщика
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)

    # Копирование исполняемого файла
    exe_source = Path("dist/Падение_Меча.exe")
    exe_dest = installer_dir / "Падение_Меча.exe"

    if exe_source.exists():
        shutil.copy2(exe_source, exe_dest)
        print(f"✅ Исполняемый файл скопирован в {installer_dir}")

        # Создание README для установщика
        readme_content = """# Падение Меча - Установка

## Установка игры

1. Скопируйте файл "Падение_Меча.exe" в любую папку
2. Запустите файл двойным щелчком
3. Игра запустится автоматически

## Системные требования

- Windows 7/8/10/11
- Минимум 2 GB RAM
- 500 MB свободного места на диске

## Управление

- WASD - Движение
- E - Взаимодействие
- ESC - Меню
- Мышь - Навигация по меню

## Поддержка

При возникновении проблем обращайтесь к разработчику:
- VK: https://vk.com/sergeyoshepkov
- Email: Oshchepkov.Sergey@urfu.me

Удачной игры!
"""

        with open(installer_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)

        print("✅ README создан")
        print(f"📁 Установщик готов в папке: {installer_dir}")

    else:
        print("❌ Исполняемый файл не найден!")


if __name__ == "__main__":
    print("⚔️ Сборка игры 'Падение Меча'")
    print("=" * 50)

    # Сборка .exe
    if build_exe():
        # Создание установщика
        create_installer()
        print("\n🎉 Сборка завершена! Игра готова к распространению.")
    else:
        print("\n❌ Сборка не удалась. Проверьте ошибки выше.")
