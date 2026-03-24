import csv
import os

#数据清洗
def clear_data(page_num):
    c_data = []
    n = 0
    #若找不到文件，就说明处理完了所有文件，即可退出数据清洗阶段
    try:
        file_name = 'data/第{}页.csv'.format(page_num)
        with open(file_name, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                n += 1
                #处理掉不属于安居客的数据
                if '㎡' not in row[0]:
                    if row == ["楼层", "房型", "面积", "房源地址及名称", "价格", "公交站距离", "地铁站距离"]:
                        pass
                    else:
                        try:
                            #仅获取楼层数量
                            row[0] = int(row[0].split('共')[1].split('层')[0])
                            #室厅卫数据仅保留数字
                            num = ''
                            for i in str(row[1]):
                                if i.isdigit(): #str.isdigit过滤非数字字符
                                    num += i
                                else:
                                    num += '.'
                            row[1] = num[:-1]
                            #去除掉面积的单位
                            row[2] = float(row[2][:-1])
                            #去除价格的单位
                            row[4] = float(row[4][:-1])
                            if row[4] >= 10000: #排除极端数据
                                continue
                            #清洗公交、地铁站的距离，将出现的重复数据去除
                            #公交站距离
                            bus_lst = eval(row[5])   #eval()将列表字符串转化为列表
                            bus_set = set(bus_lst)   #将列表转化为集合，集合会自动去除数据中的重复数据
                            row[5] = bus_set
                            #地铁站距离
                            metro_lst = eval(row[6])
                            metro_set = set(metro_lst)
                            row[6] = metro_set
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                    c_data.append(row)
    except FileNotFoundError:
        return False
    if n == 1:
        os.remove(file_name)
    else:
        with open(file_name, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(c_data)
        os.rename(file_name, 'data/第{}页_clear.csv'.format(page_num))
    return True

if __name__ == '__main__':
    page_num = 1
    while True:
        flag = clear_data(page_num)
        if flag:
            page_num += 1
        else:
            print('-----所有数据清洗完毕-----')
            break
