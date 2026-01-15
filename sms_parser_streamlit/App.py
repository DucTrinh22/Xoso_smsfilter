# App.py
from datetime import datetime
import requests
import streamlit as st
from core.bet_checker import BetChecker
from core.comparator import SMSComparator
from core.lottery_fetcher import MinhNgocFetcher
from core.parser import SMSParser
from components.input_form import render_input_form
from components.result_display import render_results
import streamlit.components.v1 as components
from bs4 import BeautifulSoup

# Config trang
st.set_page_config(page_title="SMS Cược XS", layout="wide")
st.title("📟 Hệ thống Phân Tích SMS")

# 1. KHUNG CẤU HÌNH NGÀY (Expander)
with st.expander("📆 Lịch Xổ Số", expanded=False):
    c_config_1, c_config_2 = st.columns(2)
    with c_config_1:
        # Chọn ngày
        selected_date = st.date_input("Chọn ngày xổ số", datetime.now())
        date_str_for_api = selected_date.strftime("%d-%m-%Y")
    
    with c_config_2:
        # Chọn Miền
        khu_vuc = st.selectbox(
            "Chọn Miền",
            options=["Miền Nam", "Miền Trung", "Miền Bắc"],
            index=1 # Để mặc định Miền Trung cho bạn test
        )

# Khởi tạo class logic
comparator = SMSComparator()
parser = SMSParser()
fetcher = MinhNgocFetcher()

# --- 2. HIỂN THỊ BẢNG KẾT QUẢ (LOGIC MỚI: CẮT HTML) ---
st.caption(f"Đang hiển thị kết quả: **{khu_vuc}** - Ngày: **{date_str_for_api}**")

# Mapping slug sang link Kết quả chính thức (Ổn định hơn link In vé dò)
slug_map = {
    "Miền Nam": "mien-nam",
    "Miền Trung": "mien-trung",
    "Miền Bắc": "mien-bac"
}
slug = slug_map.get(khu_vuc, "mien-nam")

# URL chính thức: minhngoc.net.vn/ket-qua-xo-so/{vùng}/{ngày}.html
url_embed = f"https://www.minhngoc.net.vn/ket-qua-xo-so/{slug}/{date_str_for_api}.html"

try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url_embed, headers=headers, timeout=15)
    
    if response.status_code == 200:
        response.encoding = 'utf-8'
        
        # Dùng BeautifulSoup để cắt bỏ phần đầu trang/quảng cáo thừa
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm div chứa bảng kết quả (thường class là 'box_kqxs' hoặc 'content')
        content_div = soup.find('div', class_='box_kqxs')
        
        if content_div:
            # Lấy HTML của bảng
            clean_html = str(content_div)
            
            # Thêm CSS tùy chỉnh để bảng đẹp hơn khi nhúng
            custom_css = """
            <style>
                body { font-family: Arial, sans-serif; background-color: #ffffff; }
                .box_kqxs { width: 100% !important; border: none !important; }
                .title_kqxs { background-color: #020e91; color: white; padding: 5px; text-align: center; font-weight: bold; }
                table { width: 100%; border-collapse: collapse; }
                td, th { border: 1px solid #ddd; padding: 6px; text-align: center; }
                /* Ẩn bớt các nút in/chia sẻ thừa */
                .opt_date, .buttons-wrapper { display: none !important; }
            </style>
            """
            
            # Gắn Base URL để load được ảnh từ Minh Ngọc
            final_html = f'<base href="https://www.minhngoc.net.vn/" target="_blank">{custom_css}{clean_html}'
            
            components.html(final_html, height=600, scrolling=True)
        else:
            # Fallback: Nếu không cắt được thì hiển thị cả trang (với base tag)
            st.warning("Không thể trích xuất bảng, hiển thị toàn bộ trang...")
            fixed_html = f'<base href="https://www.minhngoc.net.vn/" target="_blank">{response.text}'
            components.html(fixed_html, height=600, scrolling=True)
            
    else:
        st.error(f"Minh Ngọc báo lỗi (404/500) cho ngày {date_str_for_api}. Có thể chưa có kết quả.")

except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")

st.markdown("---")

# --- PHẦN NHẬP LIỆU ---
lines = render_input_form()

col1, col2 = st.columns([1, 5])
with col1:
    btn_analyze = st.button("Phân tích sms", type="primary")

def clear_input_callback():
    if "input_sms_area" in st.session_state:
        st.session_state["input_sms_area"] = ""

with col2:
    st.button("Xoá nhập liệu", on_click=clear_input_callback)

# --- XỬ LÝ PHÂN TÍCH (LOGIC MỚI) ---
if "results" not in st.session_state:
    st.session_state.results = []

if btn_analyze:
    if not lines:
        st.warning("Vui lòng nhập tin nhắn!")
    else:
        st.session_state.results = []
        
        # BƯỚC 1: PHÂN TÍCH CÚ PHÁP (Luôn chạy dù có mạng hay không)
        temp_results = []
        for line in lines:
            # 1. So sánh/Parse
            kq_ss = comparator.compare(line)
            
            # 2. Lấy object parse để chuẩn bị dò
            kq_parse = None
            if kq_ss.hop_le:
                # Parse lại để lấy cấu trúc object cho việc dò vé
                # (Comparator trả về string, ta cần object Cuoc)
                kq_parse = parser.parse(kq_ss.tin_nhan_sau_sua)

            temp_results.append({
                "ss": kq_ss,
                "parse": kq_parse,
                "check_results": [] # Mặc định chưa có kết quả dò
            })

        # Lưu kết quả phân tích vào session ngay lập tức
        st.session_state.results = temp_results

        # BƯỚC 2: TẢI KẾT QUẢ VÀ DÒ (Chạy sau)
        kqxs_data = {}
        try:
            with st.spinner(f"Đang tải dữ liệu xổ số để dò..."):
                kqxs_data = fetcher.fetch_data(date_str_for_api)
        except Exception as e:
            st.error(f"Lỗi kết nối: {e}")

        # BƯỚC 3: CẬP NHẬT KẾT QUẢ DÒ (Nếu có dữ liệu)
        if kqxs_data:
            checker = BetChecker(kqxs_data)
            
            # Duyệt lại danh sách đã phân tích để dò
            for res in st.session_state.results:
                parsed_obj = res["parse"]
                if parsed_obj and parsed_obj.hop_le:
                    # Dò từng cược trong tin nhắn
                    line_check_results = []
                    for cuoc in parsed_obj.danh_sach_cuoc:
                        ket_qua_check = checker.check_cuoc(cuoc)
                        line_check_results.append(ket_qua_check)
                    
                    # Cập nhật vào kết quả
                    res["check_results"] = line_check_results

# --- 4. HIỂN THỊ KẾT QUẢ ---
if st.session_state.results:
    # Truyền thêm cờ báo hiệu có dữ liệu xổ số hay không
    has_lottery_data = any(r.get("check_results") for r in st.session_state.results)
    render_results(st.session_state.results, has_data=has_lottery_data)
    
    st.markdown("---")
    if st.button("🗑️ Xóa kết quả"):
        st.session_state.results = []
        st.rerun()
