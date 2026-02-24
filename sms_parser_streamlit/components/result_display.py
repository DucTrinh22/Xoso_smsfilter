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
            # Layout: tin đã Sửa
            st.markdown(f"**Tin đã sửa:** `{ss.tin_nhan_sau_sua}`")
                
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
                            note_html = f"<br>🎁 <i>TRÚNG<i> <b style='color: #008000; font-size: 1.2em;'>{check_info['message']}</b>"
                        elif check_info['status'] == 'lose':
                            bg_color = "#fee2e2" # Đỏ
                            border_color = "#ef4444"
                            note_html = "<br>🌑 <i>THUA</i>"
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
                        
                        # Kiểm tra dựa trên ma_nhom HOẶC tên loại cược để đảm bảo bắt dính
                        if ma_nhom in ['ĐáX', 'ĐáT'] or 'đá' in (cuoc.ten_loai.lower() if cuoc.ten_loai else ''):
                            n = len(cuoc.so_danh)
                            # Tính số cặp: nC2
                            if n >= 2:
                                so_cap = n * (n - 1) // 2
                            else:
                                so_cap = 0
                            
                            ten_loai_str = cuoc.ten_loai.lower() if cuoc.ten_loai else ""
                            
                            if is_mb:
                                # Miền Bắc: Luôn tính hệ số 54 (Đá Thường)
                                he_so = 54
                            else:
                                # Miền Nam / Miền Trung
                                # Nếu là Đá Thường (ĐáT) hoặc 2dmn va 3dmn
                                if ma_nhom == 'ĐáT' or 'đá' in ten_loai_str or so_luong_dai == 2:
                                    he_so = 36
                                elif ma_nhom == 'ĐáX' or 'xiên' in ten_loai_str or so_luong_dai == 1:
                                    # Đá Xiên (áp dụng cho 1 đài)
                                    he_so = 18 
                            
                            # --- TÍNH TIỀN XÁC ---
                            # Công thức: Tiền x Hệ số x Số Cặp
                            gia_tri_xac = cuoc.tien * he_so * so_cap * so_luong_dai

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

                            # --- LOGIC TÍNH HỆ SỐ ---
                            ten_loai_check = cuoc.ten_loai.lower() if cuoc.ten_loai else ""
                            he_so = 0
                            
                            if is_mb:
                                # MB: Đầu (3 giải), Đuôi (1 giải), Bao (4 giải)
                                if 'đầu đuôi' in ten_loai_check or 'dd' in ten_loai_check:
                                    he_so = 4
                                elif 'đầu' in ten_loai_check or 'dau' in ten_loai_check:
                                    he_so = 3 # Chỉ tính 3 giải đầu
                                elif 'đuôi' in ten_loai_check or 'duoi' in ten_loai_check:
                                    he_so = 1 # Chỉ tính 1 giải đuôi
                                else:
                                    he_so = 4 # Mặc định là đầu đuôi
                            else:
                                # MN/MT: Đầu (1 giải), Đuôi (1 giải), Bao (2 giải)
                                if 'đầu đuôi' in ten_loai_check or 'dd' in ten_loai_check:
                                    he_so = 2
                                elif 'đầu' in ten_loai_check or 'dau' in ten_loai_check:
                                    he_so = 1
                                elif 'đuôi' in ten_loai_check or 'duoi' in ten_loai_check:
                                    he_so = 1
                                else:
                                    he_so = 2 # Mặc định là đầu đuôi

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
                    ten_loai_hien_thi = cuoc.ten_loai
                    ten_dai_hien_thi = cuoc.ten_dai
                    
                    if cuoc.ten_dai:
                        ten_dai_lower = cuoc.ten_dai.lower()
                        # Nếu là Miền Bắc
                        if "mb" in ten_dai_lower or "bắc" in ten_dai_lower:
                            # 1. Đổi tên đài thành MB (nếu muốn gọn) hoặc giữ nguyên
                            # ten_dai_hien_thi = "MB" 
                            
                            # 2. Nếu là các loại đá, đổi tên thành "Đá Thường"
                            if cuoc.ten_loai and "đá" in cuoc.ten_loai.lower():
                                ten_loai_hien_thi = "Đá"
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
                                <b>[{ten_dai_hien_thi}]</b> {ten_loai_hien_thi}: <b style="font-size:1.3em; color:#1f2937">{', '.join(cuoc.so_danh)}</b>
                            </div>
                            <div style="font-size: 1.4em; font-weight:bold; color:#111827; background:#fff; padding:2px 8px; border-radius:4px; border:1.5px solid #ddd; margin-left:10px; white-space:nowrap;">
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
            
            group_top = ['2CB', 'ĐáX', 'ĐáT']
            group_bottom = ['3CB', '3CXC', '3CXĐ', '3CBĐ', '4CBĐ', '4CB']
            
            # Hàm hỗ trợ tạo HTML cho danh sách (Giúp code gọn hơn)
            def build_html_rows(key_list, totals_dict, is_quaco=False):
                html_out = ""
                has_data = False
                for key in key_list:
                    val = totals_dict.get(key, 0)
                    if val > 0:
                        has_data = True
                        final_val = val * 0.8 if is_quaco else val
                        str_val = f"{final_val:,.0f}".replace(",", ".")
                        
                        # Màu sắc khác nhau cho Xác và Cò
                        color = "#168612af" if is_quaco else "#995609" # Xanh lá hoặc Đỏ
                        
                        html_out += f"""
                        <div style='margin-bottom: 6px; font-size: 25px; color: #333;'>
                            <b>{key}: </b>
                            <span style='color:{color}; font-weight:bold;'>{str_val}</span>
                        </div>
                        """
                return html_out, has_data
            
            # Tùy chỉnh kích thước và màu sắc cho nhãn 2S, 3S
            STYLE_SUBTOTAL = {
                "bg_color": "#a15624",  # Màu nền tím nhạt (giống hình)
                "text_size": "24px",    # Kích thước chữ
                "text_color": "#FFFFFF",# Màu chữ
                "padding": "2px 10px",  # Khoảng cách đệm bên trong nhãn
                "border_radius": "8px"  # Độ bo góc
            }
            def render_subtotal_label(label, value):
                if value <= 0: return ""
                str_val = f"{value:,.0f}".replace(",", ".")
                return f"""
                <div style="
                    background-color: {STYLE_SUBTOTAL['bg_color']}; 
                    color: {STYLE_SUBTOTAL['text_color']}; 
                    font-size: {STYLE_SUBTOTAL['text_size']}; 
                    font-weight: bold; 
                    padding: {STYLE_SUBTOTAL['padding']}; 
                    border-radius: {STYLE_SUBTOTAL['border_radius']};
                    display: inline-block;
                    margin: 10px 0;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                ">
                    {label}= {str_val}
                </div>
                """
            # Tính tổng cho nhóm 2S (2CB + Đá)
            total_2s = (group_totals.get('2CB', 0) + 
                        group_totals.get('ĐáT', 0) + 
                        group_totals.get('ĐáX', 0))

            # Tính tổng cho nhóm 3S (Các nhóm còn lại)
            total_3s = (group_totals.get('3CB', 0) + 
                        group_totals.get('3CXC', 0) + 
                        group_totals.get('3CXĐ', 0) + 
                        group_totals.get('3CBĐ', 0) + 
                        group_totals.get('4CBĐ', 0) + 
                        group_totals.get('4CB', 0))

            # --- 2. TẠO HTML CHO TỪNG PHẦN ---
            # Cột Tổng Xác
            html_xac_top, has_xac_top = build_html_rows(group_top, group_totals, is_quaco=False)
            html_xac_bot, has_xac_bot = build_html_rows(group_bottom, group_totals, is_quaco=False)
            
            # Cột Qua Cò
            html_co_top, has_co_top = build_html_rows(group_top, group_totals, is_quaco=True)
            html_co_bot, has_co_bot = build_html_rows(group_bottom, group_totals, is_quaco=True)

            # Tính tổng tiền qua cò (để hiển thị ở mục Tổng Cộng to phía dưới)
            total_quaco_all = 0
            for k, v in group_totals.items():
                if v > 0: total_quaco_all += v * 0.8

            # --- 3. ĐỊNH NGHĨA ĐƯỜNG KẺ NGĂN CÁCH ---
            if has_any_bet:
                st.markdown("---")
                
                # Thiết lập nhóm
                group_top = ['2CB', 'ĐáX', 'ĐáT']
                group_bottom = ['3CB', '3CXC', '3CXĐ', '3CBĐ', '4CBĐ', '4CB']

                # 1. Hàm tạo nhãn (đã chỉnh size và bỏ margin thừa)
                def get_subtotal_label_html(label, value):
                    if value <= 0: return ""
                    str_val = f"{value:,.0f}".replace(",", ".")
                    return f"""
                    <div style="
                        background-color: #86471c; 
                        color: #FFFFFF; 
                        font-size: 20px; 
                        font-weight: bold; 
                        padding: 4px 10px; 
                        border-radius: 6px;
                        white-space: nowrap;
                        box-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                    ">
                        {label}= {str_val}
                    </div>
                    """

                # 2. Hàm tạo danh sách text số tiền
                def build_html_rows_only(key_list, totals_dict, is_quaco=False):
                    html_out = ""
                    count = 0
                    for key in key_list:
                        val = totals_dict.get(key, 0)
                        if val > 0:
                            count += 1
                            final_val = val * 0.8 if is_quaco else val
                            str_val = f"{final_val:,.0f}".replace(",", ".")
                            color = "#168612" if is_quaco else "#995609"
                            html_out += f"<div style='margin-bottom: 2px; font-size: 24px; color: #333;'><b>{key}: </b><span style='color:{color}; font-weight:bold;'>{str_val}</span></div>"
                    return html_out, count > 0

                # Tính toán tổng
                total_2s = sum(group_totals.get(k, 0) for k in group_top)
                total_3s = sum(group_totals.get(k, 0) for k in group_bottom)

                # 3. GIAO DIỆN CHÍNH
                c1, c2 = st.columns(2)
                
                # Định nghĩa đường kẻ dùng chung để đảm bảo độ cao bằng nhau
                shared_divider = "<div style='margin: 12px 0; border-top: 1px solid #b2bec3; width: 90%;'></div>"

                with c1:
                    st.markdown("##### 📝 Tổng Xác")
                    html_top, has_top = build_html_rows_only(group_top, group_totals, False)
                    if has_top:
                        # Sử dụng flex-start và margin-left để nhãn nằm gần chữ
                        st.markdown(f"""
                            <div style="display: flex; align-items: center; justify-content: flex-start;">
                                <div style="min-width: 170px;">{html_top}</div> <!-- tăng min-width để tránh nhãn bị đẩy xuống dòng -->
                                <div style="margin-left: 20px;">{get_subtotal_label_html("2S", total_2s)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Luôn hiển thị đường kẻ (hoặc ẩn nếu cả 2 bên không có dữ liệu)
                    st.markdown(shared_divider, unsafe_allow_html=True)

                    html_bot, has_bot = build_html_rows_only(group_bottom, group_totals, False)
                    if has_bot:
                        st.markdown(f"""
                            <div style="display: flex; align-items: center; justify-content: flex-start;">
                                <div style="min-width: 170px;">{html_bot}</div>
                                <div style="margin-left: 20px;">{get_subtotal_label_html("3S", total_3s)}</div>
                            </div>
                        """, unsafe_allow_html=True)

                with c2:
                    st.markdown("##### 💸 Qua Cò (x0.8)")
                    html_co_top, has_co_top = build_html_rows_only(group_top, group_totals, True)
                    if has_co_top:
                        st.markdown(f"<div>{html_co_top}</div>", unsafe_allow_html=True)
                    else:
                        # Tạo khoảng trống giả để giữ alignment nếu bên trái có mà bên phải không có
                        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

                    # Đường kẻ bên phải (ngang hàng với bên trái)
                    st.markdown(shared_divider, unsafe_allow_html=True)

                    html_co_bot, has_co_bot = build_html_rows_only(group_bottom, group_totals, True)
                    if has_co_bot:
                        st.markdown(f"<div>{html_co_bot}</div>", unsafe_allow_html=True)

                # --- TỔNG CỘNG CUỐI CÙNG ---
                total_quaco_all = sum(v * 0.8 for v in group_totals.values())
                st.divider()
                str_tong_cong = f"{total_quaco_all:,.0f}".replace(",", ".")
                st.markdown(f"""
                    <div style="background-color: #d1fae5; border: 2px solid #34d399; border-radius: 10px; padding: 15px; display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 20px; font-weight: bold; color: #065f46;">💰 TỔNG CỘNG (Qua Cò):</span>
                        <span style="font-size: 30px; font-weight: 900; color: #059669;">{str_tong_cong}đ</span>
                    </div>
                """, unsafe_allow_html=True)
