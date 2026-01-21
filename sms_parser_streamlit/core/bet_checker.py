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
                # === [LOGIC MỚI] LÀM SẠCH DỮ LIỆU MIỀN BẮC ===
                # Nếu là Miền Bắc, tìm giải ĐB (5 số) đầu tiên, cắt bỏ phần rác phía trước
                if name == 'Miền Bắc' and len(res) > 0:
                    try:
                        # Tìm vị trí (index) của số đầu tiên có độ dài >= 5 (Giải ĐB)
                        idx_db = next(i for i, x in enumerate(res) if len(str(x)) >= 5)
                        # Cắt bỏ toàn bộ phần rác đứng trước giải ĐB
                        res = res[idx_db:]
                    except StopIteration:
                        # Nếu không tìm thấy số nào 5 chữ số (Dữ liệu lỗi), giữ nguyên
                        pass
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
                        detail.append(f"Lô {so} ({station_name}: {hits} lần)")
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
            # [MỚI] 6. 3 CON BAO ĐẢO (3CBĐ)
            elif cuoc.loai_cuoc in [ 'baodao', 'bdao']:
                for so in cuoc.so_danh:
                    # Bỏ qua nếu số quá ngắn (vd đánh đảo số '1')
                    if len(so) < 2: continue 

                    # 1. Sinh hoán vị (Tự động xử lý 3 số hay 4 số)
                    # Dùng set để loại bỏ số trùng (VD: 112 đảo chỉ ra 112, 121, 211)
                    perms = set([''.join(p) for p in itertools.permutations(so)])
                    
                    hit_total_so = 0 # Tổng số lần trúng của cụm này
                    
                    # 2. Dò từng số hoán vị với bảng kết quả
                    for p_so in perms:
                        hits_p = 0
                        for res in results:
                            # Tự động kiểm tra độ dài:
                            # Nếu đánh 4 con, giải nào có 2,3 số sẽ bị bỏ qua
                            if len(res) >= len(p_so) and res.endswith(p_so):
                                hits_p += 1
                        
                        if hits_p > 0:
                            hit_total_so += hits_p
                            # Chi tiết: Ghi rõ trúng số nào (đảo) từ số gốc nào
                            detail.append(f"Đảo {p_so} (gốc {so}) ({station_name}: {hits_p} lần)")
                    
                    if hit_total_so > 0:
                        win_total += hit_total_so
                        winning_numbers.add(so)

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
        elif cuoc.loai_cuoc in ['xc', 'xcdd', 'xcduoi', 'xcdau']:
             for station_name, results in valid_stations.items():
                is_mb = (station_name == 'Miền Bắc')
                targets = []

                # --- BƯỚC 1: XÁC ĐỊNH GIẢI ĐẦU & GIẢI ĐUÔI ---
                
                # A. MIỀN BẮC (Logic riêng theo yêu cầu)
                if is_mb:
                    # ĐUÔI = Giải Đặc Biệt (Nằm đầu danh sách index 0)
                    giai_duoi_list = [results[0]] if len(results) > 0 else []
                    
                    # ĐẦU = Giải 6 (Các giải có đúng 3 chữ số)
                    giai_dau_list = [r for r in results if len(r) == 3]

                # B. MIỀN NAM / TRUNG (Logic chuẩn)
                else:
                    # ĐUÔI = Giải Đặc Biệt (Nằm cuối danh sách)
                    giai_duoi_list = [results[-1]] if len(results) > 0 else []
                    
                    # ĐẦU = Giải 7 (Nằm vị trí index 1, sau giải 8)
                    giai_dau_list = [results[1]] if len(results) > 1 else []

                # --- BƯỚC 2: CHỌN GIẢI DỰA VÀO LOẠI CƯỢC ---
                
                # Trường hợp 1: XC ĐUÔI -> Chỉ lấy Giải Đuôi (MB là ĐB, MN là ĐB)
                if cuoc.loai_cuoc == 'xcduoi':
                    targets.extend(giai_duoi_list)

                # Trường hợp 2: XC ĐẦU -> Chỉ lấy Giải Đầu (MB là G6, MN là G7)
                elif cuoc.loai_cuoc == 'xcdau':
                    targets.extend(giai_dau_list)

                # Trường hợp 3: XC (Cả Đầu + Đuôi)
                else: # 'xc', 'xcdd'
                    targets.extend(giai_duoi_list)
                    targets.extend(giai_dau_list)

                # --- BƯỚC 3: DÒ SỐ ---
                for so in cuoc.so_danh:
                    hits_in_station = 0
                    for val in targets:
                        # Chỉ dò nếu giải có đủ 3 số trở lên
                        if len(val) >= 3 and val.endswith(so):
                            hits_in_station += 1
                    
                    if hits_in_station > 0:
                        win_total += hits_in_station
                        detail.append(f"XC {so} ({station_name}: {hits_in_station} lần)")
                        winning_numbers.add(so)

        if win_total > 0:
            return {"status": "win", "message": ", ".join(detail), "win_count": win_total, "winning_numbers": list(winning_numbers)}
        else:
            return {"status": "lose", "message": "Thua", "win_count": 0, "winning_numbers": []}
        
