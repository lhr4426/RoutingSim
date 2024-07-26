# RoutingSim
2024 산학협력프로젝트

개발 환경 설정 : conda env create -f RemoteSim.yaml
실행 방법 : 
1. server_binding.json 파일 수정 (선택)
2. key_binding.json 파일 수정 (선택)
3. python routing_sim.py
4. python routing_test_client.py (선택)

데이터 종류 (TCP 송수신)
- Server(RoutingSim) -> Client : Json type 
1. 초기값 설정
```python
{
    'msg' : "Input Start Point x, y. (ex : 0, 0)",
    'recommendPath' : "-",
    'nextRecommend' : "-",
    'movingLog' : "-"
}
```

2. 추천 경로 (새로 생성될 때 마다 송신)
```python
{
    'msg': 'New Recommend Path', 
    'recommendPath': [[0, 1], [0, 2], [1, 2], [2, 2]], 
    'nextRecommand': '-', 
    'movingLog': '-'
}
```

3. 다음 이동 경로 추천
```python
{
    'msg': 'Input Next Command : ', 
    'recommendPath': '-', 
    'nextRecommand': 
        {
            'command': 'back', 
            'location': [0, 1]
        }, 
    'movingLog': '-'
}
```

4. 도착
```python
{
    'msg': 'Goal!', 
    'recommendPath': '-', 
    'nextRecommand': '-', 
    'movingLog': [[0, 0], [0, 1], [0, 2], [0, 1], [1, 1], [1, 2], [2, 2]]
}
```


- Client -> Server(RoutingSim) :
1. 초기값 입력
```python
Server : "Input Start Point x, y. (ex : 0, 0)"

Input Your Message : 0,0

Server : "Input End Point x, y. (ex : 2, 2)"

Input Your Message : 2,2
```

2. 로봇 조작
```python
Server : 'Input Next Command'
Input Your Message : s
```

- 조작을 위해서는 key_binding.json에 명시된 키 사용 필요
```python
# key_binding.json
{
    "w" : "front",
    "s" : "back",
    "a" : "left",
    "d" : "right"
}
```