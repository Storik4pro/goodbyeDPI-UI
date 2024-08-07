import os
import shutil
import ctypes
import winreg

def install_font(font_path):
    try:
        # Копирование шрифта в системную папку шрифтов
        font_name = os.path.basename(font_path)
        dest_path = os.path.join(os.environ['WINDIR'], 'Fonts', font_name)
        shutil.copyfile(font_path, dest_path)

        # Регистрация шрифта в реестре
        reg_path = r'Software\Microsoft\Windows NT\CurrentVersion\Fonts'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, 'Nunito SemiBold (TrueType)', 0, winreg.REG_SZ, font_name)

        # Обновление кеша шрифтов
        ctypes.windll.gdi32.AddFontResourceW(dest_path)
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x001D, 0, 0)

        print("Шрифт успешно установлен.")
    except Exception as e:
        print(f"Ошибка при установке шрифта: {e}")

