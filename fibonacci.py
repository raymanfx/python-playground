from timeit import default_timer as timer
import sys

verbose = 1

def myprint(x):
  if (verbose):
    print(x)

def timed_func(func, *args):
  t_start = timer()
  myprint("Calling {} with arguments: {}".format(func, *args))
  func(*args)
  t_end = timer()
  return (t_end - t_start)

def fiboRec(x):
  index = int(x)
  first = 0
  second = 1
  if (index <= 1):
    return index
  else:
    result = fiboRec(index - 1) + fiboRec(index - 2)
    return result

def fiboIt(x):
  index = int(x)
  first = 0
  second = 1
  if (index <= 1):
    return index
  else:
    current = second
    new_index = 1
    while (new_index < index):
      current = first + second
      first = second
      second = current
      new_index = new_index + 1
    myprint("fiboIt: returning result: {}".format(current))
    return current


if len(sys.argv) != 2:
  print("usage: python fibonacci.py <index>")
  sys.exit()

fiboIndex = sys.argv[1]

# Test
#time = timed_func(fiboRec, fiboIndex)
#print("{}{}".format("TOTAL EXECUTION TIME - recursive (ms): ", time * 1000))
time = timed_func(fiboIt, fiboIndex)
print("{}{}".format("TOTAL EXECUTION TIME - iterative (ms): ", time * 1000))
