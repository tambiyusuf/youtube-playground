import json
import re   

from bpeTokenizer import BPETokenizer

with open("bpe_tokenizer/corpus.txt", "r", encoding="utf-8") as f:
    corpus = " ".join(satir.strip() for satir in f if satir.strip()
                    )

hedef_vocab_size = 250  # Hedeflenen vocab boyutu

tokenizer = BPETokenizer(hedef_vocab_size=hedef_vocab_size)
tokenizer.egit(corpus, yazdirma=True)

tokenizer.json_kaydet("bpe_tokenizer/bpe_sozluk.json")


yeni_tokenizer = BPETokenizer(hedef_vocab_size=hedef_vocab_size)
yeni_tokenizer.json_yukle("bpe_tokenizer/bpe_sozluk.json")

test_metin = "Dinamik ve Statik Hesaplama Grafikleri Dynamic and Static Computational Graphs"
print(f"Test metni: {test_metin}")
sonuclar = yeni_tokenizer.tokenize(test_metin)
print("Tokenizasyon sonuçları:")
for kelime, tokenler in zip(test_metin.split(), sonuclar):
    print(f"{kelime}: {tokenler}")
