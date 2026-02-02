import re

FILENAME_REGEX = re.compile("[\/\\\\<>:\"|?*.]+")

def correct_filename(name: str):
	return FILENAME_REGEX.sub("_", name)

def correct_image_filename(name: str):

	period_index = name.rfind(".")
	if period_index != -1:
		ext = name[period_index + 1:]
		if not ext.isdigit():
			name = name[:period_index]

	return FILENAME_REGEX.sub("_", name)