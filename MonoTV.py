import re
from httpx import Client
from Kekik.cli import konsol as log

class MonoTV:
    def __init__(self, m3u_dosyasi):
        self.m3u_dosyasi = m3u_dosyasi
        self.httpx = Client(timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })

    def yayin_urlini_al(self):
        kontrol_url = "https://monotv.xyz/channel.html?id=yayin1"
        try:
            response = self.httpx.get(kontrol_url)
            response.raise_for_status()
        except Exception as e:
            raise ValueError(f"MonoTV yayın kontrol URL'si alınamadı: {e}")

        if yayin := re.search(r'(?:var|let|const)\s+baseurl\s*=\s*"(https?://[^"]+)"', response.text):
            return yayin[1]
        else:
            raise ValueError("MonoTV yayın URL'si bulunamadı!")

    def m3u_guncelle(self):
        with open(self.m3u_dosyasi, "r") as dosya:
            icerik = dosya.read()

        eski_url = re.search(r'https?:\/\/[^\/]+\.(shop|click|lat)\/?', icerik)
        if not eski_url:
            raise ValueError("M3U dosyasında eski yayın URL'si bulunamadı!")

        eski_url = eski_url[0]
        log(f"[yellow][~] Eski Yayın URL : {eski_url}")

        yeni_url = self.yayin_urlini_al()
        log(f"[green][+] Yeni Yayın URL : {yeni_url}")

        yeni_icerik = icerik.replace(eski_url, yeni_url)

        with open(self.m3u_dosyasi, "w") as dosya:
            dosya.write(yeni_icerik)

if __name__ == "__main__":
    MonoTV("1.m3u").m3u_guncelle()
