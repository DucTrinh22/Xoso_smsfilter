# components/result_display.py
import streamlit as st
from config.constants import CAU_HINH_NHOM_CUOC
from core.classifier import phan_loai_nhom_cuoc 


def render_results(results, has_data=False):
    st.subheader(" Kết quả Phân tích")
    
    # --- BƯỚC 1: KHỞI TẠO DICTIONARY TỔNG HỢP ---
    # Dùng để lưu tổng xác của từng nhóm
    group_totals = {
        '2CB': 0, '3CB': 0, '4CB': 0,
        '3CXC': 0, '3CBĐ': 0, '3CXĐ': 0, '4CBĐ': 0,
        'ĐáT': 0, 'ĐáX': 0
    }
    # Biến để kiểm tra xem có cược nào được hiển thị không
    has_any_bet = False
    
    for res in results:
        ss = res["ss"]
        parse_res = res["parse"]
        check_results = res.get("check_results", [])
        
        # LOGIC MỚI: Chỉ hiển thị thắng/thua khi has_data = True
        if not ss.hop_le:
            status_icon = "❌"
            header_text = f"{status_icon} Cú pháp lỗi: {ss.tin_nhan_goc}"
        else:
            # Nếu CHƯA có data xổ số -> Chỉ hiển thị icon tick xanh (đã parse được)
            status_icon = "✅"
            header_text = f"{status_icon} {ss.tin_nhan_goc}"
            
        with st.expander(header_text, expanded=True):
            # Layout: Gốc | Sửa
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Tin nhắn gốc")
                st.text(ss.tin_nhan_goc)
            with c2:
                st.caption("Tin đã sửa")
                st.text(ss.tin_nhan_sau_sua)
                
            if ss.cac_loi:
                st.error("⚠️ " + " | ".join(ss.cac_loi))

            if ss.hop_le and parse_res and parse_res.hop_le:
                st.markdown("<hr style='margin: 5px 0px 10px 0px; border: 0; border-top: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
                
                # Duyệt từng cược
                for idx, cuoc in enumerate(parse_res.danh_sach_cuoc):
                    check_info = check_results[idx] if (check_results and idx < len(check_results)) else None
                    
                    # Style mặc định (Khi chưa dò hoặc không có mạng)
                    bg_color = "#f3f4f6" # Xám
                    border_color = "#9ca3af"
                    note_html = ""
                    
                    # Chỉ tô màu thắng thua nếu có dữ liệu
                    if has_data and check_info:
                        if check_info['status'] == 'win':
                            bg_color = "#d1fae5" # Xanh
                            border_color = "#10b981"
                            note_html = f"<br>🎁 <b style='color: #008000; font-size: 1.2em;'>{check_info['message']}</b>"
                        elif check_info['status'] == 'lose':
                            bg_color = "#fee2e2" # Đỏ
                            border_color = "#ef4444"
                            note_html = "<br>🌑 <i>Trượt</i>"
                        elif check_info['status'] == 'pending':
                             bg_color = "#fff7ed" # Cam
                             border_color = "#f97316"
                             note_html = f"<br>⏳ {check_info['message']}"

                    # LOGIC Lấy thông tin nhóm cược và tính xác
                    ma_nhom, cfg_nhom = phan_loai_nhom_cuoc(cuoc)

                    # Nếu hàm phân loại trả về None (không nhận ra Đầu/Đuôi), ta tự gán nó vào nhóm 2CB
                    if not ma_nhom and cuoc.ten_loai:
                        tl_tmp = cuoc.ten_loai.lower()
                        # Nếu có chữ 'đảo' và số đánh có 3 chữ số
                        if ('đảo' in tl_tmp or 'dao' in tl_tmp) and cuoc.so_danh and len(cuoc.so_danh[0]) == 3:
                             ma_nhom = '3CXĐ'
                        # Kiểm tra các từ khóa nhận diện Đầu/Đuôi
                        elif any(x in tl_tmp for x in ['đầu', 'đuôi', 'dau', 'duoi', 'dd']):
                            ma_nhom = '2CB'
                    
                    info_nhom_html = ""
                    if ma_nhom:
                        text_xac = ""
                        gia_tri_xac = 0
                        so_luong_so = len(cuoc.so_danh)
                        # Đếm số lượng đài dựa vào dấu phẩy trong tên đài (VD: "TP, DT" -> 2)
                        so_luong_dai = len(cuoc.ten_dai.split(",")) if cuoc.ten_dai else 0

                        # Kiểm tra có phải MB = miền bắc hay không 1 lần duy nhất
                        is_mb = False
                        if cuoc.ten_dai:
                            ten_dai_sms = cuoc.ten_dai.lower()
                            if "mb" in ten_dai_sms or "bắc" in ten_dai_sms:
                                is_mb = True

                        # Kiểm tra tên nếu là 2dmn và 3dmn
                        if cuoc.ten_dai:
                            ten_dai_sms = cuoc.ten_dai.lower()
                            if "2dmn" in ten_dai_sms or "2 đài" in ten_dai_sms:
                                so_luong_dai = 2
                            elif "3dmn" in ten_dai_sms or "3 đài" in ten_dai_sms:
                                so_luong_dai = 3
                        
                        # 1. Tính Xác cho ĐáX (Xiên 1 đài)
                        if ma_nhom == 'ĐáX':
                            # MN/MT: 18 giải, cho cho 1 đài  
                            he_so = 18
                            n = len(cuoc.so_danh)
                            if n >= 2:
                                so_cap = n * (n - 1) // 2
                            else: so_cap = 0
                            gia_tri_xac = 2 * cuoc.tien * he_so * so_cap

                        # 2. Tính Xác cho ĐáT (2 đài)
                        elif ma_nhom == 'ĐáT':
                            # MN/MT: 18 giải, MB: 27 giải
                            he_so = 27 if is_mb else 36
                            n = len(cuoc.so_danh)
                            if n >= 2:
                                so_cap = n * (n - 1) // 2
                            else: so_cap = 0
                            gia_tri_xac = 2 * cuoc.tien * he_so * so_cap

                        # 3. Tính Xác cho 2CB (Bao lô, Đầu, Đuôi, Đầu đuôi)
                        elif ma_nhom == '2CB':
                            # Lấy tên loại cược để kiểm tra (viết thường)
                            ten_loai_check = cuoc.ten_loai.lower() if cuoc.ten_loai else ""
                            he_so = 0

                            if is_mb:
                                # --- CẤU HÌNH MB ---
                                he_so = 27 # Bao lô MB (27 giải)
                                if 'đầu đuôi' in ten_loai_check or 'dd' in ten_loai_check:
                                    he_so = 5 # (Tùy chỉnh theo luật của bạn)
                                elif 'đầu' in ten_loai_check or 'dau' in ten_loai_check:
                                    he_so = 4 # 4 giải bảy
                                elif 'đuôi' in ten_loai_check or 'duoi' in ten_loai_check:
                                    he_so = 1 # 1 giải đặc biệt
                            else:
                                # --- CẤU HÌNH MN/MT ---
                                he_so = 18 # Bao lô MN (18 giải)
                                if 'đầu đuôi' in ten_loai_check or 'dd' in ten_loai_check:
                                    he_so = 2
                                elif 'đầu' in ten_loai_check or 'dau' in ten_loai_check:
                                    he_so = 1
                                elif 'đuôi' in ten_loai_check or 'duoi' in ten_loai_check:
                                    he_so = 1

                            if he_so > 0:
                                gia_tri_xac = so_luong_so * cuoc.tien * he_so * so_luong_dai

                        # 4. Tính Xác 3CB
                        elif ma_nhom == '3CB':
                            # MB: Có 27 giải nhưng 4 giải bảy chỉ có 2 số => Còn 23 giải
                            # MN/MT: Có 18 giải nhưng 1 giải tám chỉ có 2 số => Còn 17 giải
                            he_so_co_ban = 23 if is_mb else 17
                            
                            gia_tri_xac = so_luong_so * cuoc.tien * he_so_co_ban * so_luong_dai

                        # 5. Tính Xác 3CXC
                        elif ma_nhom in ['3CXC', '3CXCDau', '3CXCDuoi']:
                            ten_loai_check = cuoc.ten_loai.lower() if cuoc.ten_loai else ""
                            he_so = 0
                            if is_mb:
                                # MB: Đầu=3 (3 giải 6), Đuôi=1 (ĐB), Bao=4
                                cfg_dau = 3
                                cfg_duoi = 1
                                cfg_bao = 4
                            else:
                                # MN/MT: Đầu=1 (giải 7), Đuôi=1 (ĐB), Bao=2
                                cfg_dau = 1
                                cfg_duoi = 1
                                cfg_bao = 2
                            if 'đầu đuôi' in ten_loai_check or 'dd' in ten_loai_check:
                                he_so = cfg_bao
                            
                            # Ưu tiên 2: Kiểm tra Đầu (xcdau)
                            elif 'đầu' in ten_loai_check or 'dau' in ten_loai_check:
                                he_so = cfg_dau
                                
                            # Ưu tiên 3: Kiểm tra Đuôi (xcduoi)
                            elif 'đuôi' in ten_loai_check or 'duoi' in ten_loai_check:
                                he_so = cfg_duoi
                                
                            else:
                                # Trường hợp khách chỉ nhắn "xc 123" (không ghi rõ đầu đuôi)
                                # Mặc định hiểu là "Bao" (XC Bao)
                                he_so = cfg_bao
                            if he_so > 0:
                                gia_tri_xac = so_luong_so * cuoc.tien * he_so * so_luong_dai

                        # 6.Tính Xác 3CXĐ (3 Xỉu Chủ Đảo)
                        elif ma_nhom == '3CXĐ':
                            tong_hoan_vi = 0
                            for so in cuoc.so_danh:
                                if len(so) == 3:
                                    # Đếm số lượng ký tự duy nhất để xác định công thức
                                    so_luong_ky_tu = len(set(so))
                                    if so_luong_ky_tu == 3:
                                        tong_hoan_vi += 6   # 3 số khác nhau (ABC) -> 6 hoán vị
                                    elif so_luong_ky_tu == 2:
                                        tong_hoan_vi += 3   # 2 số giống (AAB) -> 3 hoán vị
                                    else:
                                        tong_hoan_vi += 1   # 3 số giống (AAA) -> 1 hoán vị
                                else:
                                    tong_hoan_vi += 1 # Fallback nếu số không phải 3 chữ số

                            if is_mb:
                                # MB: Hệ số 4 * Hoán vị (Theo yêu cầu)
                                he_so = 4
                                gia_tri_xac = tong_hoan_vi * cuoc.tien * he_so
                            else:
                                # MN/MT: Hệ số 4 * Hoán vị (Theo yêu cầu)
                                he_so = 2 
                                gia_tri_xac = tong_hoan_vi * cuoc.tien * he_so * so_luong_dai

                        # 7.Tính xác 3CBĐ (3 Con Bao Đảo)
                        elif ma_nhom == '3CBĐ':
                            tong_hoan_vi = 0
                            for so in cuoc.so_danh:
                                if len(so) == 3:
                                    # Đếm số lượng ký tự duy nhất để xác định công thức
                                    so_luong_ky_tu = len(set(so))
                                    if so_luong_ky_tu == 3:
                                        tong_hoan_vi += 6   # 3 số khác nhau (ABC) -> 6 hoán vị
                                    elif so_luong_ky_tu == 2:
                                        tong_hoan_vi += 3   # 2 số giống (AAB) -> 3 hoán vị
                                    else:
                                        tong_hoan_vi += 1   # 3 số giống (AAA) -> 1 hoán vị
                                else:
                                    tong_hoan_vi += 1 # Fallback nếu số không phải 3 chữ số

                            if is_mb:
                                # MB: Có 27 giải nhưng 4 giải bảy chỉ có 2 số => Còn 23 giải
                                he_so = 23
                                gia_tri_xac = tong_hoan_vi * cuoc.tien * he_so
                            else:
                                # MN/MT: Có 18 giải nhưng 1 giải tám chỉ có 2 số => Còn 17 giải
                                he_so = 17

                                gia_tri_xac = tong_hoan_vi * cuoc.tien * he_so * so_luong_dai

                        # 8. Tính Xác 4CB
                        elif ma_nhom == '4CB':
                            # MB: 27 giải - 4 giải bảy (2 số) - 3 giải sáu (3 số) = 20 giải
                            # MN: 18 giải - 1 giải tám (2 số) - 1 giải bảy (3 số) = 16 giải
                            he_so_co_ban = 20 if is_mb else 16

                            gia_tri_xac = so_luong_so * cuoc.tien * he_so_co_ban * so_luong_dai

                        # 9. Tính xác 4CBĐ (4 Con Bao Đảo)
                        elif ma_nhom == '4CBĐ':
                            tong_hoan_vi = 0
                            for so in cuoc.so_danh:
                                if len(so) == 4:
                                    # Tạo danh sách số lần xuất hiện của từng ký tự
                                    # Ví dụ: 1234 -> [1,1,1,1]; 1123 -> [1,1,2]; 1122 -> [2,2]; 1112 -> [1,3]
                                    counts = sorted([so.count(char) for char in set(so)])
                                    
                                    if counts == [1, 1, 1, 1]:      # ABCD (4 số khác nhau)
                                        tong_hoan_vi += 24
                                    elif counts == [1, 1, 2]:       # AABC (1 đôi)
                                        tong_hoan_vi += 12
                                    elif counts == [2, 2]:          # AABB (2 đôi)
                                        tong_hoan_vi += 6
                                    elif counts == [1, 3]:          # AAAB (3 số giống nhau)
                                        tong_hoan_vi += 4
                                    else:                           # AAAA (4 số giống nhau)
                                        tong_hoan_vi += 1
                                else:
                                    tong_hoan_vi += 1 # Fallback nếu số không phải 4 chữ số
                                    
                            if is_mb:
                                he_so = 20
                                gia_tri_xac = tong_hoan_vi * cuoc.tien * he_so
                            else:
                                he_so = 16
                                gia_tri_xac = tong_hoan_vi * cuoc.tien * he_so * so_luong_dai

                        # --- BƯỚC 2: CỘNG DỒN VÀO DICTIONARY ---
                        if gia_tri_xac > 0:
                            # Chuẩn hóa tên nhóm cho trường hợp XC (3CXCDau/Duoi -> 3CXC)
                            key_nhom = ma_nhom
                            if ma_nhom in ['3CXCDau', '3CXCDuoi']:
                                key_nhom = '3CXC'
                            
                            # Cộng tiền nếu nhóm nằm trong danh sách theo dõi
                            if key_nhom in group_totals:
                                group_totals[key_nhom] += gia_tri_xac
                            
                            text_xac = f" | Xác: <span style='color:#d63031'>{gia_tri_xac:,.0f}đ</span>".replace(",", ".")
                            has_any_bet = True

                        info_nhom_html = f"<div style='margin-top: 5px; padding-top: 4px; border-top: 1px dashed #ccc; font-weight: bold; color: #333;'>Nhóm: {ma_nhom} {text_xac}</div>"
                    
                    # --- Tạo khối hiển thị cuối cùng ---
                    # Lưu ý: Tôi đã bỏ các comment <!-- --> để tránh lỗi hiển thị HTML thừa
                    msg_html = f"""
                    <div style="
                        padding: 10px 12px; 
                        margin-bottom: 8px; 
                        border-radius: 6px; 
                        background-color: {bg_color}; 
                        border-left: 5px solid {border_color};
                        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                    ">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div style="flex-grow:1;">
                                <b>[{cuoc.ten_dai}]</b> {cuoc.ten_loai}: <b style="font-size:1.1em; color:#1f2937">{', '.join(cuoc.so_danh)}</b>
                            </div>
                            <div style="font-weight:bold; color:#111827; background:#fff; padding:2px 8px; border-radius:4px; border:1px solid #ddd; margin-left:10px; white-space:nowrap;">
                                {cuoc.tien_format}
                            </div>
                        </div>
                        {note_html}
{info_nhom_html}
                    </div>
                    """
                    st.markdown(msg_html, unsafe_allow_html=True)
                    

    # --- BƯỚC 3: HIỂN THỊ TỔNG KẾT THEO TỪNG NHÓM ---
    if has_any_bet:
        
        # Tạo danh sách các nhóm có tiền để hiển thị
        active_groups = []
        # Thứ tự hiển thị mong muốn
        display_order = ['2CB', '3CB', '4CB', '3CXC', 'ĐáX', 'ĐáT','3CBĐ', '3CXĐ' '4CBĐ']
        
        for key in display_order:
            tong_xac = group_totals.get(key, 0)
            if tong_xac > 0:
                qua_co = tong_xac * 0.8
                active_groups.append({
                    "nhom": key,
                    "xac": tong_xac,
                    "quaco": qua_co
                })
        
        # Render ra giao diện (Mỗi dòng 2 nhóm hoặc 1 dòng tùy ý)
        if has_any_bet:
            st.markdown("---")
            
            # Danh sách thứ tự hiển thị
            display_order = ['2CB', 'ĐáX', 'ĐáT', '3CB', '3CXC', '3CXĐ', '3CBĐ', '4CBĐ', '4CB']
            
            # Biến tính tổng tiền qua cò
            total_quaco_all = 0
            
            # Tạo 2 cột: Cột trái (Xác) - Cột phải (Qua cò)
            c1, c2 = st.columns(2)
            
            # --- CỘT 1: HIỂN THỊ TỔNG XÁC ---
            with c1:
                st.markdown("##### 📝 Tổng Xác")
                html_xac = "" # Biến chưa nội dung html
                for key in display_order:
                    val = group_totals.get(key, 0)
                    if val > 0:
                        # Format số tiền: 3,645
                        str_val = f"{val:,.0f}".replace(",", ".")
                        # Thay đổi số '4px' ở dưới để chỉnh khoảng cách
                        html_xac += f"<div style='margin-bottom: 4px; font-size: 16px;'><b>{key}</b>: {str_val}</div>"
                
                # Render 1 lần duy nhất
                st.markdown(html_xac, unsafe_allow_html=True)

            # --- CỘT 2: HIỂN THỊ QUA CÒ & TÍNH TỔNG ---
            with c2:
                st.markdown("##### 💸 Qua Cò (x0.8)")
                html_quaco = "" # Biến chưa nội dung html
                for key in display_order:
                    val = group_totals.get(key, 0)
                    if val > 0:
                        # Tính qua cò
                        quaco = val * 0.8
                        total_quaco_all += quaco
                        
                        # Format số tiền
                        str_quaco = f"{quaco:,.0f}".replace(",", ".")
                        html_quaco += f"<div style='margin-bottom: 4px; font-size: 16px;'><b>{key}</b>: {str_quaco}</div>"
                
                # Render 1 lần duy nhất
                st.markdown(html_quaco, unsafe_allow_html=True)

            # --- HIỂN THỊ TỔNG CỘNG TIỀN QUA CÒ ---
            st.divider()
            st.success(f"💰 **TỔNG CỘNG (Qua Cò): {total_quaco_all:,.0f}đ**".replace(",", "."))
