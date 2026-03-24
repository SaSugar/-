from DrissionPage import ChromiumPage,ChromiumOptions
from DrissionPage.errors import ElementNotFoundError
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager
import numpy as np
import time
import csv


#将数据写入csv文件中
def save_csv(d,page_num):
    with open('data/第{}页.csv'.format(page_num),'w',encoding='utf-8',newline='') as f:   #newline参数防止出现多余空行
        writer = csv.writer(f)
        writer.writerows(d)

#获取房源与各类建筑的距离
def get_name_distance(new_page):
    lst = []
    name = new_page.eles('@@tag()=span@@class=itemText itemTitle',timeout=5)  # 名称
    distance = new_page.eles('@@tag()=span@@class=itemText itemdistance',timeout=5)  # 距离
    for n,d in zip(name,distance):
        # 由于从源代码中获取的距离为“...米”的字符串类型数据，因此通过切片仅获得数字，从而转化为整数类型进行比较
        if int(d.text[:-1]) <= 1000:
            lst.append(n.text+' '+d.text)
    return lst

def get_inner_anjuke_data(page,n,d_list):
    #点击每个房源，获取房源页面的其它数据
    page.actions.click('xpath://*[@id="esfMain"]/section/section[3]/section[1]/section[2]/div[{}]/a/div[2]/div[1]/div[1]/h3'.format(n))
    new_page = page.latest_tab
    #跳过属于58同城的数据，判断当前页面的url是否含有"58.com"这样的字段
    flag = True
    if "58.com" in new_page.url:
        flag = False
    if flag:
        # 通过点击类型以获取对应数据，总共点击1次
        for i in range(2):
            try:
                # 仅获取房源距离<=1000米的公交站、地铁站
                distance_lst = get_name_distance(new_page)
                d_list.append(distance_lst)
                new_page.wait(np.random.uniform(3, 7))
                g = i + 2
                if g != 3:
                    new_page.actions.click('xpath://*[@id="smailMapContainer"]/div[3]/div[2]/ul/li[{}]'.format(g))
            except ElementNotFoundError:
                new_page.refresh()
                i -= 1
    new_page.close()

#获得房源地址及名称、房型、面积、楼层的函数
def get_data(page,page_num):
    rows_data = []
    # 自动打开目标网页
    url = 'https://chengdu.anjuke.com/sale/d23-p{}-t21-z1/?from=navigation'.format(page_num)
    page.get(url)
    #列标题
    titles = ['楼层','房型','面积','房源地址及名称','价格','公交站距离','地铁站距离']
    rows_data.append(titles)
    n = 1
    while True:
        d_list = []
        #楼层
        floors = page.ele('xpath:/html/body/div[1]/div/div/section/section[3]/section[1]/section[2]/div[{}]/a/div[2]/div[1]/section/div[1]/p[4]'.format(n),timeout=1)
        #房型
        type_chips = page.eles('xpath:/html/body/div[1]/div/div/section/section[3]/section[1]/section[2]/div[{}]/a/div[2]/div[1]/section/div[1]/p[1]/span'.format(n))
        chip = ''
        #跳过58同城网站的数据
        if type_chips and floors:
            for i in type_chips:
                chip += i.text
            d_list.append(floors.text)
            d_list.append(chip)
        #判断该页是否还有数据
        if not (floors or type_chips):
            break
        #面积
        area = page.ele('xpath:/html/body/div[1]/div/div/section/section[3]/section[1]/section[2]/div[{}]/a/div[2]/div[1]/section/div[1]/p[2]'.format(n))
        d_list.append(area.text)
        #房源地址及名称
        address_chips = page.eles('xpath:/html/body/div[1]/div/div/section/section[3]/section[1]/section[2]/div[{}]/a/div[2]/div[1]/section/div[2]/p[2]/span'.format(n))
        chip = ''
        for i in address_chips:
            chip += i.text
        name = page.ele('xpath:/html/body/div[1]/div/div/section/section[3]/section[1]/section[2]/div[{}]/a/div[2]/div[1]/section/div[2]/p[1]'.format(n))
        address_name = chip + ' ' + name.text
        d_list.append(address_name)
        #价格
        total_price_chips = page.eles('xpath://*[@id="esfMain"]/section/section[3]/section[1]/section[2]/div[{}]/a/div[2]/div[2]/p[1]/span'.format(n))
        chip = ''
        for i in total_price_chips:
            chip += i.text
        d_list.append(chip)
        #调用函数
        get_inner_anjuke_data(page,n,d_list)
        sleep_time = np.random.uniform(3,6)
        page.wait(sleep_time)  # 与time.sleep(1)作用一致
        rows_data.append(d_list)
        n += 1
    #将获取到的数据写入对应文件中
    save_csv(rows_data,page_num)
    print('---第{}页 爬取完成---'.format(page_num))

def task_or_close(co,page_num=None,result=None,q=False):
    # 创建浏览器对象
    page = ChromiumPage(co)
    if q == True:
        # 关闭浏览器
        page.quit()
    else:
        # 判断该页是否有数据，有就进行爬取，无就添加标记
        if not page.ele('@text()=没有找到相关房源，可'):
            get_data(page, page_num)
        else:
            result.append('no')



#配置自动化浏览器
def configure_browser(port):
    #配置对象
    return ChromiumOptions().set_local_port(port).set_user_data_path(r'C:\Users\cat12\Desktop\实训\2023级毕设-安居客爬虫与可视化分析\Chrome\Chrome{}'
                                                                     .format(str(port)[-1])).no_imgs(True) #no_imgs(True) 禁止加载图片

if __name__ == '__main__':
    #存储自动化浏览器的配置
    co_lst = []
    #为自动化浏览器分配端口号
    for po in [9111,9112,9113]:
        co = configure_browser(po)
        co_lst.append(co)
    #创建进程池
    with ProcessPoolExecutor(3) as p:
        page_num = 1
        result = Manager().list()
        while True:
            fs = [] #存储Future对象
            re_lst = [] #存储Future对象的返回值，即page对象
            for i in range(3):
                f = p.submit(task_or_close,co=co_lst[i],page_num=page_num,result=result) #submit()方法的返回值是Future对象
                time.sleep(2)
                fs.append(f)
                page_num += 1
            for f in fs:
                re = f.result()  #阻塞，等待任务完成
            if 'no' in result:
                for i in range(3):
                    task_or_close(co=co_lst[i],q=True)
                break
    print('*****全部爬取完成*****')
