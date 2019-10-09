from googletrans import Translator
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import datetime
import xlsxwriter
import os
import pickle


class Arxiv():
    def __init__(self):
        self.base_url = 'https://arxiv.org/search/?searchtype=all&query=Computation+and+Language&abstracts=show&' \
                        'size=200&order=-announced_date_first'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/76.0.3809.132 Safari/537.36'}

        self.record = self.load_record()

    def translate(self,text):
        translator = Translator(service_urls=['translate.google.cn'])
        result = translator.translate(text,dest='zh-CN').text
        return result

    def paper(self):
        html = requests.get(self.base_url,headers = self.headers)
        html.encoding = 'utf8'
        html = html.text
        bsj = BeautifulSoup(html,'lxml')
        lis = bsj.find_all('li',{'class':'arxiv-result'})
        result = []
        for li in tqdm(lis):
            res = {}
            p = li.find('p',{'class':'list-title is-inline-block'})
            pdf_href = p.find('span').find('a')
            if pdf_href:
                href = pdf_href['href']
            else:
                href = 'not found'
            title = li.find('p',{'class':'title is-5 mathjax'}).text
            title = title.replace('\n','').strip()
            cn_title = self.translate(title)
            authors = li.find('p',{'class':'authors'}).text
            authors = authors.replace('\n','').replace('  ','').strip()
            abstract = li.find('span',{'class':'abstract-full has-text-grey-dark mathjax'}).text
            abstract = abstract.replace('\n','').replace('  ','').strip()

            res['title'] = title
            res['cn_title'] = cn_title
            res['authors'] = authors
            res['abstract'] = abstract
            res['href'] = href
            if title not in self.record:
                self.record.append(title)
                result.append(res)
        self.save_record()
        return result

    def load_record(self):
        file_name = 'record.pkl'
        if not os.path.exists(file_name):
            return []
        else:
            with open(file_name,'rb') as f:
                paper_record = pickle.load(f)
            return paper_record

    def save_record(self):
        file_name = 'record.pkl'
        with open(file_name,'wb') as f:
            pickle.dump(self.record,f)

    def save_to_xlsx(self,data):
        date = datetime.datetime.now().strftime("%Y_%m_%d")
        save_name = 'paper_%s.xlsx'%date
        workbook = xlsxwriter.Workbook(save_name)
        worksheet = workbook.add_worksheet('papers')
        worksheet.write(0,0,'title')
        worksheet.write(0,1,'chinese title')
        worksheet.write(0,2,'url')
        worksheet.write(0,3,'authors')
        worksheet.write(0,4,'abstract')

        length = len(data)
        for i in range(length):
            worksheet.write(i+1,0,data[i]['title'])
            worksheet.write(i+1,1,data[i]['cn_title'])
            worksheet.write(i+1,2,data[i]['href'])
            worksheet.write(i+1,3,data[i]['authors'])
            worksheet.write(i+1,4,data[i]['abstract'])
        workbook.close()

    def process(self):
        data = self.paper()
        self.save_to_xlsx(data)


if __name__ == '__main__':
    arxiv = Arxiv()
    arxiv.process()


