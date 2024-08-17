import ctypes
import sys
import time
import winpty

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
else:
    def run_goodbyeDPI():
        command = ['E:\ByeDPI\data/goodbyeDPI/x86_64/goodbyedpi.exe', '-9']

        pty = winpty.PtyProcess.spawn(command)
        output = ""

        while True:
            try:
                data = pty.read(1024)
                if not data:
                    break
                output += data
                print(data, end="") 
                break
            except EOFError:
                break

        with open("goodbyedpi_output.log", "w") as logfile:
            logfile.write(output)

        print("Process finished.")

    run_goodbyeDPI()

print('end')
time.sleep(1000)