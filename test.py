from devices.DND_sign import DND_sign



def test_value_to_brigtness_conversion():
	sign = DND_sign(
		"DND_sign",
		"20241230000001",
		{
			"bt_address" : "48:ca:43:dd:2e:ae",
			"brightness" : 10
		}
	)

	for x in range(0,25,1):
		y = sign._brightness_to_value(sign._value_to_brightness(x))
		if not(x == y):
			assert (x == y)

	for x in range(25,75,2):
		y = sign._brightness_to_value(sign._value_to_brightness(x))
		if not(x == y):
			assert (x == y)
	
	for x in range(75,165,3):
		y = sign._brightness_to_value(sign._value_to_brightness(x))
		if not(x == y):
			assert (x == y)
	
	for x in range(165,205,4):
		y = sign._brightness_to_value(sign._value_to_brightness(x))
		if not(x == y):
			assert (x == y)
	
	for x in range(205,260,5):
		y = sign._brightness_to_value(sign._value_to_brightness(x))
		if not(x == y):
			assert (x == y)