def rect(width, length):
	"""
	Create a rectangle made of "#" with the dimensions width by length.

	Test in Interactive Mode: python3 -i <filename>.py
		- ctrl + L to clear
		- ctrl + D to exit
	
	>>> rect(4, 1)
	####

	>>> rec(6, 3)
	######
	######
	######
	"""

	blocks = '#' * width

	for _ in range(length):

		print(blocks)


	
