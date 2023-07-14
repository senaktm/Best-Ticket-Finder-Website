from time import sleep
from flask import Flask, flash, redirect,render_template,request,url_for
from flask_pymongo import PyMongo
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup 
import os 
import pymongo
import requests
import undetected_chromedriver as uc
from wtforms import Form
from selenium.webdriver.chrome.options import Options
from bson import Binary

app = Flask(__name__)
app.secret_key = 'secretkey'

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb_login = myclient["userDB"]
mydb_sefer = myclient["busDb"]
mycollection_login = mydb_login["user_info"]
mycollection_sefer = mydb_sefer["tickets"]
mycollection_sehirler = mydb_login["sehirler_info"]

firma =""

lst_kalkis_yeri =[]
lst_varis_yeri =[]
lst_kalkis_saati =[]
lst_fiyat =[]
lst_metro_saat2 = []


url=""
sefer_lst =[]
tarih=""
resim_belgesi=""


@app.route("/",methods = ["GET","POST"])
def register():
    
    if request.method=='POST':

        email = request.form['email']
        sifre = request.form['sifre']
            # MongoDB sorgusu
        email2 = mycollection_login.find_one({'email': email})

        if email2:
        # Kullanıcı zaten varsa, hata mesajı gösterin
            error = 'Bu kullanıcı adı zaten kullanılıyor'
            return error
        else:
        # Kullanıcı yoksa, MongoDB'ye yeni bir kullanıcı ekleyin
            mycollection_login.insert_one({ 'email': email,'sifre': sifre   })
            return render_template("login.html")
    
    return render_template("login.html")
    
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    sifre = request.form['sifre']
     #MongoDB sorgusu
    user = mycollection_login.find_one({ 'email': email,'sifre': sifre })

    if user:
        # Kullanıcı doğrulandıysa
        return redirect(url_for('index',sehirler=GET_SEHIRLER(),sehirlerLen=len(GET_SEHIRLER())))
    else:
        # Kullanıcı doğrulanamazsa, hata mesajı gösterin
        error = 'Geçersiz kullanıcı adı veya şifre'
    return render_template("login.html")
       




@app.route("/index",methods = ["GET","POST"])
def index():

    myclient.drop_database("busDb")

    lst_kalkis_yeri.clear()
    lst_varis_yeri.clear()
    lst_kalkis_saati.clear()
    lst_fiyat.clear()
    lst_metro_saat2.clear()

    sefer_lst.clear()


    if request.method=='POST':
        
        
        kalkis_yeri = request.form.get('exampleDataList')
        varis_yeri = request.form.get('exampleDataList2')
        tarih = request.form.get('gidisTarihi')


        
        kalkisyeri = kalkis_yeri
        varisyeri = varis_yeri
        tarihsaat = tarih
        
        

        PAMUKKALE_SCRAPING(kalkisyeri,varisyeri,tarihsaat)
        METRO_SCRAPING(kalkisyeri,varisyeri,tarihsaat)
        VARAN_SCRAPING(kalkisyeri,varisyeri,tarihsaat)



        return redirect(url_for("biletSonuc",
                            resim_belgesi=resim_belgesi,
                            sefer_lst=sefer_lst
        ))

     
 
    return render_template("index.html",sehirler=GET_SEHIRLER(),sehirlerLen=len(GET_SEHIRLER()))
           
def METRO_SCRAPING(kalkisyeri,varisyeri,tarihsaat):
        lst_kalkis_yeri.clear()
        lst_varis_yeri.clear()
        lst_kalkis_saati.clear()
        lst_fiyat.clear()
        firma="metro"
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--disable-popup-blocking')      
        driver = uc.Chrome(options=chrome_options)
        url ='https://www.metroturizm.com.tr/otobus-bileti/{kalkisyeri}-{varisyeri}?date={tarihsaat}&tw=0'.format(kalkisyeri = kalkisyeri,varisyeri=varisyeri,tarihsaat=tarihsaat)
        driver.get(url)
        sleep(10)


        metro_kalkis = driver.find_elements("xpath",'//span[@class="start ng-binding"]')

        if(len(metro_kalkis)==0):
             return ""
        else:
                    for kalkisIndex in metro_kalkis:
                        if(kalkisIndex.text!=""):
                            lst_kalkis_yeri.append(kalkisIndex.text)



                    metro_saat = driver.find_elements("xpath",'//span[@class="journey-item-hour ng-binding"]')
                    for saatIndex in metro_saat:
                        if(saatIndex.text!=""):
                            lst_kalkis_saati.append(saatIndex.text)
                            lst_metro_saat2=lst_kalkis_saati[::2]


                    metro_varis = driver.find_elements("xpath",'//span[@class="end ng-binding"]')
                    for varisIndex in metro_varis:
                        if(varisIndex.text!=""):
                            lst_varis_yeri.append(varisIndex.text)


                    metro_fiyat = driver.find_elements("xpath",'//span[@class="price ng-binding"]')
                    for fiyatIndex in metro_fiyat:
                        if(fiyatIndex.text!=""):
                            lst_fiyat.append(fiyatIndex.text)


                    resim_belgesi = 'metro.jpg'
                    for i in range(len(lst_kalkis_yeri)):
                        sefer_lst.append(resim_belgesi)
                        sefer_lst.append(firma)
                        sefer_lst.append(lst_kalkis_yeri[i])
                        sefer_lst.append(lst_varis_yeri[i])
                        sefer_lst.append(tarihsaat)
                        sefer_lst.append(lst_metro_saat2[i])
                        sefer_lst.append(lst_fiyat[i])
                        sefer_lst.append(url)
                    SAVE_MONGODB(firma,lst_kalkis_yeri,lst_varis_yeri,lst_fiyat,tarihsaat,lst_metro_saat2,resim_belgesi,url)
                    driver.close()

        


def PAMUKKALE_SCRAPING(kalkisyeri,varisyeri,tarihsaat):
        lst_kalkis_yeri.clear()
        lst_varis_yeri.clear()
        lst_kalkis_saati.clear()
        lst_fiyat.clear()
        firma="pamukkale"
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--disable-popup-blocking')
        
        driver = uc.Chrome(options=chrome_options)
        

        url='https://www.pamukkale.com.tr/bilet/{kalkisyeri}-{varisyeri}-otobus-bileti/{tarihsaat}/'.format(kalkisyeri = kalkisyeri,varisyeri=varisyeri,tarihsaat=tarihsaat)
        driver.get(url)
        sleep(10)
        
        bus_rows = driver.find_elements("xpath",'//div[@class="col-md-2 col-xs-3 sefer-list-kutu-tarih koltuk-secmobile"]')
        if(bus_rows==""):
            return ""
        else:
            for WebElement in bus_rows:
                elementHtml = WebElement.get_attribute('outerHTML')
                elementSoup = BeautifulSoup(elementHtml,'html.parser')
                temp_kalkis_saati = elementSoup.find("div",{"class":"sefersaat"})
                lst_kalkis_saati.append(temp_kalkis_saati.text)







            for i in range(0,len(lst_kalkis_saati)):
                bus_rows = driver.find_elements("xpath",'//*[@id="gidisBoxSticky"]/div[2]/div[{}]/div[3]/p[2]'.format(i+1))
                for WebElement in bus_rows:
                    elementHtml = WebElement.get_attribute('outerHTML')
                    elementSoup = BeautifulSoup(elementHtml,'html.parser')
                    temp_fiyat = elementSoup.find("p",{"class":"internetfiyat"})
                    lst_fiyat.append(temp_fiyat.text)



            bus_rows = driver.find_elements("xpath",'//*[@id="gidis-box"]/h1/span[3]')
    
            for i in range(0,len(lst_kalkis_saati)):
                for WebElement in bus_rows:
                  elementHtml = WebElement.get_attribute('outerHTML')
                  elementSoup = BeautifulSoup(elementHtml,'html.parser')
                  temp_kalkis_yeri = elementSoup.find("span",{"class":"hidden-lg hidden-md"})
                  lst_kalkis_yeri.append(temp_kalkis_yeri.text.strip('\n\t'))



            bus_rows = driver.find_elements("xpath",'//*[@id="gidis-box"]/h1/span[5]')

            for i in range(0,len(lst_kalkis_saati)):
                for WebElement in bus_rows:
                    elementHtml = WebElement.get_attribute('outerHTML')
                    elementSoup = BeautifulSoup(elementHtml,'html.parser')
                    temp_varis_yeri = elementSoup.find("span",{"class":"hidden-lg hidden-md"})
                    lst_varis_yeri.append(temp_varis_yeri.text.strip('\n\t'))


            resim_belgesi = 'pamukkale.png' # resim.jpg dosyasını binary veriye dönüştürerek sakla}
            for i in range(len(lst_kalkis_yeri)):
                sefer_lst.append(resim_belgesi)
                sefer_lst.append(firma)
                sefer_lst.append(lst_kalkis_yeri[i])
                sefer_lst.append(lst_varis_yeri[i])
                sefer_lst.append(tarihsaat)
                sefer_lst.append(lst_kalkis_saati[i])
                sefer_lst.append(lst_fiyat[i])
                sefer_lst.append(url)


            SAVE_MONGODB(firma,lst_kalkis_yeri,lst_varis_yeri,lst_fiyat,tarihsaat,lst_kalkis_saati,resim_belgesi,url)
            driver.close()

def VARAN_SCRAPING(kalkisyeri,varisyeri,tarihsaat):
        lst_kalkis_yeri.clear()
        lst_varis_yeri.clear()
        lst_kalkis_saati.clear()
        lst_fiyat.clear()
        firma="varan"
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--disable-popup-blocking')
        
        driver = uc.Chrome(options=chrome_options)
        
        url ='https://www.varan.com.tr/otobus-bileti/{kalkisyeri}/{varisyeri}/{tarihsaat}?rezC'.format(kalkisyeri = kalkisyeri,varisyeri=varisyeri,tarihsaat=tarihsaat)
        driver.get(url)
        sleep(10)


        
        varan_kalkis = driver.find_elements("xpath",'//div[@class="bos mb-2"]')

        if(len(varan_kalkis)==0):
             return ""
        else:
                    for kalkisIndex in varan_kalkis:
                        if(kalkisIndex.text!=""):
                            lst_kalkis_yeri.append(kalkisIndex.text)

                    varan_saat = driver.find_elements("xpath",'//div[@class="time"]')
                    for saatIndex in varan_saat:
                        if(saatIndex.text!=""):
                            lst_kalkis_saati.append(saatIndex.text)

                    varan_varis = driver.find_elements("xpath",'//div[@class="dolu"]')
                    for varisIndex in varan_varis:
                        if(varisIndex.text!=""):
                            lst_varis_yeri.append(varisIndex.text)


                    varan_fiyat = driver.find_elements("xpath",'//div[@class="order-5 order-lg-6 tab6"]')
                    for fiyatIndex in varan_fiyat:
                        if(fiyatIndex.text!=""):
                            lst_fiyat.append(fiyatIndex.text)


                    resim_belgesi = 'varan.jpg'
                    for i in range(len(lst_kalkis_yeri)):
                        sefer_lst.append(resim_belgesi)
                        sefer_lst.append(firma)
                        sefer_lst.append(lst_kalkis_yeri[i])
                        sefer_lst.append(lst_varis_yeri[i])
                        sefer_lst.append(tarihsaat)
                        sefer_lst.append(lst_kalkis_saati[i])
                        sefer_lst.append(lst_fiyat[i])
                        sefer_lst.append(url)
                    SAVE_MONGODB(firma,lst_kalkis_yeri,lst_varis_yeri,lst_fiyat,tarihsaat,lst_kalkis_saati,resim_belgesi,url)
                    driver.close()

        
        
        
        
@app.route("/biletSonuc",methods = ["GET","POST"])
def biletSonuc():

    sefer_lst=request.args.getlist('sefer_lst')

   
    if len(sefer_lst)!=0:
        


        if request.method == 'POST':

            filtre = request.form['filtre']
            if filtre == "artan":
                sefer_lst.clear()

                sort=list(mycollection_sefer.find({}, {'_id': 0}).sort("fiyat",1))
                for i in sort:
                    sefer = list(i.values())  # Sadece değerleri al
                    for value in sefer:
                         sefer_lst.append(value)      
                return render_template("biletSonuc.html",sefer_lst=sefer_lst,sortdatalen=len(sefer_lst))
            elif filtre == "azalan":
                sefer_lst.clear()
                sort=list(mycollection_sefer.find({}, {'_id': 0}).sort("fiyat",-1))
                for i in sort:
                    sefer = list(i.values())  # Sadece değerleri al 
                    for value in sefer:
                         sefer_lst.append(value)  
                return render_template("biletSonuc.html",sefer_lst=sefer_lst,sortdatalen=len(sefer_lst))
            
    return render_template("biletSonuc.html",
                            sefer_lst=sefer_lst,
                            sortdatalen=len(sefer_lst))
    
       
     
def SAVE_MONGODB(firma,lst_kalkis_yeri,lst_varis_yeri,lst_fiyat,tarih,lst_kalkis_saati,resim_belgesi,url):
    for i in range(len(lst_kalkis_saati)):
                    mycollection_sefer.insert_one({ 'resim':resim_belgesi,'firma': firma,'kalkis_yeri': lst_kalkis_yeri[i], 
                                    'varis_yeri': lst_varis_yeri[i], 
                                    'tarih':tarih,
                                    'kalkis_saati': lst_kalkis_saati[i], 
                                    'fiyat': lst_fiyat[i],
                                    'url' :url
                                    })
                    

def GET_SEHIRLER():
    sehir_lst=[]
    sehirler=list(mycollection_sehirler.find({}, {'_id': 0,'Id':0}))
    for i in sehirler:
                sehir = list(i.values())  # Sadece değerleri al
                for value in sehir:
                    value=value.upper()
                    sehir_lst.append(value)

    return sehir_lst
     
            
     
            
    
if __name__ == "__main__":
    app.run(debug=True)