## Camera
"카메라" 라고 하면 스마트폰의 카메라, 전문가들이 들고 다니는 카메라 등 떠오르는 것이 많아 굉장히 친숙하게 느껴진다.
카메라를 통해 받아오는 image 정보를 처리하는 영상 처리 기술은 많은 곳에서 이미 사용되고 있다.
자율주행분야에서 보면, 이슈화가 많이 된 tesla에서도 주로 이용하는 센서가 카메라이고 vision 중심의 autopilot을 공개하고 있다. 
카메라를 어디에 장착하냐에 따라 카메라의 기능이 달라진다.
> 전방 카메라인 경우:
> - 주행방향의 사람, 차량, 장애물 등 객체 인식
> - 주행방향의 차선 인식

> 측면 카메라인 경우:
> - 교차로 진입 등의 상황에서 차의 진행방향의 90도 각도의 객체 인식

> 후방 카메라인 경우:
> - 차선 합류 혹은 차선 변경 시 후방 사각지대를 감시
> - 후진 시 전방 카메라와 같은 역할

## AirSim에서 camera 사용하기
[Part1](https://github.com/EunbinSeo/AirSim/blob/master/Part1_How_to_start_AirSim.md) 에서 
우리는 맵을 선택해서 실행시킨 후 키보드를 이용하여 차를 조작했었다.
다시 한 번 맵을 선택해서 실행시켜보자. 숫자 키 '1', '2', '3'을 눌러보면, depth image, segmentation image, raw image가 화면에 출력된다. 여기서 우리는 raw image를 받아와 depth 정보가 담긴 이미지를 얻을 것이다. ([예제 코드](https://github.com/EunbinSeo/AirSim/blob/master/Part2_Using_camera_data_for_driving/sample_code_camera.py))
코드를 살펴보면, 다음과 같은 코드가 while 문 안에 있는데, 지속적으로 raw image를 받아오는 역할을 한다.
``` python3
rawImage = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthPerspective, True, False)])
}
```
이렇게 받은 raw image가 비어있는 정보가 아니라면 depth 정보가 담긴 이미지로 변환해 볼 것이다.
``` python3 
def transform_input(responses):
    img1d = np.array(responses[0].image_data_float, dtype=np.float)
    img1d = 255/np.maximum(np.ones(img1d.size), img1d)
    img2d = np.reshape(img1d, (responses[0].height, responses[0].width))

    from PIL import Image
    image = Image.fromarray(img2d)
    im_final = np.array(image.resize((720, 600)).convert('L'))

    return im_final
```
이 함수는 720\*600의 depth 정보가 담긴 이미지를 return한다. 각 픽셀은 grawy scale의 0~255에 해당하는 값을 가지고 있다. depth 이미지에 나타나는 색이 어두울수록(pixel의 값이 작을수록) 차 전방의 물체와 가깝다는 것을 확인할 수 있다.  
depth 이미지를 이용하여 SimpleMaze맵을 주행하는 코드를 실행시켜보자. 맵을 실행시킨후 방금 다운 받은 파이썬 코드를 실행시켜보자. 차를 움직이게 하는 예제 코드는 part1에서 다뤘던 hello_car.py를 참고하면된다. throttle은 차의 엔진을 직접 출력하는 것이기 때문에 우리가 생각하는 차의 속도가 아닐 수 있다. 관성 등을 고려하여 차를 움직여보자.

예제 코드는 다음과 같은 알고리즘으로 작성되어있다. 
1. 전진 혹은 후진: 전방의 가운데 영역의 가장 낮은 픽셀값을 기준으로 전진을 할지 후진을 할지 결정
2. 전진시: 왼쪽(left), 전방(center), 오른쪽(right)로 나눠 영역의 평균 픽셀 값을 기준으로 물체와의 거리가 가장 먼 쪽으로 이동한다.

예제코드보다 더 똑똑한 depth 이미지를 이용한 알고리즘을 개발하여 주행시켜보자.
![depthcar](depthcar.gif)
