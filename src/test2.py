import os
os.system("matchbox-keyboard &")
input()
os.system("kill $(pgrep matchbox-*)")