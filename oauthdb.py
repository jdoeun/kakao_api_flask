import jwt

from config import CLIENT_SECRET


def social_signin(profile_json):
    import app
    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email", None)
    nickname = kakao_account.get("nickname")
    kakao_id = str(profile_json.get("id"))

    User = {
        'email' : email,
        'nickname' : nickname,
        'kakao_id' : kakao_id
    }

    document = app.kakao_collection.find_one({'kakao_id':kakao_id}) #중복되면 찾아냄

    if document is None:
        app.kakao_collection.insert_one(User)
        token = jwt.encode({'id':kakao_id}, CLIENT_SECRET, algorithm="HS256")
        token = token.encode("utf-8").decode("utf-8")

        response_object = {
            'status' : 'success',
            'message' : 'You become a member of our service',
            'Authorization' : token
        }

        return response_object, 200

    else:
        token = jwt.encode({'id': kakao_id}, CLIENT_SECRET, algorithm="HS256")
        token = token.encode("utf-8").decode("utf-8")

        response_object = {
            'status' : 'already signin',
            'message' : 'You already our member. Login success',
            'Authorization': token
        }

        return response_object, 201

