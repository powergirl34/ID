CLIMATE CHANGE(İKLİM DEĞİŞİKLİĞİ)

Templates;

main.py
# İçe Aktarma
from flask import Flask, render_template, request, redirect, url_for, jsonify 
# jsonify ara bulucu teyze gibi davranır python sözlüğü=kız tarafı tarayıcı=erkek tarafı jsonify=ara bulucu teyze

app = Flask(__name__)

# Sabitler 
BOLUNME_ORANI = (0.40, 0.60)
AGAC_FIYATI = 4
DOGAL_GUBRE_FIYATI = 60
DOGAL_GUBRE_BIRIMI = "kg"

# Çevresel etki hesaplama fonksiyonu
def calculate_impact(donation_tl: int, allocation: str = "split") -> dict:
    # Bağış miktarını ve tahsisat türünü alarak çevresel etkiyi hesaplar
    if donation_tl is None:
        donation_tl = 0
    donation_tl = max(int(donation_tl), 0)  # Bağış miktarını pozitif bir tamsayıya dönüştürür

    trees_budget = 0  # Ağaç bütçesi
    fertilizer_budget = 0  # Doğal gübre bütçesi

    allocation = (allocation or "split").lower()  # Tahsisat türünü küçük harfe çevirir

    # Tahsisat türüne göre bütçeleri ayarlar
    if allocation == "trees":
        trees_budget = donation_tl
    elif allocation == "fertilizer":
        fertilizer_budget = donation_tl
    else:  # "split" veya başka bir değer
        trees_budget = donation_tl * BOLUNME_ORANI[0]
        fertilizer_budget = donation_tl - trees_budget  # Kalan miktarı gübre bütçesi olarak ayarlar
        allocation = "split"  # Tahsisat türünü "split" olarak ayarlar

    # Birimlere dönüştürme
    trees_count = int(trees_budget / AGAC_FIYATI)  # Ağaç sayısını hesaplar
    fertilizer_count = int(fertilizer_budget / DOGAL_GUBRE_FIYATI)  # Doğal gübre miktarını hesaplar

    # Hesaplanan verileri bir sözlük olarak döner
    return {
        "amount_tl": donation_tl, 
        "allocation": allocation,  
        "budgets": {
            "trees_tl": trees_budget,
            "fertilizer_tl": fertilizer_budget,
        },
        "unit_costs": {
            "trees_tl": AGAC_FIYATI,
            "fertilizer_tl": DOGAL_GUBRE_FIYATI,
        },
        "impact": {
            "trees_count": trees_count,
            "fertilizer": {
                "value": fertilizer_count,
                "unit": DOGAL_GUBRE_BIRIMI,
            },
        }
    }

# Ana Sayfa
@app.route('/') 
def index():
    return render_template('index.html')

# Bağış Sayfası
@app.route('/donation', methods=['GET', 'POST']) # Bağış miktarı almak için GET ve POST yöntemlerini kullanır
def donation():
    if request.method == 'POST':
        amount = request.form.get('amount', type=int) # Formdan bağış miktarını alır
        reason_name = request.form.get('reason_name', default='split') # Formdan tahsisat türünü alır
        if not amount or amount <= 1:
            return redirect(url_for('donation')) # Bağış miktarı geçerli değilse tekrar yönlendirir
        return redirect(url_for('allocation', amount=amount, reason_name=reason_name)) # Bağış miktarı geçerliyse tahsisat sayfasına yönlendirir
    
    amount = request.args.get('amount', type=int) # GET isteği ile bağış miktarını alır
    reason_name = request.args.get('reason_name', default='split') # Tahsisat türünü alır
    if amount:
        return redirect(url_for('allocation', amount=amount, reason_name=reason_name)) # Eğer bağış miktarı varsa tahsisat sayfasına yönlendirir
    return render_template('donation.html') # Bağış sayfasını render eder

# Tahsisat Sayfası
@app.route('/allocation>') # Tahsis seçimi
def allocation():
    amount = request.args.get('amount', type=int) # GET isteği ile bağış miktarını alır
    reason_name = request.args.get('reason_name', default='split') # Tahsisat türünü alır
    if not amount or amount <= 1:
        return redirect(url_for('donation')) # Bağış miktarı geçerli değilse bağış sayfasına yönlendirir
    return render_template('allocation.html', amount=amount, reason_name=reason_name) # Bağış miktarını tahsisat sayfasına gönderir


@app.route('/donor', methods=['GET']) # Bağışçı sayfasına yönlendirir
def donor():
    name = request.args.get('name') # GET isteği ile bağışçı adını alır
    email = request.args.get('email') # GET isteği ile bağışçı e-posta adresini alır
    amount = request.args.get('amount', type=int) # GET isteği ile bağış miktarını alır
    reason_name = request.args.get('reason_name', default='split') # Tahsisat türünü alır 
    if not all([name, email, amount]):
        return redirect(url_for('donation'))
    return redirect(url_for('impact', amount=amount, allocation_choice=reason_name, name=name, email=email)) # Bağışçı sayfasına yönlendirir

# Çevresel Etki Sayfası
@app.route('/donation/<int:amount>/<string:allocation_choice>')
def impact(amount: int, allocation_choice: str):
    if allocation_choice.lower() not in {"split", "trees", "fertilizer"}:
        allocation_choice = "split" # Tahsisat türü geçerli değilse "split" olarak ayarlar
    name = request.args.get('name') # GET isteği ile bağışçı adını alır
    email = request.args.get('email') # GET isteği ile bağışçı e-posta adresini alır
    data = calculate_impact(amount, allocation_choice) # Çevresel etkiyi hesaplar
    return render_template('impact.html', data=data, name=name, email=email) # Hesaplanan verileri etki sayfasına gönderir

@app.route('/thankyou') # teşekkür Sayfası 
def thankyou(): 
    # GET isteği ile bağış miktarını, adını ve e-posta adresini alır kullanıcıya veriri.
    amount = request.args.get('amount', type=int) 
    name = request.args.get('name') 
    email = request.args.get('email')
    reason_name = request.args.get('reason_name', default='split')
    return render_template('thankyou.html', amount=amount, name=name, email=email)

# Ara bulucu teyze olan jsonify devreye girer
@app.route('/api/impact')
def api_impact():
    amount = request.args.get('amount', type=int)
    allocation_choice = request.args.get('allocation', default='split') # GET isteği ile bağış miktarını ve tahsisat türünü alır
    if not amount:
        return jsonify({'error': 'amount (TL) zorunludur.'}), 400 # Bağış miktarı zorunlu ise hata mesajı döner
    return jsonify(calculate_impact(amount, allocation_choice))
 

if __name__ == '__main__':   

index.html :
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta
    name="viewport"
    content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0"
  >
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <link rel="stylesheet" href="../static/css/style.css">
  <title>İklim Bağışçısı Platformu</title>
</head>
<body>
  <header class="header">
    <div class="header__text">
      <h1>İKLİM DEĞİŞİKLİĞİNİ ÖNLEYİN!</h1>
      <p>Bağış yaparak iklim değişikliğinin önlenmesine ve yediğiniz sebze meyvelerin doğal olmasına katkı sağlayın.</p>
    </div>
  </header>
  <main>
    {% block content %}
    <h2>Bağış yapmak için aşağıdaki butona tıklayınız:</h2> <!-- Bağış yap butonu -->
    <div style ="text-align:center; margin-top: 70px;"> <!-- Butonun ortalanması ve üst boşluk -->
      <a class="button" href="{{ url_for('donation') }}"> <!--Butona bas ve donation sayfasına git-->
        <img src="{{url_for('static', filename='img/d.jpg')}}" alt="Bağış Yap" class="button__img"> <!-- Buton resmi -->
        <span>Bağış Yap</span>
      </a>
    </div>
    {% endblock %}

    <!--Bilgilendirme Bölümü-->
    <div class="fact-box"> <!-- Bilgi kutusu -->
      <div class="fact-box__title">Biliyor muydunuz?</div> <!-- Bilgi kutusu başlığı -->
      <div class="fact">🌳Ağaçlar, bulut oluşumunu teşvik eden ve yağışları artıran uçucu organik bileşikler yayar. Bu doğal süreç, yerel iklim düzenlemesinde hayati bir rol oynar.</div>
      <div class="fact">🌱Doğal gübreleme, toprağın verimliliğini artırarak bitkilerin sağlıklı büyümesini destekler ve tarımda kimyasal gübre kullanımını azaltır.</div>
      <div class="fact">🌍Sağlıklı topraklar, devasa miktarda karbonu hapsederek iklim değişikliğinin yavaşlatılmasına yardımcı olur.</div>
      <div class="fact">🌾Doğal gübreleme, toprağın su tutma kapasitesini artırarak kuraklık dönemlerinde bile bitkilerin sağlıklı kalmasına yardımcı olur.</div>
      <div class="fact">🌳Ağaçlar, havadaki karbondioksiti emerek iklim değişikliğini yavaşlatır ve temiz hava sağlar.</div>
      <div class="fact">🌱Kentlerdeki ağaçlar sadece estetik değil, aynı zamanda kentsel ısı adası etkisini azaltarak ve binaların soğutma ihtiyacını düşürerek enerji tasarrufu sağlarlar.</div>
      <div class="fact">🌍Topraktaki milyarlarca mikrop, organik maddenin parçalanması ve besin döngüsünde hayati bir rol oynar.</div>
      <div class="fact">🌾Ormanlar, su döngüsünün düzenlenmesinde kritik bir rol oynar.Terleme yoluyla suya geri su buharı salarak yağış oluşumunu destekler, su kaynaklarının sürdürülebilirliğine katkıda bulunurlar.</div>
      <div class="fact">🌳1 ton kimyasal gübre üretimi 1.5 ton CO2 salınımına neden olur.</div>
      <div class="fact">🌱Doğal gübreleme, toprağın pH dengesini iyileştirerek bitkilerin besin maddelerini daha iyi almasını sağlar.</div>
      <div class="fact">🌍Ağaçlar, kök sistemleri sayesinde toprağı erozyona karşı korur ve suyun yeraltına sızmasını sağlar.</div>
  </main>
  <footer>
    <p>&copy; 2025 Bağış Platformu. Tüm hakları saklıdır.</p>
    <br>
  </footer>
</body>
</html>

donation.html : 
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta
    name="viewport"
    content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0"
  >
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/donation.css') }}">
  <title>BAĞIŞ YAP</title>
</head>
<body>

  <div class="donation-container">
    <h1 class="donation-title">Bağış Yap</h1>
    <p class="donation-description">Sağlıklı gıdalara ulaşmak ve iklim değişikliğine karşı mücadele etmek için bağış yapın.</p>

    <form class="donation-form" action="{{ url_for('allocation') }}" method="get"> <!-- Bağış formu -->
      <label for="amount">Bağış Miktarı (TL):</label>
      <input type="number" id="amount" name="amount" min="1" required>
      <input type="hidden" name="reason_name" value="split">
      <button type="submit">Devam Et</button>
    </form>
    <h1 class="donation-note">Bağışlarınız, sağlıklı gıdalara ulaşmamıza ve iklim değişikliği ile mücadele etmemize yardımcı olacaktır. Teşekkür ederiz.</h1>
  </div>
  <footer>
    <p>&copy; 2025 Bağış Platformu. Tüm hakları saklıdır.</p>
    <br>
  </footer>
</body>
</html>  

allocation.html: 

<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta
    name="viewport"
    content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0"
  >
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}"> 
  <title>Bağış Tahsisi</title>
</head>
<body>
  <header class="header">
    <h1>Bağışınızın Tahsisi</h1>
    <p></p>
  </header>
  <main>
    {% block content %}
    <h2>Lütfen bilgilerinizi giriniz:</h2>
    <br>
    <p>Bağış Miktarınız: {{ amount }} TL</p> 
    <!--Bilgileri alıp tutar-->
    <form action="{{ url_for('donor') }}" method="get"> 
      <input type="hidden" name="amount" value="{{ amount }}"> 
      <input type="hidden" name="reason_name" value="{{ reason_name }}"> 
      <label for="name">Adınız & Soyadınız:</label> 
      <input type="text" name="name" id="name" required>
      <label for="email">E-posta Adresiniz:</label>
      <input type="text" name="email" id="email" required>
      <button type="submit">Bağışı Onayla</button>
    </form>
    {% endblock %}
  </main>
  <footer>
    <p>&copy; 2025 Bağış Platformu. Tüm hakları saklıdır.</p>
    <br>
  </footer>
</body>
</html>

impact.html:

<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta
    name="viewport"
    content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0"
  >
  <title>Çevresel Etki</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  <!-- CSS stilleri -->
  <style>
    .impact-container { 
        max-width: 800px; /* Maksimum genişlik */
        margin: 0 auto; /* Ortala */
        padding: 20px; /* İç boşluk */
        background-color: #f9f9f9; /* Arka plan rengi */
        border-radius: 10px; /* Köşe yuvarlama */
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* Gölgelendirme */
    }
    .impact-container h1 { 
        color: #0EB07C; /* Başlık rengi */
        margin-bottom: 20px; /* Alt boşluk */
    }
    
    .impact-list {
        text-align: left; /* Metin hizalaması */
        margin-top: 20px; /* Üst boşluk */
        font-size: 18px; /* Yazı boyutu */
    }

    .impact-list li {
        margin-bottom: 10px; /* Liste öğeleri arasındaki boşluk */
    }

    .back-link {
        display: inline-block; /* Satır içi blok olarak görüntüleme */
        margin-top: 30px; /* Üst boşluk */
        padding: 10px 20px; /* İç boşluk */
        background-color: #0EB07C; /* Arka plan rengi */
        color: white; /* Metin rengi */
        text-decoration: none; /* Metin dekorasyonu yok */
        border-radius: 9px; /* Köşe yuvarlama */
    }

    .back-link:hover { 
        background-color: #71f7c8ff; /* Hover efekti */
    }
  </style>
</head>
<body>
    <div class="impact-container"> 
        <h1>Çevresel Etki</h1>
        <p>Toplam Bağış Miktarı: <strong>{{ data.amount_tl }} TL</strong></p> 

        <ul class="impact-list"> <!-- Etki listesi -->
            <li>Ağaçlandırma İçin Ayrılan Bütçe: {{ data.budgets.trees_tl }} TL → <strong>{{ data.impact.trees_count }} tane</strong></li> 
            <li>Doğal Gübre İçin Ayrılan Bütçe: {{ data.budgets.fertilizer_tl }} TL → <strong>{{ data.impact.fertilizer.value }}  {{data.impact.fertilizer.unit}}</strong></li>
        </ul>
        
        <a class="next-link" href="{{ url_for('thankyou', amount=data.amount_tl, reason_name=data.allocation, name=name, email=email) }}">Devam Et</a> <!-- Teşekkür sayfasına git -->
        <br>
        <a class="back-link" href="{{ url_for('index') }}">Ana Sayfaya Dön</a> <!-- Ana sayfaya dön -->
    </div>
    <footer>
        <br>
        <br>
        <p>&copy; 2025 Bağış Platformu. Tüm hakları saklıdır.</p>
        <br>
    </footer>
</body>
</html>

thankyou.html : 

<!doctype html> 
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta
    name="viewport"
    content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0"
  >
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  <title>Bağış Onayı</title>

  <style> /* Dahili stil sayfası */
    /* Temel stil ayarları */
    .back-link {
        display: inline-block; /* Satır içi blok olarak görüntüleme */
        margin-top: 30px; /* Üst boşluk */
        padding: 10px 20px; /* İç boşluk */
        background-color: #0EB07C; /* Arka plan rengi */
        color: white; /* Metin rengi */
        text-decoration: none; /* Metin dekorasyonu yok */
        border-radius: 9px; /* Köşe yuvarlama */
    }

    .back-link:hover { 
        background-color: #71f7c8ff; 
    }
  </style>

</head>
<body>
  <header class="header">
    <h1>Teşekkürler!</h1>
    <p></p>
  </header>
  <main>
    {% block content %} 
    <!--allocation.html'den aldığı bilgileri thankyou.html'e gönderir.-->
    <h1>Bağışınız başarıyla alınmıştır.</h1>
    <br>
    <p>{% if name %}Adınız & Soyadınız: <strong>{{ name }}{% endif %}</strong></p>
    <br>
    <p>{% if email %}E-posta: <strong>{{ email }}{% endif %}</strong></p>
    <br>
    <p>{% if amount %}Bağış miktarınız: {{ amount }} TL{% endif %}</p>
    <br>
    <a class="back-link" href="{{ url_for('index') }}">Ana Sayfaya Dön</a>
    {% endblock %}
  </main>
  <footer>
    <p>&copy; 2025 Bağış Platformu. Tüm hakları saklıdır.</p>
  </footer>
</body>
</html>

CSS;

style.css:

@import url('https://fonts.googleapis.com/css2?family=Montserrat&display=swap');

body {
    margin: 0; /* Tüm kenar boşluklarını kaldır */
    padding: 0; /* Tüm iç boşlukları kaldır */
    font-family: 'Montserrat', sans-serif; /* Google Fonts'tan Montserrat fontu */
    font-size: 18px; /* Temel font boyutu */
    line-height: 20px; /* Satır yüksekliği */
    background-color: #fff; /* Arka plan rengi */
    color: #272727; /* Metin rengi */
}

h1, h2, p {
    margin: 0; /* Tüm kenar boşluklarını kaldır */
}

ul {
    list-style: none; /* Madde işaretlerini kaldır */
    margin: 0; /* Tüm kenar boşluklarını kaldır */
    padding: 0; /* Tüm iç boşlukları kaldır */
}

.header {
    background-image: url("../img/bagıs.jpg"); /* Arka plan resmi */
    background-size: contain; /* Resmin kapsama biçimi */
    background-repeat: no-repeat; /* Resmin tekrarlanmaması */
    background-position: left; /* Resmin konumu */
    background-color: #CCE59D; /* Arka plan rengi */
    padding: 25vh 30px; /* İç boşluk */
    margin-bottom: 60px; /* Alt boşluk */
    display: flex; /* Flexbox kullanımı */
    flex-direction: column; /* Dikey yönlendirme */
    align-items: flex-end; /* Sağ hizalama */
}

.header__text {
    display: flex; /* Flexbox kullanımı */
    flex-direction: column; /* Dikey yönlendirme */
    gap: 30px; /* Elemanlar arası boşluk */
    width: fit-content; /* İçeriğe göre genişlik */
    text-align: right; /* Sağ hizalama */
}

main {
    padding: 0 30px 100px; /* İç boşluk */
}

.main__title {
    text-align: center; /* Başlık hizalaması */
    margin-bottom: 100px; /* Alt boşluk */
}

.list {
    display: flex; /* Flexbox kullanımı */
    justify-content: space-around; /* Elemanlar arası boşluk */
}

.list__item a {
    text-decoration: none; /* Metin dekorasyonu yok */
    display: flex; /* Flexbox kullanımı */
    flex-direction: column; /* Dikey yönlendirme */
    align-items: center; /* Ortala */
    color: inherit; /* Renk alımı */
    gap: 20px; /* Elemanlar arası boşluk */
    padding: 20px; /* İç boşluk */
    border-radius: 24px; /* Köşe yuvarlama */
    border: 1px solid #0be2cdb3; /* Kenarlık */
    transition: 0.2s; /* Geçiş efekti */
}
.item__img {
    object-fit: contain; /* Resim kapsama biçimi */
    width: 150px; /* Genişlik */
}

.list__item a:hover {
    box-shadow: 1px 1px 4px 4px #0EB07C; /* Hover efekti */
}

.main__rez { 
    display: flex; /* Flexbox kullanımı */
    flex-direction: column; /* Dikey yönlendirme */
    gap: 20px; /* Elemanlar arası boşluk */
    align-items: center; /* Ortala */
}

.rez__img {
    object-fit: contain; /* Resim kapsama biçimi */
    width: 300px; /* Genişlik */
}

.main__title--margin {
    margin-bottom: 50px; /* Alt boşluk */
}

.main__link {
    display: inline-block; /* Satır içi blok olarak görüntüleme */
    text-decoration: none; /* Metin dekorasyonu yok */
    padding: 20px 0; /* İç boşluk */
    width: 300px; /* Genişlik */
    border-radius: 20px; /* Köşe yuvarlama */
    background-color: #0EB07C; /* Arka plan rengi */
    text-align: center; /* Metin hizalaması */
    cursor: pointer; /* İmleç şekli */
    color: #fff; /* Metin rengi */
}

.form {
    display: flex; /* Flexbox kullanımı */
    flex-direction: column; /* Dikey yönlendirme */
    align-items: center; /* Ortala */
    gap: 50px; /* Elemanlar arası boşluk */
}


.user input { 
    padding: 10px; /* İç boşluk */
    border: 1px solid #EB8028; /* Kenarlık */
    background: inherit; /* Arka plan miras alımı */
    border-radius: 5px; /* Köşe yuvarlama */
    font: inherit; /* Font alımı */
    width: 100%; /* Genişlik */
    color: #EB8028; /* Metin rengi */
}

.user input:focus,
.user input:active {
    border: 1px solid #EB8028; /* Kenarlık */
    outline: none; /* Dış hat yok */
}

.user {
    display: flex; /* Flexbox kullanımı */
    flex-direction: row; /* Yatay yönlendirme */
    width: 100%; /* Genişlik */
    justify-content: space-around; /* Elemanlar arası boşluk */
}

.user-info {
    width: 30%; /* Genişlik */
    display: flex; /* Flexbox kullanımı */
    flex-direction: column; /* Dikey yönlendirme */
    gap: 40px; /* Elemanlar arası boşluk */
}

label {
    display:inline-block ; /* Satır içi blok olarak görüntüleme */
    margin-bottom: 10px; /* Alt boşluk */
}

.address-date {
    width: 30%; /* Genişlik */
    display: flex; /* Flexbox kullanımı */
    flex-direction: column; /* Dikey yönlendirme */
    gap: 40px; /* Elemanlar arası boşluk */
}

.delivery {
    display: flex; /* Flexbox kullanımı */
    justify-content: space-between; /* Elemanlar arası boşluk */
}

.button {
    display: flex; /* Flexbox kullanımı */
    flex-direction: column; /* Dikey yönlendirme */
    align-items: center; /* Ortala */
    justify-content: center; /* Ortala */
    gap: 10px; /* Elemanlar arası boşluk */

    width: 300px; /* Genişlik */
    height: 200px; /* Yükseklik */
    border: none; /* Kenarlık yok */
    border-radius: 12px; /* Köşe yuvarlama */
    background-color: #0EB07C; /* Arka plan rengi */
    color: #fff; /* Metin rengi */
    font-size: 22px; /* Font boyutu */
    font-weight: bold; /* Font kalınlığı */
    text-decoration: none; /* Metin dekorasyonu yok */
    cursor: pointer; /* İmleç şekli */

    box-shadow: 0 4px 6px rgba(0,0,0,0.3); /* Gölgelendirme */
    transition: background-color 0.2 ease, box-shadow 0.2 ease; /* Geçiş efekti */
}

.button:hover {
    transform: scale(1.05); /* Hover efekti */
    box-shadow: 0 6px 10px rgba(0,0,0,0.4); /* Gölgelendirme */
}

.button__img {
    width: 150px; /* Genişlik */
    height: 400px; /* Yükseklik */
    object-fit: contain; /* Resim kapsama biçimi */
}

.fact-box__title {
    position: absolute; /* Mutlak konumlandırma */
    top: 0px; /* Üst konum */
    left: 0; /* Sol konum */
    width: 100%; /* Genişlik */
    text-align: center; /* Metin hizalaması */
    font-size: 20px; /* Font boyutu */
    font-weight: bold; /* Font kalınlığı */
    padding: 10px; /* İç boşluk */
    background-color: #0EB07C; /* Arka plan rengi */
    color: #fff; /* Metin rengi */
    border-top-left-radius: 10px; /* Sol üst köşe yuvarlama */
    border-top-right-radius: 10px; /* Sağ üst köşe yuvarlama */
}


.fact-box {
  position: relative; /* Göreli konumlandırma */
  width: 80%; /* genişliği %80 yaptım */
  max-width: 800px; /* maksimum genişlük */
  height: 140px;  /* yükseklik */
  margin: 40px auto; /* üst ve alt boşluk, yatayda ortala */
  overflow: hidden; /* taşan içeriği gizle */
  background: #f0fff4; /* arka plan rengi */
  border-left: 6px solid #0EB07C; /* sol kenarlık */
  border-radius: 10px; /* köşe yuvarlama */
  font-size: 18px; /* yazı boyutu*/
  font-weight: bold; /* yazı kalınlığı*/
  text-align: center; /*metin hızalaması*/
  display: flex; /* flexbox kullanımı*/
  align-items: center; /* dikeyde ortala*/
  justify-content: center; /* yatayda ortala*/
  box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* gölgelendirme*/
}

.fact { /* her bir bilgi kutusu için stil */
  position: absolute; /* konumlandırma */
  top: 0; /* üst:0 */
  left: 0; /* sol:0 */
  width: 100%; /* genişlik:%100 */
  height: 100%; /* yükseklik:%100 */
  display: flex; /* flexbox kullanımı */
  align-items: center; /* dikeyde ortala */
  justify-content: center; /* yatayda ortala */
  padding: 20px; /* iç boşluk */
  box-sizing: border-box; /* kutu boyutlandırma */
  opacity: 0; /* başlangıçta görünmez */
  animation: fade 44s infinite; /* animasyon */
}

/* 11 tane bilgi için sırayla gecikme ayarları */
.fact:nth-child(1) { animation-delay: 0s; } /* .fact:nth-child: .fact sınıfına sahip ilk sıradaki elemanı seçer. */
.fact:nth-child(2) { animation-delay: 4s; } /* animation-delay: animasyonun başlaması için gecikme süresi. */
.fact:nth-child(3) { animation-delay: 8s; }
.fact:nth-child(4) { animation-delay: 12s; }
.fact:nth-child(5) { animation-delay: 16s; }
.fact:nth-child(6) { animation-delay: 20s; }
.fact:nth-child(7) { animation-delay: 24s; }
.fact:nth-child(8) { animation-delay: 28s; }
.fact:nth-child(9) { animation-delay: 32s; }
.fact:nth-child(10) { animation-delay: 36s; }
.fact:nth-child(11) { animation-delay: 40s; }

@keyframes fade { /* animasyonun seneyosu */
  0%, 8% { opacity: 0; } /* elemanlar bu yüzdelikler arasında görünmez */
  10%, 18% { opacity: 1; } /* elemanlar bu yüzdelikler arasında görünür */
  20%, 100%  { opacity: 0; } /* elemanlar bu yüzdelikler arasında görünmez */
}

donation.css:

/* Donation Page Styles */
.donation-container {
    max-width: 2000px; /* Maksimum genişlik */
    height: 1000px; /* Yükseklik */
    margin: 0 auto; /*Ortalar*/
    padding: 60px 30px; /* İçerik boşlukları */
    background-color: #7fffd4; /* Arka plan rengi */
    border-radius: 15px; /* Köşe yuvarlama */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Gölge efekti */
}

/* Başlık stilleri */
.donation-title {
    font-size: 50px; /* Başlık boyutu */
    font-weight: bold; /* Kalın yazı tipi */
    color: #0eda96; /* Başlık rengi */
    text-align: center; /* Başlık ortalanır */
    margin-bottom: 20px; /* Alt boşluk */
}

/* Açıklama metni */
.donation-description {
    text-align: center; /* Metin ortalanır */
    margin-bottom: 100px; /* Alt boşluk */
    color: #333; /* Açıklama rengi */
    font-size: 30px; /* Açıklama boyutu */
    font-weight: bold; /* Kalın yazı tipi */
}

/* Bağış formu stilleri */
.donation-form {
    display: flex; /* Flexbox kullanımı */
    flex-direction: column; /* Dikey hizalama */
    gap: 20px; /* Elemanlar arasındaki boşluk */
    align-items: center; /* Elemanlar ortalanır */
}

/* Giriş alanı stilleri */
.donation-form label {
    font-size: 30px; /* Etiket boyutu */
    color: #09c3a1; /* Etiket rengi */
}

/* Giriş alanı ve seçim kutusu stilleri */
.donation-form input[type="text"],
.donation-form select {
    width: 100%; /* Genişlik */
    max-width: 300px; /* Maksimum genişlik */
    padding: 10px 15px; /* İç boşluk */
    border: 3px solid #ccc; /* Kenarlık rengi */
    border-radius: 5px; /* Köşe yuvarlama */
    font-size: 16px; /* Yazı tipi boyutu */
    color: #09c3a1; /* Yazı rengi */
    background-color: #fff; /* Arka plan rengi */    
}

/* Giriş alanı ve seçim kutusu odaklanma stilleri */
.donation-form input:focus,
.donation-form select:focus {
    outline: none; /* Odaklanma kenarlığı kaldırılır */
    border-color: #0EB07C; /* Odaklanma kenarlık rengi */
    padding: 20px 15px; /* İç boşluk */
}

/*Gönder butonu */
.donation button {
    padding: 20px 20px; /* İç boşluk */
    background-color: #0EB07C; /* Buton arka plan rengi */
    color: #fff; /* Buton yazı rengi */
    font-size: 25px; /* Yazı tipi boyutu */
    border: none; /* Kenarlık yok */
    border-radius: 5px; /* Köşe yuvarlama */
    cursor: pointer; /* İmleç el işareti olur */
    transition: background-color 0.3s ease; /* Geçiş efekti */
}

.donation button:hover {
    background-color: #0d9f6b; /* Hover efekti */
    transform: scale(1.05); /* Hover sırasında buton büyür */
    padding: 20px 25px; /* Hover sırasında iç boşluk artar */
}






      
    app.run(debug=True)
