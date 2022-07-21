import pyodbc

#print(pyodbc.drivers())
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-9PUB3KF\SQLEXPRESS;'
                      'Database=S2T;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()
# cursor.execute('SELECT TOP (10) [MaKHQS],[TenKH] FROM DM_KHQS ')

# for i in cursor:
#     print(i.MaKHQS)

text = "tuyến bắn của c tăng nằm trên quốc lộ 31, tại điểm cao 175"

def search_object(text = ""):

    icon_list_result = []
    location_list_result = []

    #tìm kiếm icon
    icon_list = cursor.execute('SELECT TOP (10) [MaKHQS],[TuKhoa] FROM DM_KHQS ')

    for icon in icon_list:
        keyword_list = icon.TuKhoa.split(',')
        for c in keyword_list:
            keyword = c.strip().lower()
            if(keyword in text):
                icon_list_result.append(icon.MaKHQS)
        

    #tìm kiếm địa danh
    location_list = cursor.execute('SELECT TOP (10) [TuKhoa],[DanhSachToaDo] FROM DanhMucDiaDiem ')

    for location in location_list:
            keyword_list = location.TuKhoa.split(',')
            for c in keyword_list:
                keyword = c.strip().lower()
                if(keyword in text):
                    location_list_result.append(location.DanhSachToaDo)

    return icon_list_result, location_list_result

icon_list, location_list = search_object(text)
print(text)
print("icon_ids: ", icon_list)
print("location_list: ", location_list)
