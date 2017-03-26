import cv2
import cv2.cv as cv
import numpy as np
import math
import sys
import os
import imutils
from util import *
from getUserRect import *
from detectPattern import DetectContours
from detectPattern import DetectCircles
from findHomography import FindHomography


# TODO: automate getting the centroids of all the original calibration images
original = [(87, 141), (403, 141), (717, 141), (87, 347), (403, 347), (717, 347)]
original3b0 = [(33, 33), (178, 33), (326, 33), (474, 33), (622, 33), (765, 34),
                (33, 210), (178, 210), (326, 210), (474, 210), (622, 210), (766, 210),
                (33, 390), (178, 390), (326, 390), (474, 390), (622, 390), (766, 390),
                (34, 565), (178, 566), (326, 566), (474, 566), (622, 566), (765, 565)]

original3b = [(30, 30), (182, 30), (334, 30), (486, 30), (638, 30), (789, 30),
            (30, 216), (182, 216), (334, 216), (486, 216), (638, 216), (789, 216),
            (30, 403), (182, 403), (334, 403), (486, 403), (638, 403), (789, 403),
            (30, 589), (182, 589), (334, 589), (486, 589), (638, 589), (789, 589)]

original3c = [(25, 25), (135, 25), (245, 25), (355, 25), (465, 25), (575, 25), (685, 25), (794, 25),
            (25, 139), (135, 139), (245, 139), (355, 139), (465, 139), (575, 139), (685, 139), (794, 139),
            (25, 253), (135, 253), (245, 253), (355, 253), (465, 253), (575, 253), (685, 253), (794, 253),
            (25, 367), (135, 367), (245, 367), (355, 367), (465, 367), (575, 367), (685, 367), (794, 367),
            (25, 481), (135, 481), (245, 481), (355, 481), (465, 481), (575, 481), (685, 481), (794, 481),
            (25, 594), (135, 594), (245, 594), (355, 594), (465, 594), (575, 594), (685, 594), (794, 594)]


orig12 = [(30, 30), (283, 30), (536, 30), (789, 30), (30, 310), (283, 310),
(536, 310), (789, 310), (30, 589), (283, 589), (536, 589), (789, 589)]

orig18 = [(30, 30), (182, 30), (334, 30), (486, 30), (638, 30),
(789, 30), (30, 310), (182, 310), (334, 310), (486, 310),
(638, 310), (789, 310), (30, 589), (182, 589), (334, 589),
(486, 589), (638, 589), (789, 589)]

small18 =  [(293, 133), (361, 133), (430, 133), (498, 133), (566, 133), (635, 133), (293, 259), (361, 259), (430, 259),
 (498, 259), (566, 259), (635, 259), (293, 385), (361, 385), (430, 385), (498, 385), (566, 385), (635, 385)]

user = [(301, 136), (747, 136), (301, 403), (747, 403)]

orig35 = [(30, 30), (156, 30), (283, 30), (410, 30), (536, 30), (663, 30), (790, 30), (30, 170), (156, 170),
 (283, 170), (410, 170), (536, 170), (663, 170), (790, 170), (30, 310), (156, 310), (283, 310), (410, 310),
 (536, 310), (663, 310), (790, 310), (30, 450), (156, 450), (283, 450), (410, 450), (536, 450), (663, 450),
 (790, 450), (30, 590), (156, 590), (283, 590), (410, 590), (536, 590), (663, 590), (790, 590)]

#(1) translation from original to points -> get in between pixels from bilinear interpolation
#(2) homography from 4 points (1245) (2356)

#(1)

#form corners for bilinear interpolation: find a homography to make 4 corners rectilinear and apply
# homo from camera to original. new = apply homo to original
# bilinearly interpolate the orignal pixels to the new image

# def scale_translate_correction(image, transform) <-- TODO: needs to be cumulative for geometric prewarp


def interpolate_colour(original_image, (x0,y0)):
    # x0, y0 are non-integers
    x1 = int(math.floor(x0))
    x2 = int(math.ceil(x0))
    y1 = int(math.floor(y0))
    y2 = int(math.ceil(y0))
    if x1 != x2 and y1 != y2 and y2 < original_image.shape[0] and x2 < original_image.shape[1]:
        bi_points = []
        #TODO: check if its original_image[x,y] or original_image[y,x]
        bi_points.append((x1, y1, np.array(map(int, original_image[y1, x1]))))
        bi_points.append((x2, y1, np.array(map(int, original_image[y1, x2]))))
        bi_points.append((x1, y2, np.array(map(int, original_image[y2, x1]))))
        bi_points.append((x2, y2, np.array(map(int, original_image[y2, x2]))))
        colour = bilinear_interpolation(x0, y0, bi_points)
    else:
        colour = [0, 0, 0]
        if x1 == x2:
            #linearly interpolate y: color = ...
            colour = lerp(y0, [(y1, original_image[y1, x1]), (y2,original_image[y2, x1])])
        if y1 == y2:
            #linearly interpolate x: color = ...
            colour = lerp(x0, [(x1, original_image[y1, x1]), (x2,original_image[y1, x2])])
    return colour


# TRANSFORM :  H (inverse)
# reverse_warp_helper and warp_image are functions that loop through the rectangles and apply reverse bilinear interpolation
# to each point in the target image rectangle to obtain the colour

def reverse_warp_helper(original_points, user_points, target, forwarp, cam_points):
    target_h, target_w, target_d = target.shape

    inverse_transform = fh.sourceToDest(np.array(user_points), np.array(cam_points))

    #TODO: change this from a simple nested loop to apply a function on a single numpy array (faster)
    for y in range(target_h):
        for x in range(target_w):
            # inv transform
            # if point in original box, interpolate color, else point outside, put as black/white?
            # then mask out the black/white outside points and combine the image
            original_location = fh.getDest([x,y], inverse_transform)
            (x0, y0) = original_location[0]
            #check if the original location, according to the homography,  is  within our rectangle of interest
            if y0 >= original_points[0][1] and y0 <= original_points[-1][1] and x0 >= original_points[0][0] and x0 <= original_points[1][0]:
                target[y,x] = interpolate_colour(forwarp, (x0,y0))
            else:
                target[y,x] = [0,0,0]


def warp_image(original_points, forwarp, points_shape, user_points, cam_points):
    # points_shape: (rows, cols) tuple, describing the layout of dots e.g. 9 dots (3,3) or 12 dots (3,4)
    blank = np.zeros((1200,1200, 3), dtype=np.uint8)
    #this function passes indices to a helper, which will transform that sub-rectangle
    rows = points_shape[0]
    cols = points_shape[1]
    for index in range(len(original_points)-cols-1):
        temp = np.zeros(blank.shape, dtype=np.uint8)
        if (index+1) % cols != 0:
            print index+cols+1

            original_corners = [original_points[index], original_points[index+1],
                                original_points[index+cols], original_points[index+cols+1]]
            cam_corners = [cam_points[index], cam_points[index+1], cam_points[index+cols], cam_points[index+cols+1]]
            user_corners = [user_points[index], user_points[index+1], user_points[index+cols], user_points[index+cols+1]]
            reverse_warp_helper(original_corners, user_corners, temp, forwarp, cam_corners)
        blank = cv2.add(blank, temp)

    cv2.imwrite(sys.argv[2], blank)
#    cv2.imshow('blank', blank)
#    cv2.waitKey(0)

def read_dots(path):
    dco = DetectContours()
    points = []
    for i in range(0,number_points):
        #if i < 10:
        #    i = str(0) + str(i)
        img = cv2.imread(path + "/" + str(i) + ".jpg")
        a = dco.getContours(img)
        #dci.get_circles(img)
        points.append(dco.getCentroids(a))
        #points.append(dci.get)
    return points

#TODO: make number_points based on (r,c)
number_points = 18
dco = DetectContours()
dci = DetectCircles()
fh = FindHomography()
points = []
cam_shape = []

points = read_dots("images/" + sys.argv[1])



print points
forwarp = cv2.imread('images/doge18.jpg')
height, width, depth = forwarp.shape
userpt_locations = get_dots("images/user/3e18user.jpg")
#userpt_orig_locations = original_locations(userpt_locations, (3,6), orig18, points)

#warp_image(map(lambda x:x[0], points), forwarp, (3,6), userpt_locations, points)

#warp_image(userpt_locations, forwarp, (3,6), map(lambda x:x[0] , points), userpt_locations)

warp_image(orig18, forwarp, (3,6), userpt_locations, map(lambda x:x[0], points))
