from threading    import Lock
import os, datetime, pystray, guizero, logging


class DND_sign:
	_bt_address       = None
	_selected         = "MS Teams"
	_msteams_status   = None
	sign_state        = b'0'
	_set_state        = b'0'
	_brightness       = 0           # 0-100
	bt_messages_out   = []
	bt_messages_in    = []
	bt_lock_out       = Lock()
	bt_lock_in        = Lock()
	update_interval   = 5000
	_bt_grace_counter = 0
	_update_counter   = 0
	_name             = ""
	_gzidn            = ""
	_firmware_version = None
	_window           = None


	def __init__(self, name, gzidn, settings):
		self._name       = name
		self._gzidn      = gzidn
		self._bt_address = settings["bt_address"]
		self._brightness = settings["brightness"]

	def update(self):
		self._update_counter += 1
		if ((self._update_counter >= 1) and (self._bt_grace_counter > 0)):
			self._bt_grace_counter -= 1
		if ((self._update_counter >= 1) and (self._bt_grace_counter == 0)):
			if (self._selected == "MS Teams"):
				self._msteams_status = self._get_status_locally()
				ms_tams_states = ["Busy", "DoNotDisturb"]
				if (self._msteams_status in ms_tams_states):
					self._set_state = bytearray(str(self._brightness), "utf-8")
				else:
					self._set_state = b'0'

			if (self._selected == "On"):
				self._set_state = bytearray(str(self._brightness), "utf-8")

			if (self._selected == "Off"):
				self._set_state = b'0'

			if not(self._set_state == self.sign_state):
				with self.bt_lock_out:
					self.bt_messages_out.append(
						{
							"address"   : self._bt_address,
							"char_uuid" : "19b10002-e8f2-537e-4f6c-d104768a1214",
							"value"     : self._set_state,
							"action"    : "set"
						}
					)
					self._bt_grace_counter = 3
			
			if (len(self.bt_messages_in)>0):
				with self.bt_lock_in:
					message             = self.bt_messages_in[0]
					self.bt_messages_in = self.bt_messages_in[1:]
					self.sign_state     = message["value"]
		
		if (self._update_counter >= 5):
			self._update_counter = 1
			self.get_device_status()

	def stray(self):
		return pystray.MenuItem(
			"DND_sign",
			pystray.Menu(
				pystray.MenuItem(
					"On",
					self._on_click_set_state,
					checked = self._is_state
				),
				pystray.MenuItem(
					"MS Teams",
					self._on_click_set_state,
					checked = self._is_state
				),
				pystray.MenuItem(
					"Off",
					self._on_click_set_state,
					checked = self._is_state
				),
			),
		)
	
	def get_name(self):
		return self._name

	def get_gzidn(self):
		return self._gzidn
	
	def get_settings(self):
		settings = {}
		settings["bt_address"] = self._bt_address
		settings["brightness"] = self._brightness
		return settings

	def _on_click_set_state(self, icon, item):
		self._selected = item.text
	
	def _is_state(self, item):
		if (item.text == self._selected):
			return True
		else:
			return False

	def set_brightness(self, brightness):
		self._brightness = brightness

	def get_device_status(self):
		pass

	def get_bt_message_out(self):
		if (len(self.bt_messages_out)>0):
			with self.bt_lock_out:
				message              = self.bt_messages_out[0]
				self.bt_messages_out = self.bt_messages_out[1:]
			return message
		else:
			return None

	def set_bt_message_in(self, message):
		with self.bt_lock_in:
			self.bt_messages_in.append(message)
		return True
		
	def _get_todays_log_files(self, username):
		if not(type(username)==str):
			raise Exception("Argument \'username\' must by of type string!")

		today     = str(datetime.date.today())
		files     = os.listdir('C:/Users/' + username + '/AppData/Local/Packages/MSTeams_8wekyb3d8bbwe/LocalCache/Microsoft/MSTeams/Logs')
		files_f   = list(map(lambda x: x.split("_")[2].strip(".log"), filter(lambda x: ("MSTeams_"  + today) in x, files)))
		yesterday = today
		if (len(files_f) == 0):
			for i in range(1,15,1):
				yesterday   = str(datetime.date.today()-datetime.timedelta(days=i))
				files_f     = list(map(lambda x: x.split("_")[2].strip(".log"), filter(lambda x: ("MSTeams_"  + yesterday) in x, files)))
				if not(len(files_f) == 0):
					break
				
			
		if (len(files_f)>0):
			sorted_files = [files_f[0]]
			for x in files_f:
				t        = x.split(".")[0]
				t_s      = t.split("-")
				hour     = int(t.split("-")[0])
				minute   = int(t.split("-")[1])
				second   = int(t.split("-")[2])
				msecond  = int(x.split(".")[1])

				for i in range(0,len(sorted_files),1):
					i_t        = sorted_files[i].split(".")[0]
					i_hour     = int(i_t.split("-")[0])
					i_minute   = int(i_t.split("-")[1])
					i_second   = int(i_t.split("-")[2])
					i_msecond  = int(sorted_files[i].split(".")[1])
					if (hour < i_hour):
						sorted_files[i] = x
						break
					else:
						if (hour == i_hour):
							if (minute < i_minute):
								sorted_files[i] = x
								break
							else:
								if (second < i_second):
									sorted_files[i] = x
									break
								else:
									if (second == i_second):
										sorted_files[i] = x
										break
									else:
										if (msecond < i_msecond):
											sorted_files[i] = x
											break
				sorted_files.append(x)

			sorted_files = list(map(lambda x: "MSTeams_"  + str(yesterday) + "_" + str(x) + ".log", sorted_files))
			return(sorted_files)
		else:
			return []

	def _get_status_locally(self):
		files = self._get_todays_log_files(os.getlogin())
		state = None
		for file in reversed(files):
			with open('C:/Users/' + os.getlogin() + '/AppData/Local/Packages/MSTeams_8wekyb3d8bbwe/LocalCache/Microsoft/MSTeams/Logs/' + file, "r") as f:
				for line in reversed(list(f)):
					if ("availability:" in line):
						state = line.split("availability:")[-1].strip()[0:-1].split(',')[0]
						break
			if (state):
				break
		return state
	
	def _brightness_to_value(self, brightness):
		if ((brightness >= 0) and (brightness <= 100 )):
			points = [0, 25, 50, 80, 90, 100]
			if ((brightness >= points[0]) and (brightness <= points[1])):
				return brightness
			if ((brightness > points[1]) and (brightness <= points[2])):
				return (self._brightness_to_value(points[1]) + 2*(brightness - points[1]))
			if ((brightness > points[2]) and (brightness <= points[3])):
				return (self._brightness_to_value(points[2]) + 3*(brightness - points[2]))
			if ((brightness > points[3]) and (brightness <= points[4])):
				return (self._brightness_to_value(points[3]) + 4*(brightness - points[3]))
			if ((brightness > points[4]) and (brightness <= points[5])):
				return (self._brightness_to_value(points[4]) + 5*(brightness - points[4]))

	def _value_to_brightness(self, value):
		if ((value >= 0) and (value <= 255 )):
			points = [0, 25, 75, 165, 205, 255]
			if ((value >= points[0]) and (value <= points[1])):
				return value
			if ((value > points[1]) and (value <= points[2])):
				return int((value - points[1])/2 + self._value_to_brightness(points[1]))
			if ((value > points[2]) and (value <= points[3])):
				return int((value - points[2])/3 + self._value_to_brightness(points[2]))
			if ((value > points[3]) and (value <= points[4])):
				return int((value - points[3])/4 + self._value_to_brightness(points[3]))
			if ((value > points[4]) and (value <= points[5])):
				return int((value - points[4])/5 + self._value_to_brightness(points[4]))

	def _on_click_save(self, brightness_slider):
		self._brightness = self._brightness_to_value(int(brightness_slider.value))
		if (int(self._set_state) > 0):
			self._set_state = bytearray(self._brightness)
		self._window.destroy()

	def _on_click_cancel(self):
		self._window.destroy()

	def window(self, app):
		self._window = guizero.Window(
			app,
			height  = 500,
			width   = 500,
			visible = False,
			title   = self._name + " (" + self._gzidn + ")"
		)

		brightness_box = guizero.Box(
			self._window,
			align   = "top",
			width   = "fill",
		)

		brightness_text_box = guizero.Box(
			brightness_box,
			align   = "left",
			width   = 150,
			height  = 18,
		)

		guizero.Text(
			brightness_text_box,
			text    = "Brightness:",
			align   = "left",
		)

		brightness_slider = guizero.Slider(
			brightness_box,
			align      = "left",
			start      = 0,
			end        = 100,
			horizontal = True,
			width      = "fill",
		)
		brightness_slider.value = self._value_to_brightness(int(self._brightness))

		guizero.Text(
			self._window,
			text    = "",
			align   = "top",
			height  = 1,
			width   = "fill",
		)

		notifications_box = guizero.Box(
			self._window,
			align   = "top",
			width   = "fill",
		)

		notifications_text_box = guizero.Box(
			notifications_box,
			align   = "left",
			width   = 150,
			height  = 18,
		)

		guizero.Text(
			notifications_text_box,
			text    = "Notifications:",
			align   = "left"
		)

		notifications_check_box = guizero.Combo(
			notifications_box,
			options = ["None", "On/Off"],
			align   = "left",
		)

		guizero.Text(
			self._window,
			text    = "",
			align   = "bottom",
			height  = 1,
			width   = "fill",
		)

		button_box = guizero.Box(
			self._window,
			align   = "bottom",
			width   = "fill",
		)

		guizero.Text(
			button_box,
			text    = "",
			align   = "left",
			width   = 2,
		)

		guizero.PushButton(
			button_box,
			text     = "Save",
			align    = "left",
			width    = "fill",
			command  = self._on_click_save,
			args     = (brightness_slider,)
		)

		guizero.Text(
			button_box,
			text    = "",
			align   = "left",
			width   = 2,
		)

		guizero.PushButton(
			button_box,
			text     = "Cancel",
			align    = "left",
			width    = "fill",
			command  = self._on_click_cancel
		)

		guizero.Text(
			button_box,
			text    = "",
			align   = "right",
			width   = 2,
		)

		self._window.visible = True