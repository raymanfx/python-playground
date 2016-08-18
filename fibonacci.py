from timeit import default_timer as timer

verbose = 0

def myprint(x):
	if (verbose):
		print(x)

def timed_func(func, arg):
	t_start = timer()
	func(arg)
	t_end = timer()
	return (t_end - t_start)

def fiboRec(x):
	first = 1
	second = 2
	if (x <= 2):
		return x
	else:
		result = fiboRec(x - 1) + fiboRec(x - 2)
		return result

def fiboIt(x):
	first = 1
	second = 2
	if (x <= 2):
		return x
	else:
		current = second
		index = 2
		while (index < x):
			current = first + second
			first = second
			second = current
			index = index + 1
		return current

# Test
time = timed_func(fiboRec, 30)
print("{}{}".format("TOTAL EXECUTION TIME - recursive (ms): ", time * 1000))
time = timed_func(fiboIt, 30)
print("{}{}".format("TOTAL EXECUTION TIME - iterative (ms): ", time * 1000))
