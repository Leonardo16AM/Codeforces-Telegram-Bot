import requests
import numpy as np
from skimage import io
import time
import termcolor as tc
import matplotlib.pyplot as plt
import os



class Error(Exception):
    pass
class User_not_found(Error):
    pass
class Contest_not_found(Error):
    pass


cf = "http://codeforces.com/api/"
def call(method, params):
    url = f"{cf}{method}"
    req = requests.get(url, params=params)
    if req.status_code == 200:
        return req.json()






def get_user_info(usr):
    ret=str("")
    try:
        url="https://codeforces.com/api/user.info"

        resp=requests.get(url,params={"handles":usr})

        if resp.json()['status']!='OK':
            raise User_not_found('Not found user on codeforces.com')
        user=resp.json()["result"][0]
        ret+=f"User: *{usr}*\n"
        if user.get('rank')!=None: ret+=f"Rank: *{user['rank']}*\n"
        if user.get('firstName')!=None : ret+=f"Name: {user['firstName']} {user['lastName']}\n"
        if user.get('rating')!=None: ret+=f"Rating: {user['rating']}\n"
        if user.get('maxRating')!=None: ret+=f"Max Rating: {user['maxRating']}\n"
        if user['contribution']!='': ret+=f"Contribution: {user['contribution']}\n"
        if user.get("country")!=None :ret+=f"Country: {user['country']}\n"
        if user.get("city")!=None :ret+=f"City: {user['city']}\n"
        if user.get("organization")!=None:
            if user.get("organization")!="":
                ret+=f"Organization: {user['organization']}\n"
    except Exception:
        if resp.json()['status']!='OK':
            raise User_not_found('Not found user on codeforces.com')

    return ret






def get_user_last_acc_submits(usr):
    ret=str('')
    try:
        url="https://codeforces.com/api/user.status"

        resp=requests.get(url,params={"handle":usr,
                                        "from":1,
                                        "count":100})
        
        if resp.json()['status']!='OK':
            raise User_not_found('Not found user on codeforces.com or any other error')
        cnt=0;
        for subm in resp.json()['result']:
            if subm['verdict']!='OK':continue
            ret+=f"{subm['contestId']}"
            ret+=f"{subm['problem']['index']} - "
            ret+=f"{subm['problem']['name']:>2}\n"
            cnt+=1
            if cnt==10: break
        if cnt==0:
            ret='User with no accepted submitions'
    except Exception:
        if resp.json()['status']!='OK':
            raise User_not_found('Not found user on codeforces.com or any other error')

    return ret








def pos_rat_change(contest_id,usr_rank,usr_rating):
    '''Returns psoible rating change in form of a string'''
    contest_id=int(contest_id)
    usr_rank=int(usr_rank)
    usr_rating=int(usr_rating)
    try:
        data=call("contest.ratingChanges", {"contestId": contest_id})["result"]
        same_rating=[]

        for user in data:
            rank=user["rank"]
            rating=user["oldRating"]
            delta=user["newRating"]-user["oldRating"]
            if abs(usr_rating-rating)<=3 :
                if rank==usr_rank:
                    return f"Predicted rating change: ```{delta}```"
                same_rating.append( [abs(usr_rank-rank),rank,delta] )


        same_rating.sort()

        a=same_rating[0]
        b=same_rating[1]

        for user in same_rating:
            if user==1 :continue
            if user[1]!=same_rating[0][1]:
                b=user
                break


        M=(b[2]-a[2])/(b[1]-a[1])
        B=a[2]-M*a[1]


        return f"Predicted rating change: ```{int(M*usr_rank+B)}```"

    except Exception as error:
        print(error)
        return "Unpredictible"








def get_table_rank_delta(cont_id):
    try:
        rating = [[1200, "gray"],
                [1400, "green"],
                [1600, "#03a89e"],
                [1900, "blue"],
                [2100, "#aa00aa"],
                [2400, "orange"],
                [3000, "red"],
                [9999, "black"]]
        data = call("contest.ratingChanges", {"contestId": cont_id})["result"]
        title = data[0]["contestName"]
        x = []
        delta = np.zeros((len(data),), dtype=np.int64)
        color = []
        for i in range(len(data)):
            delta[i] = data[i]["newRating"] - data[i]["oldRating"]
            x.append(data[i]["rank"])
            for j in range(len(rating)):
                if data[i]["oldRating"] < rating[j][0]:
                    color.append(rating[j][1])
                    break
        plt.figure(figsize=(8, 6))
        plt.title(title)
        plt.xlabel("Rank")
        plt.ylabel("Delta Rate")
        plt.yticks(np.arange(-300, 301, 50))
        plt.ylim(-300, 300)
        plt.grid()
        plt.scatter(x, delta, s=0.5, c=color)
        plt.savefig(str(cont_id)+".jpg")
        plt.close()
    except Exception:
            raise Contest_not_found('Contest not found on codeforces.com or any other error')



def get_table_rank_new_rating(cont_id):
    try:
        rating = [[1200, "gray"],
                [1400, "green"],
                [1600, "#03a89e"],
                [1900, "blue"],
                [2100, "#aa00aa"],
                [2400, "orange"],
                [3000, "red"],
                [9999, "black"]]
        data = call("contest.ratingChanges", {"contestId": cont_id})["result"]
        title = data[0]["contestName"]
        x = []
        delta = np.zeros((len(data),), dtype=np.int64)
        color = []
        for i in range(len(data)):
            delta[i] = data[i]["newRating"]
            x.append(data[i]["rank"])
            for j in range(len(rating)):
                if data[i]["newRating"] < rating[j][0]:
                    color.append(rating[j][1])
                    break
        plt.title(title)
        plt.xlabel("Rank")
        plt.ylabel("New Rating")
        plt.grid()
        plt.scatter(x, delta, s=0.5, c=color)
        plt.savefig(str(cont_id)+"B.jpg")
        plt.close()
    except Exception:
            raise Contest_not_found('Contest not found on codeforces.com or any other error')







def get_table_rank_old_rating(cont_id):
    try:
        rating = [[1200, "gray"],
                [1400, "green"],
                [1600, "#03a89e"],
                [1900, "blue"],
                [2100, "#aa00aa"],
                [2400, "orange"],
                [3000, "red"],
                [9999, "black"]]
        data = call("contest.ratingChanges", {"contestId": cont_id})["result"]
        title = data[0]["contestName"]
        x = []
        delta = np.zeros((len(data),), dtype=np.int64)
        color = []
        for i in range(len(data)):
            delta[i] = data[i]["oldRating"]
            x.append(data[i]["rank"])
            for j in range(len(rating)):
                if data[i]["oldRating"] < rating[j][0]:
                    color.append(rating[j][1])
                    break
        plt.title(title)
        plt.xlabel("Rank")
        plt.ylabel("Old Rating")
        plt.grid()
        plt.scatter(x, delta, s=0.5, c=color)
        plt.savefig(str(cont_id)+"C.jpg")
        plt.close()
    except Exception:
            raise Contest_not_found('Contest not found on codeforces.com or any other error')






urlupd="https://api.telegram.org/< Your bot token >/getUpdates"
urlsendpic="https://api.telegram.org/< Your bot token >/sendPhoto"
urlsendmes="https://api.telegram.org/< Your bot token >/sendMessage"


resp=requests.get(urlupd)
print(resp.status_code)
print(resp.json())
print(get_user_info("Leonardo16"))
print(tc.colored(" >>> Starting sever...",color="green"))



last=0
prev={}

while True:
    try:
        resp=requests.get(urlupd,params={'offset':last}).json()['result']

        for request in resp:
            last=request['update_id']+1
            try:

                if request['message']['text']=='/start':
                    try:
                        print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                    except Exception:
                        print(f"{request['update_id']} Unknown {request['message']['text']}")

                    requests.get(urlsendmes,params={'parse_mode':'Markdown',
                                                    "chat_id":request['message']['chat']['id'],
                                                    "text":"Welcome to codeforces grapher bot. Press '/' to see commands. Creator: @Leonardo16AM. If it doesnt works or any other problem is because it is still in production, sorry for the inconveniences."})

                    prev[request['message']['chat']['id']]=None
                    continue

                if request['message']['text']=='/user_info' or request['message']['text']=="/user_info@codeforces_test_bot":
                    try:
                        print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                    except Exception:
                        print(f"{request['update_id']} Unknown {request['message']['text']}")


                    requests.get(urlsendmes,params={'parse_mode':'Markdown',
                                                    "chat_id":request['message']['chat']['id'],
                                                    "text":"Send user handle"})
                    prev[request['message']['chat']['id']]="user_info"
                    continue


                if request['message']['text']=='/posible_rating_change'or request['message']['text']=="/posible_rating_change@codeforces_test_bot":
                    try:
                        print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                    except Exception:
                        print(f"{request['update_id']} Unknown {request['message']['text']}")


                    requests.get(urlsendmes,params={'parse_mode':'Markdown',
                                                    "chat_id":request['message']['chat']['id'],
                                                    "text":'Send contest id, rank (without unofficials) and old rating( Separated by commas without blank spaces). Example: "1428,620,2064" '})

                    prev[request['message']['chat']['id']]="posible_rating_change"
                    continue

                if request['message']['text']=='/last_acc'or request['message']['text']=="/last_acc@codeforces_test_bot":
                    try:
                        print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                    except Exception:
                        print(f"{request['update_id']} Unknown {request['message']['text']}")


                    requests.get(urlsendmes,params={'parse_mode':'Markdown',
                                                    "chat_id":request['message']['chat']['id'],
                                                    "text":"Send user handle"})

                    prev[request['message']['chat']['id']]="last_acc"
                    continue


                if request['message']['text']=='/table_rank_delta'or request['message']['text']=="/table_rank_delta@codeforces_test_bot":
                    try:
                        print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                    except Exception:
                        print(f"{request['update_id']} Unknown {request['message']['text']}")


                    requests.get(urlsendmes,params={'parse_mode':'Markdown',
                                                    "chat_id":request['message']['chat']['id'],
                                                    "text":"Send contest id"})

                    prev[request['message']['chat']['id']]="table_rank_delta"
                    continue


                if request['message']['text']=='/table_rank_old_rating'or request['message']['text']=="/table_rank_old_rating@codeforces_test_bot":
                    try:
                        print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                    except Exception:
                        print(f"{request['update_id']} Unknown {request['message']['text']}")


                    requests.get(urlsendmes,params={'parse_mode':'Markdown',
                                                    "chat_id":request['message']['chat']['id'],
                                                    "text":"Send contest id"})

                    prev[request['message']['chat']['id']]="table_rank_old_rating"
                    continue


                if request['message']['text']=='/table_rank_new_rating'or request['message']['text']=="/table_rank_new_rating@codeforces_test_bot":
                    try:
                        print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                    except Exception:
                        print(f"{request['update_id']} Unknown {request['message']['text']}")


                    requests.get(urlsendmes,params={'parse_mode':'Markdown',
                                                    "chat_id":request['message']['chat']['id'],
                                                    "text":"Send contest id"})

                    prev[request['message']['chat']['id']]="table_rank_new_rating"
                    continue










                if prev.get(request['message']['chat']['id'])=="user_info":
                    try:
                        usr=request['message']['text']

                        try:
                            print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                        except Exception:
                            print(f"{request['update_id']} Unknown {request['message']['text']}")

                        requests.get(urlsendmes,params={'parse_mode':'Markdown',
                                                        "chat_id":request['message']['chat']['id'],
                                                        "text":get_user_info(usr)})

                        prev[request['message']['chat']['id']]=None
                    except User_not_found as error :
                        requests.get(urlsendmes,params={"chat_id":request['message']['chat']['id'],
                                                        "text":error})
                    continue

                if prev.get(request['message']['chat']['id'])=="last_acc":
                    try:
                        usr=request['message']['text']
                        try:
                            print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                        except Exception:
                            print(f"{request['update_id']} Unknown {request['message']['text']}")
                        requests.get(urlsendmes,params={"chat_id":request['message']['chat']['id'],
                                                        "text":get_user_last_acc_submits(usr)})
                        prev[request['message']['chat']['id']]=None
                    except User_not_found as error :
                        requests.get(urlsendmes,params={"chat_id":request['message']['chat']['id'],
                                                        "text":error})
                    continue


                if prev.get(request['message']['chat']['id'])=="table_rank_delta":
                    try:
                        contest=request['message']['text']
                        try:
                            print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                        except Exception:
                            print(f"{request['update_id']} Unknown {request['message']['text']}")

                        get_table_rank_delta(contest)
                        resp=requests.get(urlsendpic,files={"photo":open(contest+".jpg","rb")},params={"chat_id":request['message']['chat']['id']})
                        os.remove(contest+".jpg")
                        prev[request['message']['chat']['id']]=None
                    except Contest_not_found as error :
                        requests.get(urlsendmes,params={"chat_id":request['message']['chat']['id'],
                                                        "text":error})
                    continue


                if prev.get(request['message']['chat']['id'])=="table_rank_old_rating":
                    try:
                        contest=request['message']['text']
                        try:
                            print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                        except Exception:
                            print(f"{request['update_id']} Unknown {request['message']['text']}")

                        get_table_rank_old_rating(contest)
                        resp=requests.get(urlsendpic,files={"photo":open(contest+"C.jpg","rb")},params={"chat_id":request['message']['chat']['id']})
                        os.remove(contest+"C.jpg")
                        prev[request['message']['chat']['id']]=None
                    except Contest_not_found as error :
                        requests.get(urlsendmes,params={"chat_id":request['message']['chat']['id'],
                                                        "text":error})
                    continue

                if prev.get(request['message']['chat']['id'])=="table_rank_new_rating":
                    try:
                        contest=request['message']['text']
                        try:
                            print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                        except Exception:
                            print(f"{request['update_id']} Unknown {request['message']['text']}")

                        get_table_rank_new_rating(contest)
                        resp=requests.get(urlsendpic,files={"photo":open(contest+"B.jpg","rb")},params={"chat_id":request['message']['chat']['id']})
                        os.remove(contest+"B.jpg")
                        prev[request['message']['chat']['id']]=None
                    except Contest_not_found as error :
                        requests.get(urlsendmes,params={"chat_id":request['message']['chat']['id'],
                                                        "text":error})
                    continue


                if prev.get(request['message']['chat']['id'])=="posible_rating_change":
                    try:
                        text=request['message']['text']
                        try:
                            print(f"{request['update_id']} {request['message']['from']['username']} {request['message']['text']}")
                        except Exception:
                            print(f"{request['update_id']} Unknown {request['message']['text']}")

                        requests.get(urlsendmes,params={'parse_mode':'Markdown',
                                                            "chat_id":request['message']['chat']['id'],
                                                            "text":pos_rat_change(text.split(',')[0],text.split(',')[1],text.split(',')[2])})
                        prev[request['message']['chat']['id']]=None
                    except Exception as error:
                        requests.get(urlsendmes,params={"chat_id":request['message']['chat']['id'],'parse_mode':'Markdown',
                                                        "text":'Please send contest id, rank and old rating( *Separated by commas without blank spaces*). Example: "1428,620,2064" '})
                    continue



            except KeyError as error: print(tc.colored(error,color="red"))
    except Exception as error:
        print(tc.colored(error,color="red"))

    time.sleep(1)

