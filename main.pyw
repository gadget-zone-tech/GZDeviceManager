from PIL                     import Image
from settings                import Settings
from bleak                   import BleakScanner, BleakClient
import datetime, os, threading, time
import asyncio, logging
import guizero, pystray, ctypes



if __name__ == '__main__':
	root_path = os.path.dirname(os.path.realpath(__file__))
	if not(os.path.exists(root_path + "\\log")):
		os.mkdir(root_path + "\\log")
	if not(os.path.isfile(root_path + "\\log\\log.txt")):
		with open(root_path + "\\log\\log.txt", "w"):
			pass
	logging.basicConfig(
		filename = root_path + "\\log\\log.txt",
		format   = '%(asctime)s %(levelname)-8s %(message)s',
		level    = logging.INFO,
		datefmt  = '%Y-%m-%d %H:%M:%S'
	)
	logger = logging.getLogger(__name__)
	logger.info("Root level path is: {:s}".format(root_path))
	exit_flag       = False
	settings        = Settings()
	bt_flag         = False
	bt_messages_out = []
	bt_messages_in  = []


# BLUETOOTH SETUP
if __name__ == '__main__':
	def bt_manager():
		async def change_state(address, char_uuid, sign_state):
			async with BleakClient(address) as client:
				svcs = client.services
				#print("Set state: " + str(sign_state))
				await client.write_gatt_char(char_uuid, sign_state)
				time.sleep(0.25)
				battery_level = await client.read_gatt_char(char_uuid)
				return {
					"char_uuid"  : str(char_uuid),
					"value"      : battery_level,
					"action"     : None,
				}
		
		global settings
		while True:
			if not(exit_flag):
				for device in settings.claimed_devices:
					message = device.get_bt_message_out()
					if (message):
						logger.info("BLE message: " + str(message))
						try:
							result = asyncio.run(
								change_state(
									message["address"],
									message["char_uuid"],
									message["value"],
								)
							)
							device.set_bt_message_in(result)
							print(result)
							logger.info("BLE result: " + str(result))
						except BaseException as error:
							print(error)
							logger.error(error)
			else:
				break
			time.sleep(0.1)


# GUIZERO SETUP
if __name__ == '__main__':
	app_id = "GZDeviceManager"
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
	
	app = guizero.App(
		title = "GZDeviceManager",
		visible = False
	)	
	app.tk.iconbitmap(os.path.dirname(os.path.realpath(__file__)) + "\\assets\\gz_64.ico")

	def app_exit_check():
		global exit_flag
		if (exit_flag):
			exit()
	app.repeat(1000, app_exit_check)

	def app_exit():
		global exit_flag
		exit_flag = True
		exit()
	app.when_closed = app_exit

	app.icon = root_path + '\\assets\\gz_64.ico'

	for claimed_device in settings.claimed_devices:
		if (claimed_device.update_interval > 0):
			app.repeat(
				claimed_device.update_interval,
				claimed_device.update,
			)


# SYSTEM TRAY MENU SETUP
if __name__ == '__main__':
	def on_click_manager(icon, item):
		settings.window(app)

	def on_click_exit(icon, item):
		global exit_flag
		exit_flag = True
		icon.stop()

	menu_items = [
		pystray.Menu.SEPARATOR,
		pystray.MenuItem(
			'Manager',
			on_click_manager
		),
		pystray.MenuItem(
			'Exit',
			on_click_exit,
		)
	]
	for claimed_device in settings.claimed_devices:
		menu_items[:0] = [claimed_device.stray()]

	icon = pystray.Icon(
		'test name',
		icon = Image.open(
			root_path + '\\assets\\gz_64.ico'
		),
		menu = pystray.Menu(*menu_items)
	)


# START
if __name__ == '__main__':
	threading.Thread(target=icon.run).start()
	threading.Thread(target=bt_manager).start()
	if (settings.update_required):
		pystray.Icon.notify("New version of GZDeviceManager is available!")
	app.display()