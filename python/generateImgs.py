import os
import sys
import shutil
from imageGenerator import CalibrationPatternGenerator

# python generateImgs.py [rows] [cols] [filename]
# filename: image name
folderpath = os.getcwd() + "/user/generated/" + sys.argv[3]
campath = os.getcwd() + "/user/camera/" + sys.argv[3]
imgpath = os.getcwd() + "/user/uploads/" + sys.argv[3]
allpath = os.getcwd() + "/user/all/" + sys.argv[3]

# race condition will not happen unless there is a naming conflict in files (should not have)
if not os.path.exists(folderpath):
    os.makedirs(folderpath)
if not os.path.exists(campath):
    os.makedirs(campath)

cpg = CalibrationPatternGenerator(sys.argv[1], sys.argv[2], imgpath, folderpath, allpath)

cpg.createRegular()

shutil.make_archive(os.getcwd() + "/user/generated-zip/" + sys.argv[3], 'zip', folderpath)


# TODO: probably, remove the generated folder and the zip files after being used
