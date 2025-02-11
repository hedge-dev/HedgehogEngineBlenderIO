import re

FILENAME_REGEX = re.compile("[\/\\\\<>:\"|?*]+")

def correct_filename(name: str):
	return FILENAME_REGEX.sub("_", name)