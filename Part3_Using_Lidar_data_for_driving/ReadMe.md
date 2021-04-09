## LiDAR란?
LiDAR는 표면 위의 물체와 물체 크기 및 거리까지 감지할 수 잇는 센서이다.
카메라와 달리 기상 변화의 영향을 크게 받지 않고, 야간이나 안개가 낀 날 등 빛이 차단된 환경에서도 잘 작동한다.
간단하게 LiDAR가 물체의 위치 정보를 얻어올 수 있는 원리는 다음과 같다.
> LiDAR의 레이저에서 빛을 쏘아 시그널을 방출 → 시그널이 장애물에 도달 → 그 시그널이 장애물에 반사 → 시그널이 리시버에 돌아옴 → 레이저 펄스가 기록
![lidar](https://user-images.githubusercontent.com/53460541/114142520-02e51b00-994e-11eb-80f9-1b6c51b53feb.png)
LiDAR는 카메라 및 GPS 정보를 받아올 수 없을 때, 효과적으로 자율주행의 객체 인식 및 회피 주행을 할 때 사용된다.

## AirSim에서 Lidar를 사용하기 위한 요구사항
[Part1](https://github.com/EunbinSeo/AirSim/blob/master/Part1_How_to_start_AirSim.md)에서 AirSim을 사용하기 위한 프로그램 및 Map 설치 등 setting하는 방법을 소개했다. 완료되면 AirSim문서의 AirSim/settings.json 파일을 열고 다음 내용을 입력하자.

```
{
 "SeeDocsAt": "https://github.com/Microsoft/AirSim/blob/master/docs/settings.md",
 "SettingsVersion": 1.2,
 "SimMode": "Car",
 "DefaultSensors": {
   "Distance": {
    "SensorType": 5,
    "Enabled": true
 },
 "Lidar1": {
  "SensorType": 6,
  "Enabled": true,
  "NumberOfChannels": 16,
  "RotationsPerSecond": 10,
  "PointsPerSecond": 200000,
  "DrawDebugPoints": false,
  "DataFrame": "SensorLocalFrame"
  }
 }
}

```
변수명에서 LiDAR 구성이 어떻게 되어 있는지 알 수 있다. LiDAR channel의 수 ("NumberOfChannels"), 회전 속도("RotationsPerSecond"), 초당 출력하는 point의 수("PointsPerSecond"), LiDAR에서 인식한 point들을 맵에 표시("DrawDebugPoints"), output에서의 point들의 Frame("DataFrame") 등을 조절할 수 있다. 

Velodyne사의 VLP16을 이용하기로 했는데 [Velodyne VLP-16 datasheet](http://www.mapix.com/wp-content/uploads/2018/07/63-9229_Rev-H_Puck-_Datasheet_Web-1.pdf)을 참고해보니 spec이 16채널의 1초당 최대 300000 point, 회전 속도는 5~20Hz이다. VLP16을 직접 사용해보니 200000 point씩 10Hz정도의 성능을 보여주었다. 이 사양에 맞춰 json파일을 작성해주었다. 

DrawDebugPoints를 true로 할 경우, 컴퓨터 사양에 따라 delay가 생길 수 있으니 false로 테스트하는 것이 더 나아보였다. 

LiDAR 구성을 더 추가하거나 바꾸고 싶다면 [document](https://github.com/microsoft/AirSim/blob/master/docs/lidar.md)를 참고하면 된다.

## LiDAR Raw data 추출 및 시각화
코드는 다음 [링크](https://github.com/EunbinSeo/AirSim/blob/master/Part3_Using_Lidar_data_for_driving/sample_code_Lidar.py)에서 다운 받아 AirSim-master/PythonClient/car 에 저장한다.

#### 1. Raw data
Lidar sensor에서 받는 Raw data의 형식은 3개의 element를 담은 리스트들을 무수히 많이 담고 있는 리스트로 이루어져 있다. 이는 Lidar에서 인식하는 point들의 위치이다.
코드 상에서 출력해보면 다음과 같이 나온다.
``` python3
points = self.parse_lidarData(lidarData)
print(points)
```
![lidar_raw_data](https://user-images.githubusercontent.com/53460541/114148649-f7492280-9954-11eb-93fd-ab48e27aa4b9.png)

이런 raw data를 x좌표는 x좌표끼리, y좌표는 y좌표끼리, z좌표는 z좌표끼리 뽑아내는 작업을 할 것이다. points에는 x, y, z 좌표가 한 리스트 안에 존재한다. 코드로 더 보게 좋게 나열하면 다음과 같다. 
``` python3
points = self.parse_lidarData(lidarData)
points_x = points[:,0]
points_y = points[:,1]
points_z = points[:,2]
print (f'x value : {points_x}\n y value : {points_y}\n z value: {points_z}\n')
```
![lidar_raw_data2](https://user-images.githubusercontent.com/53460541/114148659-f912e600-9954-11eb-9a0b-80974e91bba6.png)

#### 2. LiDAR data visualization
x, y, z 좌표를 각각 나누어 구했으니 data를 시각화 해보자. 3D로 나타내보고, 3D map의
xy평면에 정사영 시켜 2D map을 다시 그려볼 예정이다.

먼저 xyz좌표계에 point들을 그려보자. SimpleMaze map을 켜 코드를 실행시켜보자. 다음과 같이 3차원 plot을 볼 수 있다.
![lidar_plot](https://user-images.githubusercontent.com/53460541/114149418-d92ff200-9955-11eb-8822-1be531a68412.png)

16채널로 16개의 평면에 point들이 찍혀 있다. 이를 xy평면에 정사영 시켜 plot을 그려보자. 이는 LiDAR를 이용한 여공간 탐색 및 회피 주행에서 사용할 수 있다. 정사영시킨 plot만 화면에 띄우기 위해 다운 받은 코드를 수정해보자(주석처리 된 부분들을 보자).

코드의 70, 71번째 줄과 86, 87번째 줄을 다음과 같이 바꿔주자.
``` python3
ax = fig.gca(projection='3d')
# ax = Axes3D(fig)

ax.scatter(points[:, 0], points[:, 1], zs=0, zdir='z', marker='.', 
label='points : (x,y)')
# ax.scatter(points[:, 0], points[:, 1], points[:, 2], marker='.')
```
다시 SimpleMaze map을 켜 코드를 실행시켜보면 xy 평면에 모두 정사영되어서 나오는 것을 볼 수 있다.
![lidar_plot_perspective](https://user-images.githubusercontent.com/53460541/114149422-da611f00-9955-11eb-8ac9-53829d5dcc04.png)

#### 3. 기후 상황 바꿔 실습해보기
LiDAR는 기후 상황에 크게 영향을 받지 않는 sensor 중 하나이다. 기후 상황을 바꿔 실습해보자. 다음 사진은 기후 상황을 바꿔 눈이 오는 환경에서 주행하는 상황이다.
기후 환경을 바꿀 수 있도록 다음과 같이 self.client.simEnableWeather(True)를 추가해준다.
``` python3
class LidarTest:
 def __init__(self):
 self.client.simEnableWeather(True)
```
코드를 수정한 후 F10키를 눌러 기후환경을 마음대로 조정가능하다.
