## AirSim 소개
AirSim은 Microsoft가 개발한 Unreal Engine을 기반으로 제작된 시뮬레이터입니다.
자동차와 드론 등을 물리적 그리고 시각적으로 현실적인 환경에서 테스트 할 수 있습니다. 
자율주행, 자율비행, 딥러닝, 컴퓨터 비전, 강화학습의 플랫폼으로 만드는 것을 목표로 하고 있어
차량 제어, 데이터 습득 등 다양한 API를 제공하고 있습니다.

## 설치
1. AirSim-master는 [링크](https://github.com/microsoft/AirSim)의 github repository를 다운받으세요.

> AirSim은 C++과 Python API로 이루어져 있고, 이 파일에 소스코드와 예제들이 있습니다.
Python은 pip를 통해 쉽게 dependency를 구축할 수 있습니다.
C++은 visual studio와 연동하여 사용할 수 있습니다. (python 보다는 복잡할 수 있습니다.)
간단하게 python을 이용해봅시다.

2. 시뮬레이션 할 환경인 Map을 [링크](https://github.com/microsoft/AirSim/releases/tag/v.1.2.2)에서 다운받으세요.
(자율주행의 플랫폼으로 이용하고자 했기 때문에 Neighborhood, Plains, SimpleMaze를 다운받았어요.)

## Checking the map!
각 Map 파일에 들어있는 run.bat을 실행시키면 Map이 화면에 뜹니다.
따로 차를 구동하는 코드가 없어도 다음과 같은 방법으로 차를 움직일 수 있습니다.
- 키보드 w, a, s, d 를 입력해 주행할 수 있습니다. 
- 1,2,3은 depth image, semantic segmentation image, raw image를 출력합니다.
- B와 /키는 시점이 바뀝니다.
- F1키를 이용해 더 자세한 사용법을 볼 수 있습니다. (날씨도 변경 가능)

## Setting for Python and run the Code!
권장 Python 버전: 3.6 이상
virtual environment는 optional이지만 사용할 수 있으면 사용해보세요. 환경변수 꼬여도 마음이 편합니다. 컴퓨터가 window를 이용한다면, [링크](https://dojang.io/mod/page/view.php?id=2470)를 참고하셔도 됩니다. 

설치 1번에서 받은 파일의 압축을 풀고, AirSim/master/PythonClient/car/setup_path.py를 실행시킵니다.
pip upgrade를 한 후 airsim과 tornado, opencv를 설치해야 예제 코드를 실행시킬 수 있습니다.

~~~(bash)
pip3 install --upgrade pip
pip3 install airsim
pip3 install tornado
pip3 install opencv-contrib-python
~~~

설치 2번에서 다운한 맵을 선택해서 run.at 파일을 실행시키고
예제 코드인 AirSim/master/PythonClient/car/hello_car.py를 실행시켜봅시다.
실행이 된다면, 기어를 통해 전진, 후진, 중립 등 결정하여 throttle과 steering을 조절하면 차의 방향을 조종할 수 있습니다.

## Todo list
- setting for C++
