# config/constants.py

from dataclasses import dataclass
from typing import List, Dict


LOAI_CUOC = {
    'dd': {'ten': 'Đầu đuôi', 'chu_so': 2},
    'dau': {'ten': 'Đầu', 'chu_so': 2},
    'duoi': {'ten': 'Đuôi', 'chu_so': 2},
    'da': {'ten': 'Đá', 'chu_so': 2},
    'dax': {'ten': 'Đá Xiên', 'chu_so': 2},
    'daxien': {'ten': 'Đá Xiên', 'chu_so': 2},
    'bao': {'ten': 'Bao', 'chu_so': [2,3,4]},
    'xc': {'ten': 'Xỉu chủ', 'chu_so': 3},
    'xcdau': {'ten': 'Xỉu chủ đầu', 'chu_so': 3},
    'xcduoi': {'ten': 'Xỉu chủ đuôi', 'chu_so': 3},
    'xcdao': {'ten': 'Xỉu đảo', 'chu_so': 3},
    'bd': {'ten': 'Bao đảo', 'chu_so': [3,4]},
    'bdao': {'ten': 'Bao đảo', 'chu_so': [3,4]},
}

DAI_XO_SO = {
    # XSMN
    "Tp.Hcm": {"TP", "tp", "tphcm"}, 
    "Đồng Tháp": {"ĐT", "dt", "dongthap", "dong thap"}, 
    "Cà Mau": {"CM", "cm", "ca mau"},
    "Bến Tre": {"BT", "bt", "bentre", "ben tre"}, 
    "Vũng Tàu": {"VT", "vt", "vungtau", "vung tau"}, 
    "Bạc Liêu": {"BL", "bl", "baclieu", "bac lieu"},
    "Đồng Nai": {"ĐN", "dn", "dongnai", "dong nai"}, 
    "Cần Thơ": {"CT", "ct", "cantho", "can tho"}, 
    "Sóc Trăng": {"ST", "st", "soctrang", "soc trang"},  
    "Tây Ninh": {"TN", "tn", "tayninh", "tay ninh"}, 
    "An Giang": {"AG", "ag", "angiang", "an giang"}, 
    "Bình Thuận": {"BTh", "bth", "binhthuan", "binh thuan"},
    "Vĩnh Long": {"VL", "vl", "vinhlong", "vinh long"}, 
    "Bình Dương": {"BD", "bd", "binhduong", "binh duong"}, 
    "Long An": {"LA", "la", "longan", "long an"}, 
    "Trà Vinh": {"TV", "tv", "travinh", "tra vinh"},
    "Bình Phước": {"BP", "bp", "binhphuoc", "binh phuoc"}, 
    "Hậu Giang": {"HG", "hg", "haugiang", "hau giang"}, 
    "Tiền Giang": {"TG", "tg", "tiengiang", "tien giang"}, 
    "Kiên Giang": {"KG", "kg", "kiengiang", "kien giang"},
    "Đà Lạt": {"DL", "dlat", "dalat", "da lat", "đà lạt"},
    
    #    # XSMT
    "phú yên": {"PY", "py","phuyen", "phu yen"},
    "thừa thiên huế": {"TTH", "tth", "thuatienhue", "thua tien hue"},
    "đắk lắk": {"DLK", "dlk", "daklak", "dak lak"},
    "quảng nam": {"QN", "qn", "quangnam", "quang nam"},
    "đà nẵng": {"DNang", "dnang", "da nang", "danang"},
    "khánh hòa": {"KH", "kh", "khanhhoa", "khanh hoa"},
    "quảng bình": {"QB", "qb", "quangbinh", "quang binh"},
    "bình định": {"BĐ", "bđ", "binhdinh", "binh dinh"},
    "quảng trị": {"QT", "qt", "quangtri", "quang tri"},
    "gia lai": {"GL", "gl", "gialai", "gia lai"},
    "ninh thuận": {"NT", "nt", "ninhthuan", "ninh thuan"},
    "quảng ngãi": {"QNg", "qng", "quangngai", "quang ngai"},
    "đắk nông": {"DNong", "dnong", "daknong", "dak nong"},
    "kon tum": {"KT", "kt", "kontum", "kon tum"},

    # Đài gộp
    "2 Đài MN": {"2dmn" },
    "2 Đài MT": {"2dmt" },
    "3 Đài MN": {"3dmn"},
    "3 Đài MT": {"3dmt"},
    
    # XSMB
    "Miền Bắc": {"MB", "mb"},
}

TIEN_TE = {
    'n': 1000, 'ng': 1000, 'ngan': 1000,
    'k': 1000, 
    'd': 1, 'đ': 1, 'vnd': 1,
    'tr': 1000000, 'trieu': 1000000
}

# Quy tắc sửa lỗi & mapping từ viết tắt
AUTO_FIX_RULES = {
    # Loại cược viết tắt
    'xd': 'xcdao', 'xc dao': 'xcdao', 'xdao': 'xcdao',
    'xđ': 'xcdao', 'xc đ': 'xcdao',
    'x': 'xc', 'xe': 'xc',
    'xcd': 'xcdao', 'xc d': 'xcdao',
    'xcdui': 'xcduoi', 'xc dui': 'xcduoi',
    'b': 'bao',
    'bl': 'bao',
    'blo': 'bao',
    'bđao': 'bdao',
    'bđ': 'bdao',
    'ddau': 'dd', 'đđ': 'dd', 'dđ': 'dd',
    'daa': 'da', 'đa': 'da', "đã": 'da', 'đá': 'da',
    'đau': 'dau', 'dui': 'duoi',
     
    
    # Sửa lỗi chính tả đài phổ biến
    'tp hcm': 'tp',
}



# --- CẤU HÌNH NHÓM HIỂN THỊ VÀ TỶ LỆ ---
# ty_le_an: 1 ăn bao nhiêu
# ti_le_xac: Hệ số nhân tiền xác (Ví dụ: 0.8 là 100k chỉ tính 80k)
# Đối với Khách

CAU_HINH_NHOM_CUOC = {
    '2CB': {
        'ten': '2 Con Bao',
        'match_types': ['bao', 'blo', 'b', 'bl'], 
        'match_len': 2,
        'ty_le_an': 80,    # Ví dụ: 1 ăn 80k
        'ti_le_xac': 0.8  # Ví dụ: Cò 20% (nhân 0.8)
    },
    '3CB': {
        'ten': '3 Con Bao',
        'match_types': ['bao', 'blo', 'b', 'bl'],
        'match_len': 3,
        'ty_le_an': 80,
        'ti_le_xac': 0.8
    },
    '4CB': {
        'ten': '4 Con Bao',
        'match_types': ['bao', 'blo', 'b', 'bl'],
        'match_len': 4,
        'ty_le_an': 80,
        'ti_le_xac': 0.8
    },
    'ĐáT': {
        'ten': 'Đá Thẳng',
        'match_types': ['da', 'daa'],
        'match_len': 2,
        'ty_le_an': 80,
        'ti_le_xac': 0.8
    },
    'ĐáX': {
        'ten': 'Đá Xiên 1 Đài',
        'match_types': ['dax', 'daxien'],
        'match_len': 2,
        'ty_le_an': 80,
        'ti_le_xac': 0.8
    },
    '3CXC': {
        'ten': '3 Con Xỉu Chủ',
        'match_types': ['xc', 'xcduoi', 'xcdau', 'x', 'xe'],
        'match_len': 3,
        'ty_le_an': 80,
        'ti_le_xac': 0.8
    },
    '3CXĐ': {
        'ten': '3 Con Xỉu Đảo',
        'match_types': ['xcdao', 'xd', 'xcd', 'xc dao'],
        'match_len': 3,
        'ty_le_an': 80,   
        'ti_le_xac': 0.8
    },
    '3CBĐ': {
        'ten': '3 Con Bao Đảo',
        'match_types': ['bd', 'bdao', 'bđ'],
        'match_len': 3,
        'ty_le_an': 80,
        'ti_le_xac': 0.8
    },
    '4CBĐ': {
        'ten': '4 Con Bao Đảo',
        'match_types': ['bd', 'bdao', 'bđ'],
        'match_len': 4,
        'ty_le_an': 80,
        'ti_le_xac': 0.8
    },
    
}