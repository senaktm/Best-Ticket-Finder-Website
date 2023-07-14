# Best-Ticket-Finder-Website
--Find the best ticket using web scraping with selenium

--En uygun bilet fiyatını kıyaslayıp bulan websitesi


Projede templates klasörü içerisinde bulunan jinja kütüphanesi kullanılarak
oluşturulan login.html dosyası login ve registration sayfalarının şablonunu
içermektedir.
Login.htmldosyası içerisinde html kodları, sayfa dizaynı için css kodları ve hareketli
giriş sistemi için login ve registration ekranları arasında kullanıcı tercihine göre geçiş
sağlayacak javascript kodları yer almaktadır.

![image](https://github.com/senaktm/Best-Ticket-Finder-Website/assets/72103654/f0173278-b596-4386-800b-b147fbed470a)

Kullanıcı girişi sağlandıktan sonra kullanıcı, bilet seçim ekranına yönlendirilir. Bilet
seçim ekranında sefer kalkış yeri, varış yeri ve sefer tarihi bilgilerinin seçilebileceği
dropdownlar bulunmaktadır. Kullanıcı bu ekranda kalkış yerini, varış yerini ve
seyahat edeceği tarihi seçerek biletleri aratmaktadır

![image](https://github.com/senaktm/Best-Ticket-Finder-Website/assets/72103654/15e2497c-72d3-44c6-a643-c45151cdbd3f)

Kullanıcının bilet arama sayfasında tercih ettiği seferlere ait biletlerin kullanıcıya
sunulduğu ekrandır. Bir tablo şeklinde biletler sıralanmaktadır. Biletlere ait
firmaların logoları, bilete ait kalkış yeri, varış yeri, kalkış saati, tarihi ve bilet fiyatı
bilgileri kullanıcıya sunulmaktadır. Kullanıcının isteğine göre fiyata göre artan veya
fiyata göre azalan bir sıralama tercih etmesi durumu için bir filtreleme seçeneği
oluşturulmuştur. Kullanıcı sıralama tercihi yapmadığı sürece listelenen biletler
random olarak kullanıcıya sunulmaktadır. Kullanıcı bir filtreleme işlemi yapar ise
tercih ettiği filtreye göre veriler mongoDB den alınıp sıralanmaktadır.


![image](https://github.com/senaktm/Best-Ticket-Finder-Website/assets/72103654/14bcf015-8741-4537-afa3-d573375763d7)


