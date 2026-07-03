## tokenizer sınıfı ve yardımcı fonksiyonlar

"""
- corpus hazırlama 
- çift sayma 
- en iyi çifti seçme
- birleştirme uygulama 
- eğitim döngüsü 
- json işlemleri dışa aktar / içe aktar
- tokenize metodu
"""

import re 
import json 
from collections import defaultdict

def kelimeyi_karakterlere_bol(kelime: str) -> tuple:
     # Görevi : eylem -> ('e', 'y', 'l', 'e', 'm', '</w>')
     return tuple(kelime) + ('</w>',)

class BPETokenizer:
    def __init__(self, hedef_vocab_size: int = 50):
          self.hedef_vocab_size = hedef_vocab_size
          self.merge_kurallari = []
          self.vocab : dict = {}

    def corpus_hazirla(self, metin: str) -> dict:
         frekans_sozlugu = defaultdict(int)
         metin = metin.lower() 
         metin = re.sub(r"[^\w\s]", "", metin)  # Noktalama işaretlerini kaldır
         for kelime in metin.split(): 
            if kelime:
                 karakter_tuple  = kelimeyi_karakterlere_bol(kelime)
                 frekans_sozlugu[karakter_tuple] += 1
         return dict(frekans_sozlugu) # defaultdict'i dict'e çevirip döndür
    
    def _cift_frekanslarini_say(self, frekans_sozlugu: dict) -> dict:
        cift_sayaci = defaultdict(int)
        for token_dizisi, frekans in frekans_sozlugu.items():
             for i in range(len(token_dizisi) - 1):
                cift = (token_dizisi[i], token_dizisi[i + 1])
                cift_sayaci[cift] += frekans
        return dict(cift_sayaci)  # defaultdict'i dict'e çevirip döndür
    
    def _en_iyi_cifti_sec(self, cift_frekanslari: dict) -> tuple:

        if not cift_frekanslari:
            return None
        
        en_iyi = min(
            cift_frekanslari,
            key=lambda cift:(
                -cift_frekanslari[cift], # frekansları azalan sırada sıralamak için negatif değer kullanıyoruz
                cift[0],  # aynı frekansta olan çiftleri alfabetik olarak sıralamak için
                cift[1]   # aynı frekansta olan çiftleri alfabetik olarak sıralamak için
            )
        )

        return en_iyi
    
    def _birleştirme_uygulama(self, kelime_frekanslari: dict, birlestirilecek_cift: tuple):
        yeni_sozluk = {}
        sol, sağ = birlestirilecek_cift
        yeni_token = sol + sağ # l + em

        for token_dizisi, frekans in kelime_frekanslari.items():
            yeni_dizi = []
            i = 0
            while i < len(token_dizisi):
                #('e', 'y', 'l', 'e', 'm', '</w>'): 3
                #('e' + 'm') : 3
                # em 
                if (i < len(token_dizisi) - 1 and token_dizisi[i] == sol and token_dizisi[i + 1] == sağ):
                    yeni_dizi.append(yeni_token)
                    i += 2  # Birleştirilen çiftin her iki öğesini de atla
                else:
                    yeni_dizi.append(token_dizisi[i])
                    i += 1
            yeni_sozluk[tuple(yeni_dizi)] = frekans
        return yeni_sozluk
    
    def egit(self, metin: str, yazdirma: bool = True):

        # Adım 1: Corpus'u hazırla
        kelime_frekanslari = self.corpus_hazirla(metin)
        # Adım 2: Başlangıç vocab'ını oluştur
        vocab_set = set()
        for token_dizisi in kelime_frekanslari:
            for token in token_dizisi:
                vocab_set.add(token)
                # (e , y, l, m, </w>)
        if yazdirma:
            print(f"başlangıç vocab :" , vocab_set)
            
        # Adım 3: Eğitim döngüsü
        iterasyon = 0
        while len(vocab_set) < self.hedef_vocab_size:
            iterasyon += 1
            # Adım 3.1: Çift frekanslarını say
            cift_frekanslari = self._cift_frekanslarini_say(kelime_frekanslari)
            if not cift_frekanslari:
                print("Birleştirilecek çift kalmadı. Eğitim durduruluyor.")
                break
            # Adım 3.2: En iyi çifti seç
            en_iyi_cift = self._en_iyi_cifti_sec(cift_frekanslari)
            yeni_token = en_iyi_cift[0] + en_iyi_cift[1]
            if not en_iyi_cift:
                print("Birleştirilecek çift kalmadı. Eğitim durduruluyor.")
                break


            
            self.merge_kurallari.append(en_iyi_cift)
            vocab_set.add(yeni_token)


            if yazdirma:
                print(f"Iterasyon {iterasyon}: En iyi çift: {en_iyi_cift}, Yeni token: {yeni_token}, Vocab boyutu: {len(vocab_set)}")

            kelime_frekanslari = self._birleştirme_uygulama(kelime_frekanslari, en_iyi_cift)
            
            self.vocab = {token: idx for idx, token in enumerate(sorted(vocab_set))}
            
    def tokenize(self, metin: str) -> list:
        if not self.merge_kurallari:
            raise ValueError("Tokenizer eğitilmemiş. Lütfen önce 'egit' metodunu çağırın.")
        
        metin = metin.lower()
        metin = re.sub(r"[^\w\s]", "", metin)  # Noktalama işaretlerini kaldır
        sonuclar = []

        for kelime in metin.split():
            token_dizisi = list(kelimeyi_karakterlere_bol(kelime))
            for sol, sağ in self.merge_kurallari:
                yeni_dizi = []
                i = 0
                while i < len(token_dizisi):
                    if i < len(token_dizisi) - 1 and token_dizisi[i] == sol and token_dizisi[i + 1] == sağ:
                        yeni_dizi.append(sol + sağ)
                        i += 2
                    else:
                        yeni_dizi.append(token_dizisi[i])
                        i += 1
                token_dizisi = yeni_dizi
            sonuclar.append(token_dizisi)
        return sonuclar
    
    def json_yukle(self, dosya_yolu: str):
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            veri = json.load(f)
            self.merge_kurallari = [tuple(k) for k in veri['merge_kurallari']]
            self.vocab = veri['vocab']
            self.hedef_vocab_size = veri['hedef_vocab_size']
            
        print(f"JSON dosyası yüklendi: {dosya_yolu}. Merge kuralları ve vocab güncellendi.")
        print(f"Merge kuralları: {self.merge_kurallari}")
        print(f"Vocab: {self.vocab}")
        print(f'vocab boyutu: {len(self.vocab)}')

    def json_kaydet(self, dosya_yolu: str):
        veri = {
            "vocab" : self.vocab,
            "merge_kurallari" : [list(cift) for cift in self.merge_kurallari],
            "hedef_vocab_size" : self.hedef_vocab_size
        }
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=True, indent=4)

        print(f"JSON dosyası kaydedildi: {dosya_yolu}. Merge kuralları ve vocab dışa aktarıldı.")