from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage import WebPage
from concurrent.futures import ThreadPoolExecutor
from time import sleep, time
from DrissionPage import WebPage
import random
import os
import json
from DrissionPage.errors import *
import logging
from datetime import datetime



# 创建一个配置对象，并设置自动分配端口
co = ChromiumOptions()
co.set_argument('--headless')
co.set_argument('--no-sandbox')
co.auto_port()

# 使用配置对象创建一个 ChromiumPage 对象
page = WebPage(chromium_options=co)




# 获取脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 构建日志文件夹路径
log_folder = os.path.join(script_dir, "定时阅读LinuxDO_日志")

# 检查并创建日志文件夹
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# 创建日志文件名
current_date = datetime.now()
year_folder = os.path.join(log_folder, str(current_date.year))
month_folder = os.path.join(year_folder, current_date.strftime("%m"))

# 检查并创建年份和月份文件夹
if not os.path.exists(year_folder):
    os.makedirs(year_folder)
if not os.path.exists(month_folder):
    os.makedirs(month_folder)

log_file_name = current_date.strftime("%Y-%m-%d_%H-%M") + ".log"
log_file_path = os.path.join(month_folder, log_file_name)





# 配置日志记录
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 创建一个文件处理器并设置编码为 utf-8
file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 创建一个格式化器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 将文件处理器添加到日志记录器
logger.addHandler(file_handler)




# 创建一个自定义的日志记录函数
def log_and_print(message, level=logging.INFO):
    if level == logging.DEBUG:
        logger.debug(message)
    elif level == logging.INFO:
        logger.info(message)
    elif level == logging.WARNING:
        logger.warning(message)
    elif level == logging.ERROR:
        logger.error(message)
    elif level == logging.CRITICAL:
        logger.critical(message)
    print(message)





def login(page, username, password, initial_url):
    log_and_print("没有登录，开始登录")
    # 登录界面按钮
    page.ele('css:[class="panel" ]  span.d-button-label').click()

    # 定位邮箱元素，输入邮箱
    email_input_ele = page.ele('css:input#login-account-name')
    email_input_ele.input(username)

    # 定位密码，输入密码
    password_input_ele = page.ele('css:input[autocomplete="current-password"]')
    password_input_ele.input(password)

    # 点击登录按钮
    page.ele('css:#login-button > span').click()

    # 使用wait.load_start()等待页面加载完成
    page.wait.load_start()

    page.get(url=initial_url)

def exit_login(page):
    log_and_print("开始退出账号")
    # 点击头像
    page.ele('css:#toggle-current-user').click()

    # 打印账号名称
    log_and_print(page.ele('css:#toggle-current-user').attr("aria-label"))

    # 点击资料
    page.ele('css:#user-menu-button-profile > svg > use').click()

    # 点击退出
    page.ele('css: li.logout > button > span[class="item-label"]').click()

def find_navigate_links(page):
    eles = page.eles('css:a[href][class="title raw-link raw-topic-link"]')               
    links = eles.get.links()

    return len(links), links

def read_post(page, link, index):
    global post_count, numerator_list  # 声明全局变量
    page.get(url=link)
    while True:
        # 生成一个随机数用于滚动像素
        scroll_distance = random.randint(240, 300)
        page.scroll.down(scroll_distance)
        page.wait(1)
        
        # 获取页面的总帖子数，因为发现了无回复的帖子，显示是0，而不是1 / 1，所以可以使用ElementNotFoundError解决这个问题
        post_num = page.ele("css:.timeline-replies", timeout=5)
        try:
            post_num = post_num.text
            log_and_print(post_num)
        
            # 解析分子和分母
            parts = post_num.split(' / ')

            numerator = int(parts[0])
            denominator = int(parts[1])
            
            # 检查分子和分母是否相同
            if numerator == denominator:
                # 再滑动3次
                for _ in range(3):
                    page.scroll.down(scroll_distance)
                log_and_print(f"这是第 {index} 次循环跳转，将跳转到 {link}")
                # 增加帖子计数器
                post_count += numerator
                break
            else:
                # 这个部分就是为了出来网站没有反应过来刷新，更新帖子的阅读情况的
                if denominator < 5:
                    numerator_list.append(numerator)
                    if 1 == denominator - numerator and numerator_list.count(numerator) >= 7:  
                        # 检查列表中相同值的次数
                        log_and_print("已经阅读完了这个话题，但网站没有反应过来")
                        log_and_print(f"这是第 {index} 次循环跳转，将跳转到 {link}")
                        # 增加帖子计数器
                        post_count += numerator
                        break
                else:
                    numerator_list.append(numerator)
                    if 5 > denominator - numerator and numerator_list.count(numerator) >= 7:  
                        # 检查列表中相同值的次数
                        log_and_print("已经阅读完了这个话题，但网站没有反应过来")
                        log_and_print(f"这是第 {index} 次循环跳转，将跳转到 {link}")
                        # 增加帖子计数器
                        post_count += numerator
                        break
        except ElementNotFoundError:
            log_and_print("找不到元素")
            break

def main(data):
    global post_count, numerator_list  # 声明全局变量
    post_count = 0
    numerator_list = []

    # 将元组的第一个元素赋值给 username，第二个元素赋值给 password
    username, password = data
    # print(f"Username: {username}, Password: {password}")

        
    # print(username, password)




    page.set.window.max()

    # 设置滚动方式为非平滑滚动
    page.set.scroll.smooth(on_off=False)

    linuxdo_Tab = page.new_tab(new_context=True)  # 新建标签页，以无痕模式，他的无痕是不共享数据给其他窗口，而不是打开真正的无痕窗口
    # page.close()  如果不注释就不能实现循环，因为第一次循环结束浏览器就会关闭，不会再启动。

    # 打开目标网页
    linuxdo_Tab.get(url='https://linux.do/latest')
    print(linuxdo_Tab.address)
    print(linuxdo_Tab.url)

    # 检测是否需要登录
    if linuxdo_Tab.ele('css:[class="panel" ]  span.d-button-label', timeout=2) or linuxdo_Tab.ele('css:a[class="btn btn-primary btn-small login-button btn-icon-text"]', timeout=2):
        initial_url = linuxdo_Tab.url
        linuxdo_Tab.get(url="https://linux.do/latest")
        login(linuxdo_Tab, username, password, initial_url)

    # 记录滚动开始的时间
    start_time = time()

    while True:
        # 生成一个随机数用于滚动像素
        scroll_distance = random.randint(240, 300)
        linuxdo_Tab.scroll.down(scroll_distance)
        linuxdo_Tab.wait(1)

        # 获取文档的高度
        document_height = linuxdo_Tab.run_js('return document.documentElement.scrollHeight;')
        # 获取视口的高度
        viewport_height = linuxdo_Tab.run_js('return window.innerHeight;')
        # 获取当前滚动条的位置
        scroll_position = linuxdo_Tab.run_js('return window.scrollY || window.pageYOffset || document.body.scrollTop + (document.documentElement.scrollTop || 0);')

        # 计算差值
        difference = document_height - (scroll_position + viewport_height)

        # 记录滚动结束的时间
        end_time = time()
        elapsed_time = end_time - start_time

        # 判断是否滚动到底部或超过40秒
        if difference <= 5:
            log_and_print(f'文档的高度: {document_height}, 视口的高度: {viewport_height}, 当前滚动条的位置: {scroll_position}, 到达页面底部, 差值: {difference}')

            personal_link = find_navigate_links(linuxdo_Tab)
            log_and_print(f'找到的链接数量: {personal_link[0]}')
            log_and_print(f'链接列表: {personal_link[1]}')

            log_and_print(f'滑到底用了多长时间: {elapsed_time} 秒')

            # personal_link[1] 是一个包含链接的列表
            for i, link in enumerate(personal_link[1]):
                read_post(linuxdo_Tab, link, i)

            break
        elif elapsed_time > 2:
            log_and_print(f'文档的高度: {document_height}, 视口的高度: {viewport_height}, 当前滚动条的位置: {scroll_position}, 到达页面底部, 差值: {difference}')

            personal_link = find_navigate_links(linuxdo_Tab)
            log_and_print(f'找到的链接数量: {personal_link[0]}')
            log_and_print(f'链接列表: {personal_link[1]}')

            log_and_print(f'滑到底用了多长时间: {elapsed_time} 秒')

            # 假设 personal_link[1] 是一个包含链接的列表
            for i, link in enumerate(personal_link[1]):
                read_post(linuxdo_Tab, link, i)
            break
        else:
            log_and_print(f'文档的高度: {document_height}, 视口的高度: {viewport_height}, 当前滚动条的位置: {scroll_position}, 未到达底部, 差值: {difference}')

    # 打印统计结果
    log_and_print(f"总共阅读了 {post_count} 个帖子")

    try:
        personal_logo = linuxdo_Tab.ele("css:.#toggle-current-user", timeout=5)
        exit_login(linuxdo_Tab)
    except ElementNotFoundError:
        log_and_print("找不到元素")

    # 关闭页面
    linuxdo_Tab.close()

if __name__ == "__main__":
    file_path = "linuxdo_accounts.json"
    
    # 打开并读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    # # 将字典中的每个键值对转换为元组列表
    # data_lists = list(data.items())
    # for i in data_lists:
    #     main(i)


    # 将字典中的每个键值对转换为元组列表
    data_lists = list(data.items())
    with ThreadPoolExecutor(max_workers=7) as executor:
        executor.map(main, data_lists)

    # 关闭页面
    page.quit()
