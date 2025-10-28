import requests
import json
import gzip
import logging
import time
from io import BytesIO
from requests.exceptions import RequestException, Timeout

# Log yapılandırması
logging.basicConfig(
    filename='kablo.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_canli_tv_m3u(max_retries=3, retry_delay=10):
    url = "https://core-api.kablowebtv.com/api/channels"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer <TOKEN>"  # Token'ı güvenli şekilde dışarıdan alman önerilir
    }

    for attempt in range(1, max_retries + 1):
        try:
            print(f"📡 API isteği gönderiliyor... (Deneme {attempt})")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            try:
                with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
                    content = gz.read().decode('utf-8')
            except OSError:
                content = response.content.decode('utf-8')

            data = json.loads(content)

            if not data.get('IsSucceeded') or not data.get('Data', {}).get('AllChannels'):
                logging.warning("API'den geçerli veri alınamadı.")
                print("❌ API'den geçerli veri alınamadı!")
                return False

            channels = data['Data']['AllChannels']
            print(f"✅ {len(channels)} kanal bulundu")

            with open("yeni.m3u", "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")

                kanal_sayisi = 0
                kanal_index = 1

                for channel in channels:
                    name = channel.get('Name')
                    stream_data = channel.get('StreamData', {})
                    hls_url = stream_data.get('HlsStreamUrl') if stream_data else None
                    logo = channel.get('PrimaryLogoImageUrl', '')
                    categories = channel.get('Categories', [])

                    if not name or not hls_url:
                        continue

                    group = categories[0].get('Name', 'Genel') if categories else 'Genel'
                    if group == "Bilgilendirme":
                        continue

                    tvg_id = str(kanal_index)
                    f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{name}\n')
                    f.write(f'{hls_url}\n')

                    kanal_sayisi += 1
                    kanal_index += 1

            print(f"📺 yeni.m3u dosyası oluşturuldu! ({kanal_sayisi} kanal)")
            logging.info(f"{kanal_sayisi} kanal başarıyla yazıldı.")
            return True

        except (RequestException, Timeout) as e:
            logging.error(f"API isteği başarısız: {e}")
            print(f"❌ API hatası: {e}")
            if attempt < max_retries:
                print(f"🔁 {retry_delay} saniye sonra tekrar denenecek...")
                time.sleep(retry_delay)
            else:
                print("⛔ Maksimum deneme sayısına ulaşıldı.")
                return False

        except Exception as e:
            logging.exception(f"Beklenmeyen hata: {e}")
            print(f"❌ Beklenmeyen hata: {e}")
            return False

if __name__ == "__main__":
    get_canli_tv_m3u()
