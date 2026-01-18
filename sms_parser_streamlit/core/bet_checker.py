# core/bet_checker.py
import itertools
from config.constants import DAI_XO_SO

class BetChecker:
    def __init__(self, kqxs_data):
        self.kqxs = kqxs_data 

    def get_station_result(self, dai_raw):
        """
        Tìm kết quả của MỘT đài cụ thể.
        Trả về: List số hoặc None
        """
        dai_raw = dai_raw.strip()
        # 1. Tìm trực tiếp
        if dai_raw in self.kqxs:
            return self.kqxs[dai_raw]
        
        # 2. Tìm qua config/viết tắt
        for key_config, synonyms in DAI_XO_SO.items():
            if dai_raw.lower() == key_config.lower() or dai_raw.lower() in [s.lower() for s in synonyms]:
                if key_config in self.kqxs:
                    return self.kqxs[key_config]
        return None

    def check_cuoc(self, cuoc):
        list_dai_names = [d.strip() for d in cuoc.ten_dai.split(',')]
        
        # Kiểm tra xem có dữ liệu của đài nào không
        found_any_station = False
        valid_stations = {} # { "Tên Đài": [List Số] }

        for name in list_dai_names:
            res = self.get_station_result(name)
            if res:
                valid_stations[name] = res
                found_any_station = True
        
        if not found_any_station:
            return {
                "status": "pending", 
                "message": f"Chưa có KQ đài {cuoc.ten_dai}", 
                "win_count": 0, 
                "winning_numbers": []
            }

        win_total = 0
        detail = []
        winning_numbers = set()

        # LOGIC DÒ TÁCH BIỆT TỪNG ĐÀI
        for station_name, results in valid_stations.items():
            # results[0] -> G8, results[-1] -> ĐB
            
            # 1. BAO LÔ (18 giải)
            if cuoc.loai_cuoc in ['bao', 'blo', 'b']:
                for so in cuoc.so_danh:
                    hits = 0
                    for res in results:
                        if len(res) >= len(so) and res.endswith(so):
                            hits += 1
                    if hits > 0:
                        win_total += hits
                        detail.append(f"Lô {so} ({station_name}: {hits} con)")
                        winning_numbers.add(so)

            # 2. ĐẦU (G8 - Index 0)
            elif cuoc.loai_cuoc in ['dau', 'ddau']:
                g8 = results[0]
                for so in cuoc.so_danh:
                    if g8.endswith(so):
                        win_total += 1
                        detail.append(f"Đầu {so} ({station_name})")
                        winning_numbers.add(so)

            # 3. ĐUÔI (ĐB - Index cuối)
            elif cuoc.loai_cuoc in ['duoi']:
                db = results[-1]
                for so in cuoc.so_danh:
                    if db.endswith(so):
                        win_total += 1
                        detail.append(f"Đuôi {so} ({station_name})")
                        winning_numbers.add(so)

            # 4. ĐẦU ĐUÔI (G8 + ĐB)
            elif cuoc.loai_cuoc in ['dd']:
                targets = [results[0], results[-1]]
                for so in cuoc.so_danh:
                    cnt = 0
                    for t in targets:
                        if t.endswith(so): cnt += 1
                    if cnt > 0:
                        win_total += cnt
                        detail.append(f"Đầu Đuôi {so} ({station_name})")
                        winning_numbers.add(so)

            # 5. ĐÁ / XIÊN (Cần logic đặc biệt: Xiên có thể ghép cùng 1 đài hoặc khác đài?)
            # Thường Đá thẳng là cùng 1 đài. Đá xiên quay là nhiều đài.
            # Ở đây ta giữ logic đơn giản: Gom tất cả số trúng của mọi đài vào 1 pool rồi tính xiên.
            pass 

        # --- XỬ LÝ RIÊNG CHO ĐÁ/XIÊN (Gom pool số trúng của tất cả đài) ---
        if cuoc.loai_cuoc in ['da', 'dax', 'daxien']:
            all_hits_msg = []
            found_nums = set()
            
            # Tìm tất cả số xuất hiện trong tất cả các đài đã chọn
            for st_name, res_list in valid_stations.items():
                for so in cuoc.so_danh:
                    # Lô 18 giải
                    for r in res_list:
                        if r.endswith(so):
                            found_nums.add(so)
                            # Lưu lại để báo cáo (số này nổ ở đài nào)
                            # all_hits_msg.append(f"{so} ({st_name})") 
                            break 

            if len(cuoc.so_danh) >= 2:
                pairs = list(itertools.combinations(cuoc.so_danh, 2))
                for p1, p2 in pairs:
                    if p1 in found_nums and p2 in found_nums:
                        win_total += 1
                        detail.append(f"Xiên {p1}-{p2}")
                        winning_numbers.add(p1); winning_numbers.add(p2)
        
        # --- XỬ LÝ XỈU CHỦ (Tách đài) ---
        elif cuoc.loai_cuoc in ['xc', 'xcduoi']:
             for station_name, results in valid_stations.items():
                db = results[-1]
                for so in cuoc.so_danh:
                    if len(db) >= 3 and db.endswith(so):
                        win_total += 1
                        detail.append(f"XC {so} ({station_name})")
                        winning_numbers.add(so)

        elif cuoc.loai_cuoc in ['xcdau']:
             for station_name, results in valid_stations.items():
                if len(results) > 1: # G7 thường ở vị trí index 1
                    g7 = results[1]
                    for so in cuoc.so_danh:
                        if len(g7) >= 3 and g7.endswith(so):
                            win_total += 1
                            detail.append(f"XC Đầu {so} ({station_name})")
                            winning_numbers.add(so)

        if win_total > 0:
            return {"status": "win", "message": ", ".join(detail), "win_count": win_total, "winning_numbers": list(winning_numbers)}
        else:
            return {"status": "lose", "message": "Trượt", "win_count": 0, "winning_numbers": []}
