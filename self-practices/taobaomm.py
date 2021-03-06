from pyspider.libs.base_handler import *
 
PAGE_START = 1   # 列表开始页码
PAGE_END = 30    # 列表结束页码
DIR_PATH = 'D:/yh/YH2021/Python/taobaomm'   #资源保存路径
 
 
class Handler(BaseHandler):
    crawl_config = {
    }
 
    def __init__(self):
        self.base_url = 'https://mm.taobao.com/json/request_top_list.htm?page='
        self.page_num = PAGE_START
        self.total_num = PAGE_END
        self.deal = Deal()
 
    def on_start(self):
        while self.page_num <= self.total_num:
            url = self.base_url + str(self.page_num)
            self.crawl(url, callback=self.index_page, validate_cert=False)
            self.page_num += 1
 
    def index_page(self, response):
        for each in response.doc('.lady-name').items():
            self.crawl(each.attr.href, callback=self.detail_page, fetch_type='js',validate_cert=False)
 
    def detail_page(self, response):
        domain = response.doc('.mm-p-domain-info li > span').text()
        if domain:
            page_url = 'https:' + domain
            self.crawl(page_url, callback=self.domain_page, validate_cert=False)
 
    def domain_page(self, response):
        name = response.doc('.mm-p-model-info-left-top dd > a').text()
        dir_path = self.deal.mkDir(name)
        brief = response.doc('.mm-aixiu-content').text()
        if dir_path:
            imgs = response.doc('.mm-aixiu-content img').items()  #所有图片的集合
            count = 1
            self.deal.saveBrief(brief, dir_path, name)
            for img in imgs:
                url = img.attr.src
                if url:
                    extension = self.deal.getExtension(url)
                    file_name = name + str(count) + '.' + extension
                    count += 1
                    self.crawl(img.attr.src, callback=self.save_img,save={'dir_path': dir_path, 'file_name': file_name},validate_cert=False)
 
    def save_img(self, response):
        content = response.content
        dir_path = response.save['dir_path']
        file_name = response.save['file_name']
        file_path = dir_path + '/' + file_name
        self.deal.saveImg(content, file_path)
 
 
import os
 
class Deal:
    def __init__(self):
        self.path = DIR_PATH             #DIR_PATH: 资源保存路径
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if not os.path.exists(self.path):
            os.makedirs(self.path)
 
    def mkDir(self, path):               #创建 MM 名字对应的文件夹
        path = path.strip()
        dir_path = self.path + path
        exists = os.path.exists(dir_path)
        if not exists:
            os.makedirs(dir_path)
            return dir_path
        else:
            return dir_path
 
    def saveImg(self, content, path):     #传入图片二进制流以及保存路径，存储图片
        f = open(path, 'wb')
        f.write(content)
        f.close()
 
    def saveBrief(self, content, dir_path, name):     #在文档中保存 MM 的文字简介
        file_name = dir_path + "/" + name + ".txt"    #文档名字
        f = open(file_name, "w+")
        f.write(content.encode('utf-8'))
 
    def getExtension(self, url):          #通过图片 URL 获得链接的后缀名
        extension = url.split('.')[-1]
        return extension