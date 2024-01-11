import requests
from flask import request, redirect, jsonify, make_response
from flask_restx import Namespace, Resource

from config import CLIENT_ID, REDIRECT_URI

oauth_api = Namespace(
    name='Kakaologin',
    description='API for Using Kakao login',
    path='/oauth/kakao'
)

@oauth_api.route("/") # 카카오로 로그인하기를 누르면 해당 api로 이동, redirect 통해 바로 request token을 받기 위해 링크 변경
class KakaoSignIn(Resource):
    def get(self):
        client_id = CLIENT_ID
        redirect_uri = REDIRECT_URI
        kakao_oauthurl = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        return redirect(kakao_oauthurl)

@oauth_api.route("/callback") # 위의 라우팅에서 redirect 되면서 바로 이 api로 오게 된다
class KakaoSignInCallback(Resource):
    def get(self):
        global access_token
        try:
            code = request.args.get("code") # callback 뒤에 붙어오는 request token을 뽑아낸다
            client_id = CLIENT_ID
            redirect_uri = REDIRECT_URI
            #Python에서 HTTP 요청을 보내는 모듈인 requests
            token_request = requests.get(
                f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
            )
            token_json = token_request.json() # 위의 get 요청을 통해 받아온 데이터를 json화 해주면 이곳에 access token이 숨어있다
            error = token_json.get("error", None)

            if error is not None:
                return make_response({"message":"INVALID CODE"}, 400) #에러 처리
            access_token = token_json.get("access_token") #카카오 로그인을 통해 유저에 대한 정보를 받을 권한이 있는 토큰

            # --- 여기까지 access token 받아오는 통신 ---

            # --- 아래 코드는 access token 기반으로 유저 정보 요청하는 통신

            profile_request = requests.get("https://kapi.kakao.com/v2/user/me", headers={"Authorization" : f"Bearer {access_token}"})

            profile_json = profile_request.json()

        except KeyError:
            return make_response({"message" : "INVALID_TOKEN"}, 400)

        except access_token.DoesNotExsist:
            return make_response({"message" : "INVALID TOKEN"}, 400)

        from apis.oauthdb import social_signin

        return social_signin(profile_json)

@oauth_api.route('/signout')
class kakao_sign_out(Resource):
    url = f"https://kauth.kakao.com/oauth/logout?client_id={CLIENT_ID}&logout_redirect_uri={REDIRECT_URI}"


