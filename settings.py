from devices.DND_sign        import DND_sign
import guizero, requests, configparser
import zipfile, os, serial, time, json
import shutil, sys, logging
import serial.tools.list_ports as list_ports



class Settings:
	update_required = False
	config          = configparser.ConfigParser()
	claimed_devices = []
	_version        = None
	_subversion     = None
	_revision       = None
	_device_list    = None
	_version        = None
	_window         = None
	_devices_box    = None
	_logger         = None

	def __init__(self):
		self._logger = logging.getLogger(__name__)
		self.config.read(
			os.path.dirname(os.path.realpath(__file__)) + "\\config.ini"
		)
		temp             = self.config["settings"]["version"].split(".")
		self._version    = int(temp[0])
		self._subversion = int(temp[1])
		self._revision   = int(temp[2])
		self._logger.info(
			"Settings from \"config.ini\" file loaded"
		)
		
		root_path = os.path.dirname(os.path.realpath(__file__))
		if os.path.isfile(root_path + "\\devices.json"):
			with open(root_path + "\\devices.json") as d_f:
				devices = json.load(d_f)
				for device in devices:
					self.add_device(device)
			self._logger.info(
				"Saved devices loaded from \"devices.json\""
			)
		else:
			with open(root_path + "\\devices.json", "w") as d_f:
				json.dump({}, d_f)
			self._logger.info(
				"File \"devices.json\" was not found and new file was created"
			)
		
		try:
			response = requests.get(
				self.config["settings"]["update_url"]
			)
			if (response.status_code == 200):
				response_j = response.json()
				version    = int(response_j["name"].split(".")[0])
				subversion = int(response_j["name"].split(".")[1])
				revision   = int(response_j["name"].split(".")[2])
				if ((version > self._version) or 
					(subversion > self._subversion) or 
					(revision > self._revision)):
					update_required = True
		except Exception as exc:
			print(exc)
	
	def add_device(self, info):
		if (info["name"] == "DND_sign"):
			self.claimed_devices.append(
				DND_sign(
					info["name"],
					info["gzidn"],
					info['settings'],
				)
			)
			print(self.claimed_devices[0].get_settings())

	def on_click(self):
		pass

	def _on_click_search(self):
		com_ports = list_ports.comports()
		for port in com_ports:
			ser_port  = serial.Serial(
				port     = port.name,
				baudrate = 115200,
				timeout  = 0.5,
			)
			print(str(port.device) + " - " + str(port.location) + " - " + str(port.manufacturer))
			response = None
			try:
				ser_port.write("GZ-GET-INFO\n".encode('utf-8'))
				time.sleep(0.1)
				response = ser_port.read_until(expected='\n').decode('utf-8')
			except Exception as err:
				print(err)
			if (response):
				info = json.loads(response.split("-")[-1])
				is_claimed = False
				for device in self.claimed_devices:
					if (device.get_gzidn() == info["gzidn"]):
						is_claimed = True
				print(info)
				if not(is_claimed):
					print(info)
					data = {}
					data["name"]                   = info["name"]
					data["gzidn"]                  = info["gzidn"]
					if (info["name"] == "DND_sign"):
						data["settings"]               = {}
						data["settings"]["bt_address"] = info["bt_address"]
						data["settings"]["brightness"] = self.config["devices.DND_sign"]["default_brightness"]
						self.add_device(data)
					self._devices_box.update()

	def on_click_update(self):
		response = requests.get(self.config["settings"]["update_url"])
		if (response.status_code == 200):
			download = requests.get(response.json()["zipball_url"])
			with open(os.path.dirname(os.path.realpath(__file__)) + '//tmp//update.tar.gz', 'wb') as temp_file:
				temp_file.write(download.content)
				with zipfile.ZipFile(temp_file.name) as zip_file:
					zip_file.extractall(os.path.dirname(os.path.realpath(__file__)) + "//tmp//")
		try:
			os.system(
				"start cmd.exe @cmd /k \'{:s}\'".format(
					os.path.dirname(os.path.realpath(__file__)) + "//tmp//install.bat"
				)
			)
			shutil.rmtree(
				os.path.dirname(os.path.realpath(__file__)) + "//tmp//"
			)
			os.mkdir(
				os.path.dirname(os.path.realpath(__file__)) + "//tmp//"
			)
			os.execl(sys.executable, sys.executable, *sys.argv)
		except Exception as err:
			print(err)

	def _check_connections(self):
		pass

	def _on_window_close(self):
		self.save()
		self._window.destroy()

	def window(self, app):
		self._window = guizero.Window(
			app,
			height  = 650,
			width   = 1200,
			visible = False,
			title   = "GZDeviceManager"
		)
		self._window.repeat(5000, self._check_connections)
		self._window.when_closed = self._on_window_close
		
		self._window.icon = os.path.dirname(os.path.realpath(__file__)) + '//assets//gz_64.ico'
		
		button_box = guizero.Box(
			self._window,
			align  = "left",
			height = "fill",
			width  = 250,
			border = 0
		)
		
		guizero.Text(
			button_box,
			text   = "",
			height = 1,
			width  = 25
		)
		
		search_button = guizero.PushButton(
			button_box,
			text    = "Search for Devices",
			command = self._on_click_search,
			height  = 2,
			width   = 25,
		) 
		
		guizero.Text(
			button_box,
			text   = "",
			height = 1,
			width  = 25
		)
		
		guizero.PushButton(
			button_box,
			text    = "Update Device Firmware",
			enabled = False,
			command = self.on_click_update,
			height  = 2,
			width   = 25,
		)
		
		guizero.Text(
			button_box,
			text   = "",
			height = 1,
			width  = 25
		)
		
		guizero.PushButton(
			button_box,
			text    = "Update Device Manager",
			enabled = self.update_required,
			command = self.on_click_update,
			height  = 2,
			width   = 25,
		) 
		
		guizero.Text(
			button_box,
			text   = "",
			height = 1,
			width  = 25
		)
		
		guizero.PushButton(
			button_box,
			text    = "Save Manager Settings",
			enabled = False,
			command = self.on_click_update,
			height  = 2,
			width   = 25,
		)

		settings_box = guizero.TitleBox(
			self._window,
			"Manager Settings",
			align  = "right",
			height = "fill",
			width  = 500,
			border = 1
		)
		
		self._devices_box = guizero.TitleBox(
			self._window,
			"Devices",
			align  = "left",
			height = "fill",
			width  = "fill",
			border = 1
		)

		def update_devices_box():
			def on_mouse_enter(event_data):
				event_data.widget.border = 3
		
			def on_mouse_leave(event_data):
				event_data.widget.border = 1

			for child in self._devices_box.children:
				if isinstance(child, guizero.Box):
					child.destroy()

			for device in self.claimed_devices:
				device_box = guizero.Box(
					self._devices_box,
					height = 50,
					width  = "fill"
				)
				device_box.bg                = "red"
				device_box.border            = 0
				device_box.when_mouse_enters = on_mouse_enter
				device_box.when_mouse_leaves = on_mouse_leave
				button_remove = guizero.PushButton(
					device_box,
					align   = "right",
					text    = "R",
					enabled = False,
					args    = (app,)
				)
				button_remove.bg = None
				button_settings = guizero.PushButton(
					device_box,
					align   = "right",
					text    = "Settings",
					command = device.window,
					args    = (app,)
				)
				button_settings.bg = None
				guizero.Text(
					device_box,
					text    = device.get_name() + " (" + device.get_gzidn() + ")",
					align   = "left",
				)

		self._devices_box.update = update_devices_box

		guizero.Text(
			self._devices_box,
			align  = "bottom",
			text   = "",
			height = 1,
			width  = 25
		)
		update_devices_box()
		self._window.visible = True
	
	def save(self):
		settings = []
		for device in self.claimed_devices:
			device_settings = {}
			device_settings["name"]     = device.get_name()
			device_settings["gzidn"]    = device.get_gzidn()
			device_settings["settings"] = device.get_settings()
			settings.append(device_settings)
		self._logger.info(
			"Saved following data to \"devices.json\" file: {:s}". format(str(settings))
		)
		print(settings)
		with open(os.path.dirname(os.path.realpath(__file__)) + "\\devices.json", "w") as d_f:
			d_f.write(
				json.dumps(
					settings,
					indent = 4
				)
			)