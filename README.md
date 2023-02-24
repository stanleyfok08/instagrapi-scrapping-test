# instagrapi-scrapping-test

Function: 
Download profile pic and most liked pic from IG using a list in a csv

1. download profile pic
2. download most liked pic

Created on 2023/01/04  updated 2023/01/20

Requirement:
- instagrapi version 1.16.30
- a csv named "0 Database.csv" with columns "IG" for IG username

Also, the python script may will trigger "too many request" from IG and need to wait a couple hours to continue if that happened (changing account won't work). I tried changing proxy, but it give another error instead of "too many request".

But, if IG request a Recaptcha check when running the program, and I manually login to IG in the browser (the api don't have a solution to this), there is no "too many request" anymore. I have no idea how did I trigger this. This only happened one time during the whole coding process.

by Stanley Fok
