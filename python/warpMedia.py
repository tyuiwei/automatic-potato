import os
import sys
import cv2
from getDots import *
from detectPattern import DetectContours
from computeMapping import *

# python warpMedia.py [rows] [cols] [mediaId] [x] [y] [w] [h]

rows = int(sys.argv[1])
cols = int(sys.argv[2])
x = int(float(sys.argv[4]))
y = int(float(sys.argv[5]))
w = float(sys.argv[6])
h = float(sys.argv[7])

number_points = rows * cols
print rows, cols
sys.stdout.flush()
# alldot = cv2.imread(os.getcwd() + "/user/all/" + sys.argv[3] + ".jpg")
# # make image for userpt_locations
# blank = np.zeros(cv2.imread(os.getcwd() + "/user/camera/" + sys.argv[3] + "/0.jpg").shape)
# f_x = w / alldot.shape[1]
# f_y = h / alldot.shape[0]
#
# print alldot.shape
# print f_y, f_x
# print w/alldot.shape[1], h/alldot.shape[0]
# sys.stdout.flush()
#
# dots = cv2.resize(alldot, (None), fx=f_x, fy=f_y, interpolation = cv2.INTER_LINEAR)
# blank[y:int(y+h), x:int(x+w)] = dots

#  read_user_dots(path, number_points, x, y, w, h, shape):


userpt_locations = read_user_dots(os.getcwd() + "/user/generated/" + sys.argv[3], number_points, x,y,w,h,
                    cv2.imread(os.getcwd() + "/user/camera/" + sys.argv[3] + "/0.jpg").shape)
origpoints = read_dots(os.getcwd() + "/user/generated/" + sys.argv[3], number_points) #camera points

points = read_cam_dots(os.getcwd() + "/user/camera/" + sys.argv[3], number_points) #camera points
#forwarp = cv2.imread(os.getcwd() + "/user/uploads/" + sys.argv[3]) # + ".jpg") #media for warp
forwarp = cv2.imread(os.getcwd() + "/user/all/all2.jpg") # + ".jpg") #media for warp
height, width, depth = forwarp.shape
fx = 1.0*width/w
fy = 1.0*height/h
#warp_image(map(lambda x:x[0],origpoints), forwarp, (rows, cols), map(lambda x:x[0], userpt_locations),
warp_image(map(lambda x:x[0],points), forwarp, (rows, cols), map(lambda x:x[0], userpt_locations),
map(lambda x:x[0], points), os.getcwd() + "/user/final/" + sys.argv[3]+".jpg", fx, fy)
