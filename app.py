
from flask import Flask, request, render_template
import  sqlite3, os, socket, cgi, sys

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

DATABASE = 'database.db'
db = sqlite3.connect(DATABASE)
db.commit()

@app.route('/')
def main():	
	return render_template('index.html')

@app.route('/kurulum') 
def kurulum():
	return render_template('kurulum.html')

# SQL Enjeksiyon Zafiyetinin Acik Oldugu Fonksiyon
@app.route('/sqlenjeksiyon', methods=['GET'])
def sqlenjeksiyon():
	if request.args:

		# request ile gelen kullanici adi alinir
		kullaniciadi = request.args.get('kullaniciadi')

		# Request ile gelen sifre alinir
		sifre = request.args.get('sifre') 

		# gelen parametreler ile dogrudan sql sorgusu hazirlanir 
		sorgu = "SELECT * FROM uyeler WHERE kullanici='"+kullaniciadi+"' AND sifre='"+sifre+"'" 
		
		# veritabanina baglanilir
		db = sqlite3.connect(DATABASE)
		db.row_factory = sqlite3.Row
		
		# sorgu calistirilir 
		cursor = db.execute(sorgu)

	 	# sorgu sonuclari alinir 
		uyeler = cursor.fetchall()

		# eger sorgu sonucu bos degilse 
		if uyeler:
			uye = uyeler[0] # bir kayit donecegi varsayilarak ilk kayit alinir
			# tablodaki veriler sirayla alinir
			uyeadi = uye['kullanici']
			yas = uye['yas']
			boy = uye['boy']
			kilo = uye['kilo']
			tc = uye['tc']
			#render_template fonksiyonu ile ilgili sayfaya gerekli parametreler gonderilir
			return render_template('sqlenjeksiyon.html', uye=uye) 
		else:
			return render_template('sqlenjeksiyon.html', uyari=True) 
	else:
		return render_template('sqlenjeksiyon.html')


"""
# SQL Enjeksiyon Zafiyetinin Kapali Oldugu Fonksiyon
@app.route('/sqlenjeksiyon', methods=['GET'])
def sqlenjeksiyon():
	if request.args:

		# request ile gelen kullanici adi alinir
		kullaniciadi = request.args.get('kullaniciadi')

		# Request ile gelen sifre alinir
		sifre = request.args.get('sifre') 

		# sql sorgusu prepared statement seklinde hazirlanir bu yontemle zafiyet kapatilmis olur 
		sorgu = "SELECT * FROM uyeler WHERE kullanici=? AND sifre=?" 
		
		# veritabanina baglanilir
		db = sqlite3.connect(DATABASE)
		db.row_factory = sqlite3.Row
		
		# sorgu parametreler ile calistirilirir
		cursor = db.execute(sorgu, (kullaniciadi,sifre))

	 	# sorgu sonuclari alinir 
		uyeler = cursor.fetchall()

		# eger sorgu sonucu bos degilse 
		if uyeler:
			uye = uyeler[0] # bir kayit donecegi varsayilarak ilk kayit alinir
			
			# tablodaki veriler sirayla alinir
			uyeadi = uye['kullanici']
			yas = uye['yas']
			boy = uye['boy']
			kilo = uye['kilo']
			tc = uye['tc']
			#render_template fonksiyonu ile ilgili sayfaya gerekli parametreler gonderilir
			return render_template('sqlenjeksiyon.html', uye=uye) 
		else:
			return render_template('sqlenjeksiyon.html', uyari=True) 
	else:
		return render_template('sqlenjeksiyon.html')
"""		

# XSS Zafiyetinin Acik Oldugu Fonksiyon
@app.route('/xss', methods=['GET'])
def xss():
	if request.args:
		yazar = request.args.get('yazar') # parametre olarak gelen veriler degiskenlere alinir
		yorum = request.args.get('yorum')
		
		# yorum eklemek icin gerekli sorgu hazirlanir
		sorgu = "INSERT INTO yorumlar ('yorum','yazar') VALUES (?,?)"
		
		# veritabanina baglanilir
		db = sqlite3.connect(DATABASE)
		db.row_factory = sqlite3.Row

		# eger yazar ismi girilmemisse 'Gizli' olarak kaydedilir
		if not yazar:
			yazar = 'Gizli'
		# degiskenler uzerinde herhangi bir filtreleme islemi yapilmadan sorgu calistirilir 
		db.execute(sorgu, (yorum,yazar,)) # zafiyetin olustugu durum burasidir

		# veritabaninta yapilan degisikligin etkili olmasi icin commit edilir
		db.commit()

	# gelen parametreler ile dogrudan sql sorgusu hazirlanir 
	sorgu = "SELECT * FROM yorumlar ORDER BY yorum ASC"
		
	# veritabanina baglanilir
	db = sqlite3.connect(DATABASE)
	# veritabanindan cekilen verileri kolon isimleri ile kullanabilmek icin gerekli atama islemi
	db.row_factory = sqlite3.Row
	# sorgu sonucunda donen verileri kullanabilmek icin gerekli cursor olusturulur
	cursor = db.cursor()
	# sorgu calistirilir 
	cursor.execute(sorgu)

	# sorgu sonuclari alinir 
	yorumlar = cursor.fetchall()

	#render_template fonksiyonu ile ilgili sayfaya gerekli parametreler gonderilir
	return render_template('xss.html', yorumlar=yorumlar)


"""
# XSS Zafiyetinin Kapali Oldugu Fonksiyon
@app.route('/xss', methods=['GET'])
def xss():
	if request.args:
		yazar = request.args.get('yazar') # parametre olarak gelen veriler degiskenlere alinir
		yorum = request.args.get('yorum')
		
		# yorum eklemek icin gerekli sorgu hazirlanir
		sorgu = "INSERT INTO yorumlar ('yorum','yazar') VALUES (?,?)"
		
		# veritabanina baglanilir
		db = sqlite3.connect(DATABASE)
		db.row_factory = sqlite3.Row

		# cgi modulundeki 'escape' fonksiyonu kullanilarak girdiler guvenli metin haline getirilir
		# yapilan bu islem XSS zafiyetinin kapandigi noktadir
		yazar = cgi.escape(yazar,True)
		yorum = cgi.escape(yorum,True)
		
		# eger yazar ismi girilmemisse 'Gizli' olarak kaydedilir
		if not yazar:
			yazar = 'Gizli'

		# sorgu calistirilir 
		db.execute(sorgu, (yorum,yazar,))

		# veritabaninta yapilan degisikligin etkili olmasi icin commit edilir
		db.commit()

	# veritabanindaki yorumlari cekmek icin gerekli sorgu hazirlanir
	sorgu = "SELECT * FROM yorumlar ORDER BY yorum ASC"
		
	# veritabanina baglanilir
	db = sqlite3.connect(DATABASE)
	
	# veritabanindan cekilen verileri kolon isimleri ile kullanabilmek icin gerekli atama islemi
	db.row_factory = sqlite3.Row

	# sorgu sonucunda donen verileri kullanabilmek icin gerekli cursor olusturulur
	cursor = db.cursor()
	
	# sorgu calistirilir 
	cursor.execute(sorgu)

	# sorgu sonuclari alinir 
	yorumlar = cursor.fetchall()
	
	#render_template fonksiyonu ile ilgili sayfaya gerekli parametreler gonderilir
	return render_template('xss.html', yorumlar=yorumlar)
"""

# Komut Enjeksiyonu Zafiyetinin Acik Oldugu Fonksiyon
@app.route('/komutenjeksiyon', methods=['GET'])
def komutenjeksiyon():
	if request.args:
		adres = request.args.get('adres') # parametre olarak gelen adres alinir
   		komut = 'ping -c 4 ' # parametre olarak gelen adrese ping gonderebilmek icin gerekli olan komut hazirlanir
		komut = komut + adres # komut ile parametre birlestirilir
		sonuc = os.popen(komut).read() # komut calistirilir ve ciktilar okunur
		return render_template('komut.html', sonuc=sonuc) # render_template fonksiyonu ile ilgili sayfaya gerekli parametreler gonderilir
	else:
		return render_template('komut.html')


"""
# Komut Enjeksiyonu Zafiyetinin Kapali Oldugu Fonksiyon
@app.route('/komutenjeksiyon', methods=['GET'])
def komutenjeksiyon():
	if request.args:
		adres = request.args.get('adres') # parametre olarak gelen adres alinir

		try:
			# socket modulunde bulunan 'gethostbyname' fonksiyonu ile gelen adresin dogrulugu kontrol edilir
			# eger adres gecerli bir adres icermiyorsa except ile hata yakalanir ve komut isletilmez
   			ip = socket.gethostbyname(adres) # zafiyetin kapandigi nokta burasidir
   			komut = 'ping -c 4 ' # parametre olarak gelen adrese ping gonderebilmek icin gerekli olan komut hazirlanir
			komut = komut + str(ip) # komut ile parametre birlestirilir
			sonuc = os.popen(komut).read() # komut calistirilir ve ciktilar okunur
			return render_template('komut.html', sonuc=sonuc) # render_template fonksiyonu ile ilgili sayfaya gerekli parametreler gonderilir
		except socket.error:
   			return render_template('komut.html', sonuc='Adres Dogru Degil') # gecersiz adres sonucunda hata mesaji verilir
	else:
		return render_template('komut.html')


"""


if __name__ == '__main__':
	app.run(port=8080,debug=True)

