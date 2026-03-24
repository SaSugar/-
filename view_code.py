import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

#指定列名获取数据,为True时返回20个均匀数据
def get_data(tit,scale_flag=False):
    n = 1
    new_s = pd.Series()   #创建一个空series数据结构用以存储后续的series数据
    while True:
        try:
            csv_df_data = pd.read_csv('data/第{}页_clear.csv'.format(n))
            s = csv_df_data[tit]
            new_s = pd.concat([new_s, s])  #向空Series数据结构添加series数据
            n += 1
        except FileNotFoundError:
            if scale_flag:
                s_max = new_s.max()
                s_min = new_s.min()
                ndarray = np.linspace(s_min,s_max,20) #根据获取到的数据，在该数据的最大值与最小值之间均匀取出20个值
                return pd.Series(ndarray)   #将ndarray转化为一个series
            else:
                return new_s

#保存图表
def save_fig(fname):
    plt.savefig(f'figure/{fname}')

#获取楼层字典
def get_floor_dic(floor_s):
    floor_dic = {}
    for f in floor_s:
        if f not in floor_dic:
            floor_dic[f] = 1
        else:
            floor_dic[f] = floor_dic[f] + 1
    return floor_dic

#格式化房型和楼层/面积的对应形式
def room_type_FA_format():
    room_type_s = get_data('房型')
    room_type_num = 1
    room_type_num_dic = {}
    room_type_lst = []
    #根据房型的原始顺序，从而获得房型序号列表
    for rt in room_type_s:
        if rt not in room_type_num_dic:
            room_type_num_dic[rt] = room_type_num
            room_type_lst.append(room_type_num)
            room_type_num += 1
        else:
            room_type_lst.append(room_type_num_dic[rt])

    return [room_type_lst,room_type_s]

#用于房型刻度值的设置
def set_room_type_scale(room_type_lst,room_type_s):
    dic = {}
    for num,rt in zip(room_type_lst,room_type_s):
        if num not in dic:
            dic[num] = rt
    return dic

#面积-价格散点图
def area_price_scatter():
    plt.figure(figsize=(15,8))
    area_s = get_data('面积')
    price_s = get_data('价格')
    x_scale = get_data('面积',True)
    y_scale = get_data('价格',True)
    plt.scatter(area_s,price_s)
    plt.xticks(x_scale,rotation=-45)
    plt.yticks(y_scale)
    plt.grid()
    plt.title('面积-价格散点图')
    plt.xlabel('面积(平方米)')
    plt.ylabel('价格(万)',rotation=0,labelpad=20) #labelpad参数调整轴标题与轴的间距
    plt.tight_layout()
    save_fig('面积_价格散点图')

#房型占比饼图
def room_type_pie():
    plt.figure(figsize=(15,8))
    room_type_s = get_data('房型')
    room_type_dic = {}
    for rt in room_type_s:
        if rt not in room_type_dic:
            room_type_dic[rt] = 1
        else:
            room_type_dic[rt] = room_type_dic[rt] + 1
    values = list(room_type_dic.values())
    percent_values = []
    for v in values:
        percent_values.append(float(f'{v / sum(values) * 100:.2f}'))
    #仅显示>=3%的数据的标签和添加explode
    labels = []
    explode = []
    values_pie = []
    values_total = 0
    index_num = 0
    for i,j in zip(percent_values,values):
        if i >= 3:
            labels.append(list(room_type_dic.keys())[index_num])     #获取房型标签
            explode.append(0.05)
            values_pie.append(j)
        else:
            values_total += j
        index_num += 1
    values_pie.append(values_total)
    labels.append('其它')
    explode.append(0)
    #仅显示>=3%的数据的百分比
    def display_per(per):
            return f'{per:.2f}%'
    plt.pie(values_pie,labels=labels,autopct=display_per,explode=explode)    #pie()方法会自动将饼图中每个扇形所占百分比作为值传入autopct中
    plt.legend()
    plt.title('房型占比饼图')
    plt.xlabel('房型(室厅卫)')
    plt.tight_layout()
    save_fig('房型占比饼图')

#楼层分布直方图
def floor_bar():
    plt.figure(figsize=(15,8))
    floor_s = get_data('楼层')
    floor_dic = get_floor_dic(floor_s)
    x = list(floor_dic.keys())
    y = list(floor_dic.values())
    plt.bar(x,y)
    plt.title('楼层分布直方图')
    plt.xticks(x)
    for i,ii in zip(x,y):
        plt.text(i,ii,ii,va='bottom',ha='center')
    plt.xlabel('楼层(层)')
    plt.ylabel('房源数量(个)',rotation=0,labelpad=30)
    plt.tight_layout()
    save_fig('楼层分布直方图')

#房源分布与交通便利性关系的水平直方图
def transportation_convenience_barh():
    plt.figure(figsize=(15,8))
    #对数据进行分类
    def classification(n,dic):
        if n == 0:
            dic['0'] = dic['0'] + 1
        elif n >= 1 and n <= 2:
            dic['1~2'] = dic['1~2'] + 1
        elif n >= 3 and n <= 4:
            dic['3~4'] = dic['3~4'] + 1
        else:
            dic['>5'] = dic['>5'] + 1
    bus_convenience_s = get_data('公交站距离')
    metro_convenience_s = get_data('地铁站距离')
    house_tra_conv_dic = {}
    n = 1
    for b,m in zip(bus_convenience_s,metro_convenience_s):
        house_tra_conv_dic[n] = {'公交站':len(eval(b)),'地铁站':len(eval(m))}
        n += 1
    # y刻度
    y_bus_dic = {
        '0':0,
        '1~2':0,
        '3~4':0,
        '>5':0
    }
    y_metro_dic = {
        '0': 0,
        '1~2': 0,
        '3~4': 0,
        '>5': 0
    }
    for ht in house_tra_conv_dic:
        bus_num = house_tra_conv_dic[ht]['公交站']
        metro_num = house_tra_conv_dic[ht]['地铁站']
        classification(bus_num,y_bus_dic)
        classification(metro_num,y_metro_dic)
    height = 0.2
    y = np.array([1,2,3,4])
    #公交站个数水平柱形
    plt.barh(y,list(y_bus_dic.values()),height=height,label='公交站')
    #地铁站个数水平柱形
    plt.barh(y + height,list(y_metro_dic.values()),height=height,label='地铁站')
    plt.legend()
    for i in y:
        plt.text(list(y_bus_dic.values())[i - 1],i,str(list(y_bus_dic.values())[i - 1]),va='center',ha='left')
        plt.text(list(y_metro_dic.values())[i - 1],i + height,str(list(y_metro_dic.values())[i - 1]), va='center', ha='left')
    plt.yticks(y+height/2,labels=list(y_metro_dic.keys()))
    plt.title('房源分布与交通便利性关系的水平直方图')
    plt.xlabel('房源数量(个)')
    plt.ylabel('站台数量区间(个)',rotation=0,labelpad=20)
    plt.tight_layout()
    save_fig('房源分布与交通便利性关系的水平直方图')

#房型+楼层与价格关系的散点图
def room_type_floor_price_scatter():
    plt.figure(figsize=(15,8))
    floor_s = get_data('楼层')
    price_s = get_data('价格')
    x_scale = list(get_floor_dic(floor_s).keys())
    room_type_format = room_type_FA_format()
    room_type_scale_dic = set_room_type_scale(room_type_format[0],room_type_format[1])
    plt.scatter(floor_s,room_type_format[0],c=price_s,cmap='YlOrRd',linewidths=0.5,edgecolors='black')
    plt.yticks(list(room_type_scale_dic.keys()),labels=list(room_type_scale_dic.values()))
    plt.xticks(x_scale,rotation=-30)
    plt.grid()
    plt.title('房型+楼层与价格关系的散点图')
    plt.xlabel('楼层(层)',labelpad=10)
    plt.ylabel('房型(室厅卫)',rotation=0,labelpad=30)
    #添加颜色条
    cbar = plt.colorbar()
    cbar.set_label('价格(万)',rotation=0,labelpad=25)
    plt.tight_layout()
    save_fig('房型+楼层与价格关系的散点图')

#房型+面积与价格关系的散点图
def room_type_area_scatter():
    plt.figure(figsize=(15,8))
    area_s = get_data('面积')
    area_y = get_data('面积',True)
    price_s = get_data('价格')
    room_type_format = room_type_FA_format()
    room_type_scale_dic = set_room_type_scale(room_type_format[0], room_type_format[1])
    plt.scatter(room_type_format[0],area_s,c=price_s,cmap='YlOrRd',linewidths=0.5,edgecolors='black')
    plt.xticks(list(room_type_scale_dic.keys()),labels=list(room_type_scale_dic.values()),rotation=-45)
    plt.yticks(area_y)
    plt.title('房型+面积与价格关系的散点图')
    plt.xlabel('房型(室厅卫)',labelpad=10)
    plt.ylabel('面积(平方米)',rotation=0,labelpad=35)
    plt.grid()
    cbar = plt.colorbar()
    cbar.set_label('价格(万)', rotation=0, labelpad=25)
    plt.tight_layout()
    save_fig('房型+面积与价格关系的散点图')

if __name__ == '__main__':
    plt.rcParams['font.sans-serif'] = ['SimHei']

    #绘图
    area_price_scatter()
    room_type_pie()
    floor_bar()
    transportation_convenience_barh()
    room_type_floor_price_scatter()
    room_type_area_scatter()
    #展示图表
    plt.show()


