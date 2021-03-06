# coding: utf-8
import os
import sys
import numpy as np
import h5py
import matplotlib.pyplot as plt
from eulerangles import euler2mat
from mpl_toolkits.mplot3d import axes3d, Axes3D #<-- Note the capitalization!
from PIL import Image
import random

FILE_NAME = "data/modelnet40_ply_hdf5_2048/ply_data_train0.h5"
SHAPE_NAME = "data/modelnet40_ply_hdf5_2048/shape_names.txt"
def load_h5(h5_filename):
    f = h5py.File(h5_filename)
    data = f['data'][:]
    label = f['label'][:]
    return (data, label)

def loadDataFile(filename):
    return load_h5(filename)


data,label = loadDataFile(FILE_NAME)
shape_names = [line.rstrip() for line in open(SHAPE_NAME)]


#
def pyplot_draw_point_cloud(points, output_filename):
    """ points is a Nx3 numpy array """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:,0], points[:,1], points[:,2])
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    plt.savefig("plt.jpg")
    plt.show()


def draw_point_cloud(input_points, canvasSize=500, space=200, diameter=25,
                     xrot=0, yrot=0, zrot=0, switch_xyz=[0,1,2], normalize=True):
    """ Render point cloud to image with alpha channel.
        Input:
            points: Nx3 numpy array (+y is up direction)
        Output:
            gray image as numpy array of size canvasSizexcanvasSize
    """
    image = np.zeros((canvasSize, canvasSize))
    if input_points is None or input_points.shape[0] == 0:
        return image

    points = input_points[:, switch_xyz]
    M = euler2mat(zrot, yrot, xrot)
    points = (np.dot(M, points.transpose())).transpose()

    # Normalize the point cloud
    # We normalize scale to fit points in a unit sphere
    if normalize:
        centroid = np.mean(points, axis=0)
        points -= centroid
        furthest_distance = np.max(np.sqrt(np.sum(abs(points)**2,axis=-1)))
        points /= furthest_distance

    # Pre-compute the Gaussian disk
    radius = (diameter-1)/2.0
    disk = np.zeros((diameter, diameter))
    for i in range(diameter):
        for j in range(diameter):
            if (i - radius) * (i-radius) + (j-radius) * (j-radius) <= radius * radius:
                disk[i, j] = np.exp((-(i-radius)**2 - (j-radius)**2)/(radius**2))
    mask = np.argwhere(disk > 0)
    dx = mask[:, 0]
    dy = mask[:, 1]
    dv = disk[disk > 0]

    # Order points by z-buffer
    zorder = np.argsort(points[:, 2])
    points = points[zorder, :]
    points[:, 2] = (points[:, 2] - np.min(points[:, 2])) / (np.max(points[:, 2] - np.min(points[:, 2])))
    max_depth = np.max(points[:, 2])

    for i in range(points.shape[0]):
        j = points.shape[0] - i - 1
        x = points[j, 0]
        y = points[j, 1]
        xc = canvasSize/2 + (x*space)
        yc = canvasSize/2 + (y*space)
        xc = int(np.round(xc))
        yc = int(np.round(yc))

        px = dx + xc
        py = dy + yc

        image[px, py] = image[px, py] * 0.7 + dv * (max_depth - points[j, 2]) * 0.3

    image = image / np.max(image)
    return image

def point_cloud_three_views(points):
    """ input points Nx3 numpy array (+y is up direction).
        return an numpy array gray image of size 500x1500. """
    # +y is up direction
    # xrot is azimuth
    # yrot is in-plane
    # zrot is elevation
    img1 = draw_point_cloud(points, zrot=110/180.0*np.pi, xrot=45/180.0*np.pi, yrot=0/180.0*np.pi)
    img2 = draw_point_cloud(points, zrot=70/180.0*np.pi, xrot=135/180.0*np.pi, yrot=0/180.0*np.pi)
    img3 = draw_point_cloud(points, zrot=180.0/180.0*np.pi, xrot=90/180.0*np.pi, yrot=0/180.0*np.pi)
    image_large = np.concatenate([img1, img2, img3], 1)
    return image_large

def point_cloud_three_views_demo():
    """ Demo for draw_point_cloud function """
    points = data[index]
    im_array = point_cloud_three_views(points)
    img = Image.fromarray(np.uint8(im_array*255.0))
    img.show('piano.jpg')

index = 5 #random.randint(0,len(label))
#
print(shape_names[int(label[index])])
im_array = draw_point_cloud(data[index],zrot=110/180.0*np.pi, xrot=45/180.0*np.pi, yrot=0/180.0*np.pi)
img = Image.fromarray(np.uint8(im_array*255.0))
img.show('huehue.jpg')
point_cloud_three_views_demo()
pyplot_draw_point_cloud(data[index],"")
# def read_off(file):
#     verts = []
#     faces = []
#     with open(file, "r") as infile:
#         if 'OFF' != infile.readline().strip():
#             raise Exception('Not a valid OFF header')
#         n_verts, n_faces, n_dontknow = tuple([int(s) for s in infile.readline().strip().split(' ')])
#
#         for i_vert in range(n_verts):
#             verts.append([float(s) for s in infile.readline().strip().split(' ')])
#
#         for i_face in range(n_faces):
#             faces.append([int(s) for s in infile.readline().strip().split(' ')][1:])
#     return verts, faces
# OFF_FILE = "data/ModelNet40/airplane/test/airplane_0627.off"
# verts, faces = read_off(OFF_FILE)
