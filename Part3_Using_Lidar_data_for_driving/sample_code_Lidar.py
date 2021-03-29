# Python client example to get Lidar data from a car

import setup_path
import airsim
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
import math
import time
import argparse
import pprint

import numpy


# Makes the drone fly and get Lidar data

class LidarTest:

    def __init__(self):

        # connect to the AirSim simulator

        self.client = airsim.CarClient()

        self.client.confirmConnection()

        self.client.enableApiControl(False)

        self.car_controls = airsim.CarControls()

    def execute(self):

        for i in range(3):

            state = self.client.getCarState()

            s = pprint.pformat(state)

            # print("state: %s" % s)

            # go forward

            self.car_controls.throttle = 1

            self.car_controls.steering = 0

            self.client.setCarControls(self.car_controls)

            print("Go Forward")

            time.sleep(3)  # let car drive a bit

            # Go forward + steer right
            '''
            self.car_controls.throttle = 0.5

            self.car_controls.steering = 1

            self.client.setCarControls(self.car_controls)

            print("Go Forward, steer right")

            time.sleep(3)  # let car drive a bit
            # airsim.wait_key('Press any key to get Lidar readings')
            '''
            fig = plt.figure(figsize=[5, 5])

            while (True):
                #-----------ax = fig.gca(projection='3d')
                ax = Axes3D(fig)
                lidarData = self.client.getLidarData();

                if (len(lidarData.point_cloud) < 3):

                    print("\tNo points received from Lidar data")

                else:
                    points = self.parse_lidarData(lidarData)
                    '''
                    points_x = points[:,0]
                    points_y = points[:,1]
                    points_z = points[:,2]
                    print (f'x value : {points_x}\n y value : {points_y}\n z value: {points_z}\n')
                    '''
                    #---------------ax.scatter(points[:, 0], points[:, 1], zs=0, zdir='z', marker='.', label='points : (x,y)')
                    ax.scatter(points[:, 0], points[:, 1], points[:, 2], marker='.')
                    ax.set_xlim([-35,35])
                    ax.set_ylim([-30,30])
                    ax.set_zlim([-1,1])
                    plt.pause(0.00001)

                    # plt.hold(False)

    def parse_lidarData(self, data):

        # reshape array of floats to array of [X,Y,Z]

        points = numpy.array(data.point_cloud, dtype=numpy.dtype('f4'))

        points = numpy.reshape(points, (int(points.shape[0] / 3), 3))

        return points

    def write_lidarData_to_disk(self, points):

        # TODO

        print("not yet implemented")

    def stop(self):

        airsim.wait_key('Press any key to reset to original state')

        self.client.reset()

        self.client.enableApiControl(False)

        print("Done!\n")


# main

if __name__ == "__main__":
    lidarTest = LidarTest()
    lidarTest.execute()
