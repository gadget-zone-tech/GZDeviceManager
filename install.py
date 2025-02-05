from win32com.client import Dispatch
import shutil, os



root_path = os.path.dirname(os.path.realpath(__file__))



print("")
print("Acquiring system information".ljust(40, "."), end='')
username       = os.getlogin()
install_folder = "C:\\Users\\" + username + "\\AppData\\Local\\Programs\\GZDeviceManager"
startup_folder = "C:\\Users\\" + username + "\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
print("done")

print("Copying files".ljust(40, "."), end='')
os.makedirs(install_folder,              exist_ok = True)
os.makedirs(install_folder + "\\tmp",    exist_ok = True)
os.makedirs(install_folder + "\\assets", exist_ok = True)
shutil.copy(root_path + "\\settings.py", install_folder)
shutil.copy(root_path + "\\config.ini",  install_folder)
shutil.copy(root_path + "\\main.pyw",    install_folder)
shutil.copytree(root_path + "\\assets\\",  install_folder + "\\assets",  dirs_exist_ok = True)
shutil.copytree(root_path + "\\devices",   install_folder + "\\devices", dirs_exist_ok = True)
print("done")

print("Creating startup shortcut".ljust(40, "."), end='')
shell    = Dispatch("WScript.Shell")
shortcut = shell.CreateShortcut(startup_folder + "\\GZDeviceManager.lnk")
shortcut.Targetpath = install_folder + "\\main.pyw"
shortcut.save()
print("done")

print("")
print("Instalation was successful! Press any key to exit.")
input()