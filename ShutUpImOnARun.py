import obspython as obs
import socket

# Global variables
index = 0
current_index = 0
hide_source_name = ""
show_source_name = ""
enabled = False
pb_pace_only = False
mute_only = False
livesplit_socket = None
connection_retry_count = 0

def connect_loop():
	global livesplit_socket
	global connection_retry_count

	if not livesplit_socket:
		livesplit_socket = connect_to_livesplit("localhost", 16834)
		if livesplit_socket:
			# Reset connection retry count if connection was successful
			connection_retry_count = 0
			obs.timer_remove(connect_loop)
			obs.timer_add(update_loop, 1000)  # Call every 1 second
		else:
			# add to connection retry count if connection was not successful
			connection_retry_count = connection_retry_count + 1
	# If connection retry count is greater than 5, stop trying to connect
	if connection_retry_count > 5:
		obs.timer_remove(connect_loop)
		obs.script_log(obs.LOG_ERROR, "Stopping script. Please start LiveSplit Server and restart the script.")


def update_loop():
	global index
	global current_index
	global livesplit_socket
	global pb_pace_only

	# Handle LiveSlplit connection

	if not livesplit_socket:
		livesplit_socket = connect_to_livesplit("localhost", 16834)

	# If LiveSplit is connected, handle logic
	else:

		# Check current LiveSplit phase
		current_phase = send_command(livesplit_socket, "getcurrenttimerphase")
		# When Run is active, continue
		if current_phase == "Running":
			# Check if PB Pace only is checked and run is PB Pace
			if pb_pace_only:
				pb_pace = is_pb_pace()
			else:
				pb_pace = True
			# If run is PB Pace or not in PB only mode, continue
			if pb_pace:
				# Check current LiveSplit index
				current_index = send_command(livesplit_socket, "getsplitindex")
				if current_index:
					current_index = int(current_index)
					if current_index >= index:
						# If set index has been reached, hide source
						update_sources(True)
					else:
						update_sources(False)
				else:
					# if no data was returned, reconnect server
					livesplit_socket = None
		else: 
			# When no run is active, set source visible
			update_sources(False)


# Handle OBS Scource visibility	
def update_sources(hide_sources):
	global hide_source_name
	global show_source_name
	global mute_only
	global connection_retry_count

	# Reset connection retry count if settings changed
	connection_retry_count = 0

	# Get Sources from Settings
	current_scene = obs.obs_frontend_get_current_scene()
	scene_sources = obs.obs_scene_from_source(current_scene)
	hide_item = obs.obs_scene_find_source(scene_sources, hide_source_name)
	show_item = obs.obs_scene_find_source(scene_sources, show_source_name)
	mute_source = obs.obs_get_source_by_name(hide_source_name)

	# Toggle Visibility / Audio
	if hide_sources:
		if mute_only:
			obs.obs_source_set_muted(mute_source, True)
		else:
			obs.obs_sceneitem_set_visible(hide_item, False)
		obs.obs_sceneitem_set_visible(show_item, True)
	else:
		if mute_only:
			obs.obs_source_set_muted(mute_source, False)
		else:
			obs.obs_sceneitem_set_visible(hide_item, True),
		obs.obs_sceneitem_set_visible(show_item, False)

	# Release Sources
	obs.obs_source_release(mute_source)
	obs.obs_source_release(current_scene)

# OBS  __________________________________________________________________________________________________

# Script properties
def script_properties():
	props = obs.obs_properties_create()

	# Checkbox to enable/disable the script
	obs.obs_properties_add_bool(props, "enabled", "Enabled")

	# Checkbox to set if script is only active if on pb pace
	obs.obs_properties_add_bool(props, "pb_pace_only", "Only for PB Pace")

	# Int input called index
	obs.obs_properties_add_int(props, "index", "Split Index", 0, 100, 1)

	# Source selector for hide_source
	p = obs.obs_properties_add_list(props, "hide_source", "Source to hide/mute", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
	sources = obs.obs_enum_sources()
	if sources is not None:
		for source in sources:
			name = obs.obs_source_get_name(source)
			obs.obs_property_list_add_string(p, name, name)

		obs.source_list_release(sources)

	# Checkbox to enable/disable the script
	obs.obs_properties_add_bool(props, "mute_only", "Mute Only")

	# Source selector for show_source
	p = obs.obs_properties_add_list(props, "show_source", "Source to show", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
	sources = obs.obs_enum_sources()
	if sources is not None:
		for source in sources:
			name = obs.obs_source_get_name(source)
			obs.obs_property_list_add_string(p, name, name)

		obs.source_list_release(sources)

	return props

# Set default values
def script_defaults(settings):
	obs.obs_data_set_default_int(settings, "index", 0)
	obs.obs_data_set_default_bool(settings, "enabled", False)
	obs.obs_data_set_default_bool(settings, "pb_pace_only", False)
	obs.obs_data_set_default_bool(settings, "mute_only", False)

# Description
def script_description():
    return "Hides and shows sources if run has passed a certian split in LiveSplit. Reverts to default when run ends.\nChoose Split number where Sources shoud be toggled.    First Split = Index 0\n\nMade by: Davi Be v0.1"

# Scrupt update function
def script_update(settings):
	global index
	global hide_source_name
	global show_source_name
	global enabled
	global pb_pace_only
	global mute_only
	global livesplit_socket

	mute_only = obs.obs_data_get_bool(settings, "mute_only")
	enabled = obs.obs_data_get_bool(settings, "enabled")
	pb_pace_only = obs.obs_data_get_bool(settings, "pb_pace_only")
	index = obs.obs_data_get_int(settings, "index")
	hide_source_name = obs.obs_data_get_string(settings, "hide_source")
	show_source_name = obs.obs_data_get_string(settings, "show_source")
	
	# Timer to call connect_loop every 5 seconds
	obs.timer_remove(update_loop)
	obs.timer_remove(connect_loop)
	if enabled:
		connect_loop()
		if not livesplit_socket:
			obs.timer_add(connect_loop, 30000)
	else:
		if livesplit_socket:
			livesplit_socket.close()
			livesplit_socket = None

# LiveSplit __________________________________________________

# Connect to LiveSplit server	
def connect_to_livesplit(host, port):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, port))
		obs.script_log(obs.LOG_INFO, "Connected to LiveSplit server.")
		return s
	except ConnectionRefusedError:
		obs.script_log(obs.LOG_INFO, "Failed to connect to LiveSplit server. Trying to reconnect..")
		return None
	except Exception as e:
		obs.script_log(obs.LOG_ERROR, f"Error: {e}")
		return None
		
# Send command to LiveSplit server
def send_command(sock, command):
	global livesplit_socket
	try:
		sock.send((command + "\r\n").encode())
		response = sock.recv(1024).decode().strip()
		return response
	except Exception as e:
		obs.script_log(obs.LOG_ERROR, "Connection to LiveSplit server lost. Trying to reconnect..")
		livesplit_socket = None
		obs.timer_remove(update_loop)
		obs.timer_add(connect_loop, 5000)
		return None
	
# Check if current pace is PB pace
def is_pb_pace():
	current_delta = send_command(livesplit_socket, "getdelta")
	# Convert to Unicode to differenceate between '-' as Hyphen-Minus (45) for none, and '-' as Minus Sign (8722) for negative delta
	# No Delta present
	if ord(current_delta[:1]) == 45:
		return False
	# If delta is positive, run is not PB Pace
	elif ord(current_delta[:1]) == 43:
		return False
	# If delta is negative, run is PB Pace
	elif ord(current_delta[:1]) == 8722:
		return True
