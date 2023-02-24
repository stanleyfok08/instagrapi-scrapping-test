# %%
"""
Function: 
Download profile pic and most liked pic from IG

1. download profile pic
1. download most liked pic

Created on 2023/01/04  updated 2023/01/20

Requirement:
- instagrapi version 1.16.30

@author: Stanley Fok
"""

# %%
from instagrapi import Client
from instagrapi.exceptions import ClientThrottledError, LoginRequired, UserNotFound, ClientRequestTimeout, PleaseWaitFewMinutes
import time, random, os
import pandas as pd

# %%
# for Instagrapi API functions
cl = Client()

# %%
def change_password_handler():
    # Simple way to generate a random string
    chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
    password = "".join(random.sample(chars, 8))
    return password

# %%
def login_instagrapi(account_file):
    # edit pass.txt to edit the credentials
    with open(account_file, "r") as pwd:
        insta_username = pwd.readline()  # 1st line is username
        print(insta_username)
        insta_password = pwd.readline()  # 2nd line is password
    
    new_pass = change_password_handler()
    # print("new pass is",new_pass)
    cl.change_password_handler = new_pass

    cl.login(insta_username, insta_password)

# %%
def wait():
    wait_time = random.randint(150,240)
    print("now wait", wait_time, "seconds...")
    time.sleep(wait_time)

# %%
def wait_short():
    wait_time = random.randint(20,40)
    print("now wait", wait_time, "seconds...")
    time.sleep(wait_time)

# %%
def get_user_most_liked_post(user_id,amount):
    current_id = 0
    current_max_like = 0
    
    list = cl.user_medias(user_id,amount)

    if len(list) < 1:
        print("account exists, but no medias")
        return -1,-1    
    
    wait_short()

    # print("user ID is",id)

    for m in list:
        media = m.dict()

        if media["like_count"] >= current_max_like and media["media_type"] == 1: # only count if it is a photo and has more like than previous photo
            # print(media["pk"], "has", media["like_count"], "likes")
            current_id = media["pk"]
            current_max_like = media["like_count"]
    
    if current_id == 0:
        print("account exists, but account does not post photos, only videos or other format")
        return -2,-2
    
    print("returning most liked post is:", current_id, ", it has", current_max_like,"likes")
    return current_id, current_max_like

# %%
recovered = False

try:
    df = pd.read_csv("0 Database - in process.csv")
    print("use the last modified csv")
    recovered = True
except:
    df = pd.read_csv("0 Database.csv")
    print("use the fresh csv")
    
    df["IG page exist"] = "" # add new column
    df["IG user ID"] = "" # add new column
    df["IG profile pic url"] = "" # add new column

# %%
# login to API
login_instagrapi("pass.txt")

# %%
if not os.path.exists('profile'):
    os.makedirs('profile')

# %%
# prevent over requesting
if recovered == True:
    df2 = df.loc[df['IG page exist'] == True]
    completed_list = df2['IG'].dropna().to_list()
else:
    completed_list = list()

# %%
request_times = 0

# %%
# get user info and save it
for index, rows in df.iterrows():   
    # if want to start in the middle instead   
    if index < 316: continue

    # page already processed, skip
    if (rows["IG"] in completed_list):
        print("already processed")
        continue

    # IG is blank, skip
    if (rows["IG"] != rows["IG"]):
        print("blank entry")
        continue

    # already get the info, skip
    if recovered == True:
        if(rows["IG user ID"] == rows["IG user ID"] or rows["IG profile pic url"] == rows["IG profile pic url"]):            
            print("already processed")
            continue

    # more wait time at an interval of 5
    if request_times % 5 == 0 and request_times > 0: wait_short()

    print("now processing",(rows["IG"]), "index", index)

    # download profile pic, if fail, that means account does not exist
    try:
        current_user = cl.user_info_by_username(rows["IG"]).dict()
        request_times += 1
        
        df.loc[index, 'IG page exist'] = True
        df.loc[index, 'IG user ID'] = current_user["pk"]
        df.loc[index, 'IG profile pic url'] = current_user["profile_pic_url_hd"]
        completed_list.append(rows["IG"])
        print(rows["IG"],"success")

    except PleaseWaitFewMinutes:
        print("limit reached, last index is", index,". Try again later.")
        # cl.logout()
        break
    
    except UserNotFound:
        print("this account does not exist")
        df.loc[index, 'IG page exist'] = False
        df.loc[index, 'IG user ID'] = 0
        df.loc[index, 'IG profile pic url'] = "No"
    
    except LoginRequired:
        cl.relogin()
        break

    except Exception as e:
        print(e, " ERROR: not handled")
        break

    wait_short()     
    wait_short()     
    print("\n")
    
    # early termination
    # if index > 300: break

# %%
df.to_csv("0 Database - in process.csv")


# %%
# for profile pic and most recent pic, may take very long
for index, rows in df.iterrows():   
    # if want to start in the middle instead   
    # if index < 72: continue

    # if url does not exist, skip
    if (rows["IG profile pic url"] != rows["IG profile pic url"]) or (rows["IG"] != rows["IG"]) or (rows["IG page exist"] == False): continue

    # if profile pic already downloaded, skip
    path = "profile\\" + rows["IG"] + "_profile.jpg"
    if(os.path.exists(path) == True):
        # print("already downloaded", rows["IG"])
        continue

    print("now processing",(rows["IG"]), "index", index)        

    # download profile pic, if fail, that means account does not exist
    try:
        profile_pic_url = rows["IG profile pic url"]
        path = "profile\\" + rows["IG"] + "_profile"
        p = cl.photo_download_by_url(profile_pic_url,path)
        
        print(rows["IG"],"downloaded to",p)
        # completed_list.append(rows["IG"])

    except Exception as e:
        print(e,"cannot download",index)

    print("\n")
    wait_short()     
    #wait_short()     
    
    # early termination
    # if index > 10: break

# %%
df.to_csv("0 Database - verified IG links and profile pic downloaded.csv")

# %%
df["IG post status"] = "" # add new column

# %%
# fetch this number of posts only
amount = 30

# %%
if not os.path.exists('media'):
    os.makedirs('media')

# %%
# for profile pic and most recent pic, may take very long
for index, rows in df.iterrows():      
    # if want to start in the middle instead   
    # if index < 20: continue

    # if url does not exist, skip
    if (rows["IG profile pic url"] != rows["IG profile pic url"]) or (rows["IG"] != rows["IG"]) or (rows["IG page exist"] == False): continue

    print("now processing",(rows["IG"]), "index", index)

    # download most popular pic
    post_id, post_like = get_user_most_liked_post(user_id=rows["IG user ID"],amount=amount)

    # pass if page does not have any photos
    if post_id == -1:        
        df.loc[index, 'IG post status'] = "No medias"       
        wait_short()
        continue
    elif post_id == -2:
        df.loc[index, 'IG post status'] = "No static photos"  
        wait_short()
        continue

    wait_short()
    
    # download most liked photo
    try:
        p = cl.photo_download(post_id,folder="media")
        print(rows["IG"],"downloaded to",p)    
        df.loc[index, 'IG post status'] = "Good"
    except Exception as e:        
        print(e,"cannot download")

    print("\n")
    wait_short()
    
    # if index > 0: break

# %%
df.to_csv("0 Database - verified IG links and profile pic downloaded - most liked pic downloaded.csv")

# %%
cl.logout()


