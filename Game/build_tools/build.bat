@echo off
chcp 65001 >nul
echo ⚔️ Сборка игры "Падение Меча"
echo ================================================

echo.
echo 🎮 Запуск сборки...
cd ..
python build_tools\build_exe.py

echo.
echo 📁 Проверка результата...
if exist "dist\Падение_Меча.exe" (
    echo ✅ Исполняемый файл создан успешно!
    echo 📂 Расположение: dist\Падение_Меча.exe
    echo.
    echo 🎉 Сборка завершена! Игра готова к распространению.
) else (
    echo ❌ Ошибка при создании исполняемого файла!
    echo Проверьте сообщения об ошибках выше.
)

echo.
pause 