#Version V04
#This code has been made by J&J_Ian1515 under the GPL license. Any commercial usage is excluded.
#Source : 
import urllib
import urllib.parse
import urllib.request
import base64
import xml.etree.ElementTree
import json
import datetime

#============== Zone de Personnalisation ====================== 



LOGIN = "votre Login MySolisArt"
PASS = "votre mot de passe MySolisArt"
ID = "l'identifiant de votre instalation"




#============== Fin Zone de Personnalisation - Ne rien toucher en dehors de cette zone ====================== 

DOMAIN = "https://my.solisart.fr"
URL_DATA = "/admin/divers/ajax/lecture_valeurs_donnees.php"
URL_DICT = "/admin/divers/js/solisart/commun-donnees.1702435180.js"
IHM = "admin"
CONNEXION = "Se Connecter"
usefulData = [ i for i in range(584,629) ]

login = {'id': LOGIN, 'pass': PASS, 'ihm': IHM, 'connexion': CONNEXION}
loginbytes = urllib.parse.urlencode(login).encode()

def getDataDict(domain=DOMAIN):
    resp = urllib.request.urlopen("{domain}{path}".format(domain=domain, path=URL_DICT))
    data = resp.readlines()
    data_definitions = [l.decode() for l in data if b'const donnee_' in l]
    return { int(l.split('=')[1].split(';')[0]):''.join(l.split("=")[0].split('_')[1:]) for l in data_definitions }

def logInSolisart(LOGIN,PASS, domain=DOMAIN):
    loginRequest = urllib.request.Request("{domain}{path}".format(domain=domain, path="/"), data=loginbytes, method='POST')
    loginRequest.add_header("Content-Type", "application/x-www-form-urlencoded")
    loginResponse = urllib.request.urlopen(loginRequest, loginbytes)
    cookie = loginResponse.getheader("Set-Cookie").split(";")[0]
    loginRequest.add_header("Cookie", cookie)
    urllib.request.urlopen(loginRequest, loginbytes)
    return cookie

def getValues(cookie, id, domain=DOMAIN):
    requestData = {
        'id': base64.b64encode(id.encode()).decode(),
        'heure': 0,
        'periode': 5
    }
    requestDataBytes = urllib.parse.urlencode(requestData).encode()
    req = urllib.request.Request("{domain}{path}".format(domain=domain, path=URL_DATA), data=requestDataBytes, method='POST')
    req.add_header("Cookie", cookie)
    resp = urllib.request.urlopen(req, requestDataBytes)
    data = resp.read()
    return data

def clean(key,value):
    if key[:2] == "rl":
        return value
    if key[:2] == "fl" and value.lower() != "off":
        return float(value.rstrip(" Cdlmnp"))
    return value.rstrip(" Cdlmnp")

def manage_sensor():
    cookie,xmldata,xmlparsed = "","",""
    try:
        cookie = logInSolisart(LOGIN, PASS )
        xmldata = getValues(cookie, ID)
        donnee_conversion = getDataDict()
        xmlparsed = xml.etree.ElementTree.fromstring(xmldata)
        useful_values = [ {
            'heure': int(v.attrib['heure']),
            'code': int(v.attrib['donnee']),
            'donnee': donnee_conversion[int(v.attrib['donnee'])].strip(),
            'valeur': base64.b64decode(v.attrib['valeur'].encode()).decode()
        } for v in xmlparsed if int(v.attrib['donnee']) in usefulData ]
        returnData = {i["donnee"]: clean(i["donnee"],i["valeur"]) for i in useful_values}
        returnData["LastUpdate"] = datetime.datetime.now().isoformat(sep=' ', timespec="seconds")
        print(json.dumps(returnData))
    except:
        print(json.dumps({"DataSource": "ERROR"}))

if __name__ == "__main__":
    manage_sensor()