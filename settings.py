import sys,os
# select the elements of path list who  contains the word 'site-packages'
site = [x for x in sys.path if 'site-packages' in x]

# take current working directory
cwd = sys.path[0] 
# add src
cwd = os.path.join(cwd, 'src')
print(cwd)
# create a new file named conda.pth in the site-packages directory
with open(os.path.join(site[0], 'conda.pth'), 'w') as f:
    f.write(cwd)
