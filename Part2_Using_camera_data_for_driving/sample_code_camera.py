# In settings.json first activate computer vision mode: 
# https://github.com/Microsoft/AirSim/blob/master/docs/image_apis.md#computer-vision-mode

import setup_path
import airsim

# requires Python 3.5.3 :: Anaconda 4.4.0
# pip install opencv-python
import cv2
import time
import sys
import numpy as np

def printUsage():
    print("Usage: python camera.py [depth|segmentation|scene]")

def transform_input(responses):
    img1d = np.array(responses[0].image_data_float, dtype=np.float)
    img1d = 255/np.maximum(np.ones(img1d.size), img1d)
    img2d = np.reshape(img1d, (responses[0].height, responses[0].width))

    from PIL import Image
    image = Image.fromarray(img2d)
    im_final = np.array(image.resize((720, 600)).convert('L'))

    return im_final


cameraType = "depth"

for arg in sys.argv[1:]:
    cameraType = arg.lower()

cameraTypeMap = {
    "depth": airsim.ImageType.DepthVis,
    "segmentation": airsim.ImageType.Segmentation,
    "seg": airsim.ImageType.Segmentation,
    "scene": airsim.ImageType.Scene,
    "disparity": airsim.ImageType.DisparityNormalized,
    "normals": airsim.ImageType.SurfaceNormals
}

if (not cameraType in cameraTypeMap):
    printUsage()
    sys.exit(0)

print(cameraTypeMap[cameraType])

client = airsim.CarClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
help = False
car_controls = airsim.CarControls()
frameCount = 0
"""
fontFace = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.5
thickness = 2
textSize, baseline = cv2.getTextSize("FPS", fontFace, fontScale, thickness)
print(textSize)

textOrg = (10, 10 + textSize[1])



fps = 0
"""

repeat = 0 # 같은공간에서 앞뒤 앞뒤 반복 피하는 용도

while True:
    # because this method returns std::vector<uint8>, msgpack decides to encode it as a string unfortunately.
    #rawImage = client.simGetImage("0", cameraTypeMap[cameraType])
    rawImage = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthPerspective, True, False)])
    if (rawImage == None):
        print("Camera is not returning image, please check airsim for error messages")
        sys.exit(0)
    else:
        png = transform_input(rawImage) # depth image를 받아온다.
        png = cv2.bitwise_not(png)      # 받아온 depth image를 흑백반전 시킨다.
        left = png.copy()
        center = png.copy()
        right = png.copy()
        centerbox = png.copy()

        left = png[:,:240]  # depth image(720 * 600) 에서 왼쪽 영역(600*240 size)를 잘라낸다. 
        center = png[:, 240:480] # depth image(720 * 600) 에서 가운데 영역(600*240 size)를 잘라낸다.
        right = png[:, 480:] # depth image(720 * 600) 에서 오른쪽 영역(600*240 size)를 잘라낸다.
        centerbox = png[100:500, 140:580] # depth image(720 * 600) 에서 중심 영역(400*440 size)를 잘라낸다.

        # left, center, right, centerbox 이미지의 각 pixel 값을 array로 변환
        left_array = np.array(left)
        left_array = left_array.reshape(144000)
        center_array = np.array(center)
        center_array = center_array.reshape(144000)
        right_array = np.array(right)
        right_array = right_array.reshape(144000)
        centerbox_array = np.array(centerbox)
        centerbox_array = centerbox_array.reshape(176000)

        #배열 출력
        """
        print("left")
        print(left_array)
        print("center")
        print(center_array)
        print("right")
        print(right_array)
        print("centerbox")
        print(centerbox_array)
        
        """
        aver_left = int(np.mean(left_array))
        aver_center = int(np.mean(center_array))
        aver_right = int(np.mean(right_array))
        aver_centerbox = int(np.mean(centerbox_array))

        # 각 화면 픽셀의 평균값 출력

        """
        print("left")
        print(aver_left)
        print("center")
        print(aver_center)
        print("right")
        print(aver_right)
        print("centerbox")
        print(aver_centerbox)
        """

        #cv2.putText(png, 'FPS ' + str(fps), textOrg, fontFace, fontScale, (255, 0, 255), thickness)
        #png = cv2.resize(png, None, fx=10, fy=10)

        #화면 출력

        cv2.imshow("Depth", png)
        cv2.imshow("Left", left)
        cv2.imshow("Center", center)
        cv2.imshow("Right", right)
        cv2.imshow("Centerbox", centerbox)

        #centerbox 영역에 있는 물체들 중, 가장 가까운 것의 pixel값이 150이상이면 전진 
        if np.min(centerbox_array) > 150:
            
            #이후, 이미지를 다시 left, center, right 영역으로 나눈 후, 각 영역에 존재하는 pixel값들의 평균을 구한다.
            #평균값이 가장 큰 방향을 차의 이동방향으로 결정한다.
            max_value = max(aver_left,aver_center, aver_right)
            if max_value == aver_left:
                direction = "left"
            if max_value == aver_center:
                direction = "front"
            if max_value == aver_right:
                direction = "right"

        #centerbox 영역에 있는 물체들 중, 가장 가까운 것의 pixel값이 150 이하이면 후진 
        else:
            direction = "back"

        # get state of the car
        car_state = client.getCarState()
        print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))

        #차를 왼쪽으로 전진시키는 코드
        if direction == "left":
            #관성을 줄이기 위해, 차가 움직이고 있는 경우 0.1초간 break 시켰다.
            if car_state.speed != 0:
                car_controls.brake = 1
                client.setCarControls(car_controls)
                print("Apply brakes")
                time.sleep(0.1)  # let car drive a bit
                car_controls.brake = 0  # remove brake

            # Go forward + steer left (왼쪽으로 전진)
            car_controls.throttle = 0.5
            car_controls.steering = -0.5
            client.setCarControls(car_controls)
            print("Go Forward, steer left")
            time.sleep(0.5)  # let car drive a bit

        #차를 앞으로 전진시키는 코드
        if direction == "front":
            #관성을 줄이기 위해, 차가 움직이고 있는 경우 0.1초간 break 시켰다.
            if car_state.speed != 0:
                car_controls.brake = 1
                client.setCarControls(car_controls)
                print("Apply brakes")
                time.sleep(0.1)  # let car drive a bit
                car_controls.brake = 0  # remove brake

            # go forward (앞으로 전진)
            car_controls.throttle = 0.5
            car_controls.steering = 0
            client.setCarControls(car_controls)
            print("Go Forward")
            time.sleep(0.5)  # let car drive a bit

        #차를 오른쪽으로 전진시키는 코드
        if direction == "right":
            if car_state.speed != 0:
                car_controls.brake = 1
                client.setCarControls(car_controls)
                print("Apply brakes")
                time.sleep(0.1)  # let car drive a bit
                car_controls.brake = 0  # remove brake

            # Go forward + steer right
            car_controls.throttle = 0.5
            car_controls.steering = 0.5
            client.setCarControls(car_controls)
            print("Go Forward, steer right")
            time.sleep(0.5)  # let car drive a bit

        if direction == "back":
            #관성을 줄이기 위해, 차가 움직이고 있는 경우 0.1초간 break 시켰다.
            if car_state.speed != 0:
                car_controls.brake = 1
                client.setCarControls(car_controls)
                print("Apply brakes")
                time.sleep(0.1)  # let car drive a bit
                car_controls.brake = 0  # remove brake

            # go reverse (후진)
            car_controls.throttle = -0.5
            car_controls.is_manual_gear = True;
            car_controls.manual_gear = -1
            car_controls.steering = 0
            client.setCarControls(car_controls)
            print("Go reverse, steer right")
            time.sleep(0.5)  # let car drive a bit
            car_controls.is_manual_gear = False;  # change back gear to auto
            car_controls.manual_gear = 0

            if direction == "front":
                repeat += 1

            elif direction == "back":
                repeat += 1

            else:
                repeat = 0
                
        #차가 같은 공간에서 전진, 후진을 반복하는 경우 그 공간을 빠져나오게 하기 위해 작성한 코드. steering을 오른쪽으로 한 상태로 후진한다.
        if repeat == 10:
            if car_state.speed != 0:
                car_controls.brake = 1
                client.setCarControls(car_controls)
                print("Apply brakes")
                time.sleep(0.1)  # let car drive a bit
                car_controls.brake = 0  # remove brake
            # go reverse
            car_controls.throttle = -1
            car_controls.is_manual_gear = True;
            car_controls.manual_gear = -1
            car_controls.steering = 1
            client.setCarControls(car_controls)
            print("Go reverse, steer right")
            time.sleep(1.5)  # let car drive a bit
            car_controls.is_manual_gear = False;  # change back gear to auto
            car_controls.manual_gear = 0
            repeat = 0
    frameCount = frameCount + 1


    key = cv2.waitKey(1) & 0xFF;
    if (key == 27 or key == ord('q') or key == ord('x')):
        break;

client.enableApiControl(False)
