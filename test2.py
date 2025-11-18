import time
import sys

print("Loading...", end="", flush=True)
time.sleep(2)
# Overwrite "Loading..." with spaces and then new text
sys.stdout.write("\r" + " " * 10 + "\r") # Clear the line with spaces
sys.stdout.write("Done!")
sys.stdout.flush()
