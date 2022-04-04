# minecraft Mod Translator
## (부제)영어가 딸려서 만든 모드 번역기

1. `모드`가 1개면 그냥 하겠는데 **pam's harvest**하다가 능지가 딸려 현타와서 만들었습니다.  
2. 해당 프로그램은 2가지 버전이 존재합니다. `구글 버전`과 `Papago 버전`입니다.  
3. 현재 `구글 버전`의 경우 `무료번역`은 가능하지만 중간 *timeout*뜨면 에러가 나서 그냥 예외처리로 영어가 그대로 들어가게 해놓았습니다.  
4. 대신 `Papago 버전`의 경우 머기업답게 준수한 퀄리티의 번역과 깔끔한 API의 도움으로 번역이 아주 잘되나 아쉽게도 돈이 들어가는 관계로 `N Cloud`에서 직접 API 키를 발급받아 사용해주시기 바랍니다. [Papago N Cloud 링크](https://www.ncloud.com/product/aiService/papagoTranslation)
5. 버전은 **branch**로 나눠놓았습니다.
  
# Requirements
1. commentjson==0.9.0  
pip install commentjson
2. googletrans==4.0.0rc1  
pip install googletrans==4.0.0rc1
# 사용방법
1. **mod**폴더에 번역하고자 하는 jar 모드 파일을 넣습니다.
2. (**cmd** or **powershell**) python main.py
3. 열심히 기다립니다.
4. **translated_mod**에 번역된 jar 모드 파일이 있을겁니다.
5. 이제 그 모드파일을 가져다 적용하고 즐기세요!  
![0](./mdimg/01.png)
# 잡담
제가 생각해도 기능구현만 우선시해서 가독성이 겁나 구린데 죄송합니다.  
아직 parameter도 설정파일로 안만들었고 UI도 없는데 직장인이라 업데이트가 많이 늦어요.  
혹시라도 이 프로그램을 사용하시고 수정이나 이슈를 알려주시면 최대한 빨리 반영하도록 하겠습니다.  
영알못들아... 나에게 힘을 줘..!!