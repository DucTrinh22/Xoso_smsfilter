# core/bet_checker.py
import itertools
from config.constants import DAI_XO_SO

class BetChecker:
    def __init__(self, kqxs_data):
        self.kqxs = kqxs_data 

    def find_station_results(self, ten_dai_code):
        # 1. Tìm tên đầy đủ từ Config
        target_full_name = None
        for full, shorts in DAI_XO_SO.items():
            if ten_dai_code.lower() in [s.lower() for s in shorts]:
                target_full_name = full
                break
        
        if not target_full_name: return []

        # 2. Lấy data từ dict kqxs
        # Do đã normalize ở Fetcher nên tỉ lệ khớp key rất cao
        return self.kqxs.get(target_full_name, [])

    def check_cuoc(self, cuoc):
        results = self.find_station_results(cuoc.ten_dai)
        
        if not results:
            return {"status": "pending", "message": f"Chưa có KQ đài {cuoc.ten_dai}"}

        win_count = 0
        detail = []
        
        # --- LOGIC DÒ XSMN/XSMT (18 Lô) ---
        # List results: index 0 là G8, index -1 là ĐB
        
        # 1. BAO LÔ
        if cuoc.loai_cuoc in ['bao', 'blo', 'b']:
            for so in cuoc.so_danh:
                hits = 0
                for res in results:
                    if len(res) >= 2 and res.endswith(so):
                        hits += 1
                if hits > 0:
                    win_count += hits
                    detail.append(f"Lô {so} ({hits} nháy)")

        # 2. ĐẦU (Giải 8 - Index 0)
        elif cuoc.loai_cuoc in ['dau', 'ddau']:
            g8 = results[0]
            for so in cuoc.so_danh:
                if g8.endswith(so):
                    win_count += 1
                    detail.append(f"Đầu {so}")

        # 3. ĐUÔI (Giải ĐB - Index cuối cùng)
        elif cuoc.loai_cuoc in ['duoi']:
            db = results[-1]
            for so in cuoc.so_danh:
                if db.endswith(so):
                    win_count += 1
                    detail.append(f"Đuôi {so}")

        # 4. ĐÁU ĐUÔI (Đầu + Đuôi)
        elif cuoc.loai_cuoc in ['dd']:
            g8 = results[0]
            db = results[-1]
            for so in cuoc.so_danh:
                cnt = 0
                if g8.endswith(so): cnt += 1
                if db.endswith(so): cnt += 1
                if cnt > 0:
                    win_count += cnt
                    detail.append(f"Đầu Đuôi {so} ({cnt} nháy)")

        # 5. ĐÁ / XIÊN
        elif cuoc.loai_cuoc in ['da', 'dax', 'daxien']:
            # Tìm các số có xuất hiện trong bảng (2 số cuối)
            found_nums = set()
            for so in cuoc.so_danh:
                for res in results:
                    if res.endswith(so):
                        found_nums.add(so)
                        break
            
            # Logic tính tổ hợp đá
            if len(cuoc.so_danh) >= 2:
                pairs = list(itertools.combinations(cuoc.so_danh, 2))
                for p1, p2 in pairs:
                    if p1 in found_nums and p2 in found_nums:
                        win_count += 1
                        detail.append(f"Xiên {p1}-{p2}")

        # 6. XỈU CHỦ (3 số cuối giải ĐB)
        elif cuoc.loai_cuoc in ['xc', 'xcduoi']:
            db = results[-1]
            for so in cuoc.so_danh:
                if len(db) >= 3 and db.endswith(so):
                    win_count += 1
                    detail.append(f"XC {so}")

        if win_count > 0:
            return {"status": "win", "message": ", ".join(detail), "win_count": win_count}
        else:
            return {"status": "lose", "message": "Trượt", "win_count": 0}