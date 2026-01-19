import requests
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta

def round_to_10min(dt):
    """將時間四捨五入到最近的10分鐘"""
    minute = (dt.minute // 10) * 10
    return dt.replace(minute=minute, second=0, microsecond=0)

def get_latest_image_url():
    """獲取最新的圖片URL"""
    UTC8 = timezone(timedelta(hours=8))
    now = datetime.now(UTC8)
    current_time = round_to_10min(now)
    start_time = current_time - timedelta(minutes=30)
    
    yyyymm = start_time.strftime('%Y%m')
    yyyymmdd = start_time.strftime('%Y%m%d')
    yyyymmddhhmm = start_time.strftime('%Y%m%d%H%M')
    
    url = f"https://watch.ncdr.nat.gov.tw/00_Wxmap/7A13_RAIN_KINETIC_ENERGY/{yyyymm}/{yyyymmdd}/rke_{yyyymmddhhmm}.png"
    
    return url

def download_image(url):
    """下載圖片並返回PIL Image對象"""
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    return None

def process_image(base_img, overlay_img):
    """處理圖片：縮放去背圖、裁切、疊加到底圖"""
    base_width, base_height = base_img.size
    
    overlay_resized = overlay_img.resize((base_width, base_height))
    
    left = 481
    top = 129
    right = 2048
    bottom = 1577
    
    overlay_cropped = overlay_resized.crop((left, top, right, bottom))
    
    if overlay_cropped.mode != 'RGBA':
        overlay_cropped = overlay_cropped.convert('RGBA')
    
    base_cropped = base_img.crop((left, top, right, bottom))
    
    if base_cropped.mode != 'RGBA':
        base_cropped = base_cropped.convert('RGBA')
    
    result = Image.new('RGBA', base_cropped.size)
    result.paste(base_cropped, (0, 0))
    result.paste(overlay_cropped, (0, 0), overlay_cropped)
    
    return result

def main():
    base_url = "https://raw.githubusercontent.com/gyrreegr/think7/main/rain1.png"
    
    base_img = download_image(base_url)
    if not base_img:
        return
    
    overlay_url = get_latest_image_url()
    overlay_img = download_image(overlay_url)
    
    if overlay_img:
        result = process_image(base_img, overlay_img)
        result.save('rainkineticphoto.png')

if __name__ == "__main__":

    main()
