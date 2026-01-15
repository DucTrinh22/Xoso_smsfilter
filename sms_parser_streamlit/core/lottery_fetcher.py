# core/lottery_fetcher.py
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime

class MinhNgocFetcher:
    def __init__(self):
        # Dùng giao diện In Vé Dò -> HTML sạch, dễ lấy, ít bị chặn
        self.base_url = "https://www.minhngoc.net.vn/in-ve-do/mien-nam.html?ngay={date}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_data(self, date_str):
        """
        Trả về dict: { 'Tên Tỉnh': ['số G8', ..., 'số ĐB'] }
        Danh sách số sẽ được sort tự động từ Giải 8 -> Giải ĐB do cấu trúc trang web.
        """
        # Đảm bảo date_str đúng định dạng dd-mm-yyyy
        url = self.base_url.format(date=date_str)
        print(f"Fetching: {url}") # Debug link
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                print(f"Lỗi kết nối: {response.status_code}")
                return {}

            soup = BeautifulSoup(response.content, 'html.parser')
            results = {}
            
            # Tìm tất cả các bảng kết quả (class 'bkqt')
            tables = soup.find_all('table', class_='bkqt')
            
            if not tables:
                print("Không tìm thấy bảng kết quả (Sai cấu trúc HTML hoặc chưa có KQ)")
                return {}

            for table in tables:
                # 1. Lấy tên tỉnh (nằm trong td class='tinh')
                tinh_node = table.find(class_='tinh')
                if not tinh_node: 
                    continue
                
                raw_name = tinh_node.get_text(strip=True)
                prov_name = self._normalize_station_name(raw_name)
                
                # 2. Lấy tất cả các số trong bảng
                # Duyệt qua từng ô (td) và tìm số
                numbers = []
                # Loại bỏ các dòng tiêu đề, chỉ lấy dòng chứa số
                rows = table.find_all('tr')
                for row in rows:
                    tds = row.find_all('td')
                    for td in tds:
                        # Bỏ qua ô tên tỉnh và ô tên giải (thường có class, hoặc chứa text không phải số)
                        if 'tinh' in td.get('class', []) or 'ngay' in td.get('class', []):
                            continue
                            
                        txt = td.get_text(strip=True)
                        
                        # Dùng Regex để bắt số (2 đến 6 chữ số)
                        # Regex này xử lý được cả trường hợp "123 - 456"
                        found_nums = re.findall(r'\d{2,6}', txt)
                        if found_nums:
                            numbers.extend(found_nums)
                
                # XSMN/MT chuẩn có 18 lô giải
                if len(numbers) >= 18:
                    results[prov_name] = numbers
            
            return results

        except Exception as e:
            print(f"Exception fetching data: {e}")
            return {}

    def get_lottery_table_df(self, date_str):
        """Tạo DataFrame để hiển thị lên UI"""
        data = self.fetch_data(date_str)
        if not data:
            return None
        
        # Mapping index hiển thị
        prizes_index = ["G8", "G7", "G6", "G5", "G4", "G3", "G2", "G1", "ĐB"]
        # Cấu trúc giải MN: 1, 1, 3, 1, 7, 2, 1, 1, 1 (Tổng 18 số)
        structure = [1, 1, 3, 1, 7, 2, 1, 1, 1]
        
        df_data = {}
        for prov, nums in data.items():
            # Chỉ xử lý nếu đủ 18 số (tránh lỗi index)
            if len(nums) < 18: continue
            
            col = []
            idx = 0
            for count in structure:
                # Lấy slice các số thuộc giải đó
                prize_nums = nums[idx : idx + count]
                # Nối lại thành chuỗi (ví dụ G6 có 3 số: "123 - 456 - 789")
                col.append(" - ".join(prize_nums))
                idx += count
            
            df_data[prov] = col
            
        if not df_data: return None

        return pd.DataFrame(df_data, index=prizes_index)

    def _normalize_station_name(self, name):
        name_lower = name.lower()
        # Mapping tên từ Web sang tên chuẩn trong Config
        mapping = {
            'tp.hcm': 'Tp.Hcm', 'thành phố': 'Tp.Hcm', 'sài gòn': 'Tp.Hcm',
            'kiên giang': 'Kiên Giang', 'lâm đồng': 'Đà Lạt', 'đà lạt': 'Đà Lạt',
            'tiền giang': 'Tiền Giang', 'cà mau': 'Cà Mau', 'đồng tháp': 'Đồng Tháp',
            'bạc liêu': 'Bạc Liêu', 'bến tre': 'Bến Tre', 'vũng tàu': 'Vũng Tàu',
            'cần thơ': 'Cần Thơ', 'đồng nai': 'Đồng Nai', 'sóc trăng': 'Sóc Trăng',
            'an giang': 'An Giang', 'tây ninh': 'Tây Ninh', 'bình thuận': 'Bình Thuận',
            'bình dương': 'Bình Dương', 'trà vinh': 'Trà Vinh', 'vĩnh long': 'Vĩnh Long',
            'long an': 'Long An', 'hậu giang': 'Hậu Giang', 'bình phước': 'Bình Phước',
            'bình định': 'Bình Định', 'gia lai': 'Gia Lai', 'ninh thuận': 'Ninh Thuận',
            'đà nẵng': 'Đà Nẵng', 'quảng nam': 'Quảng Nam', 'đắk lắk': 'Đắk Lắk',
            'quảng ngãi': 'Quảng Ngãi', 'thừa thiên huế': 'Thừa Thiên Huế',
            'phú yên': 'Phú Yên', 'khánh hòa': 'Khánh Hòa', 'kon tum': 'Kon Tum',
            'đắk nông': 'Đắk Nông', 'quảng trị': 'Quảng Trị', 'quảng bình': 'Quảng Bình'
        }
        for k, v in mapping.items():
            if k in name_lower:
                return v
        return name.title()
    