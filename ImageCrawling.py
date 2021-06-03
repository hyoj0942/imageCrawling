from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.parse import quote_plus
import dload
import os
from selenium import webdriver
import time

class ImgCrawling:
    def __init__(self, plusUrl, directory):
        self._plusUrl = plusUrl
        self.mainUrl = [
                        f'https://search.daum.net/search?w=img&nil_search=btn&DA=NTB&enc=utf8&q={quote_plus(self._plusUrl)}',
                        f'https://www.google.com/search?q={quote_plus(self._plusUrl)}&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjgwPKzqtXuAhWW62EKHRjtBvcQ_AUoAXoECBEQAw&biw=768&bih=712',
                        f'https://search.naver.com/search.naver?where=image&sm=tab_jum&query={quote_plus(self._plusUrl)}'
                        ]
        self.imgNums = int(input('다음, 구글, 네이버에서 다운받을 이미지 수를 입력하시오 (*3): '))
        self._directory = directory

    def __str__(self):
        return "{} - 검색할 URL: \n다음: {}\n구글: {}\n네이버: {}\n\n이미지 다운로드 수: {}\n".format(self._plusUrl ,self.mainUrl[0], self.mainUrl[1], self.mainUrl[2], self.imgNums * 3)

    def createFolder(self):
        """
        다운받을 이미지가 저장될 폴더를 생성하는 함수(createFolder)
        > 지정된 directory에 plusUrl변수명을 참고하여 폴더생성
        > 이미 동일명의 폴더가 있다면 pass
        """
        try:
            if not os.path.exists(self._directory):
                os.makedirs(self._directory)
                print('폴더가 생성되었습니다!\n폴더명: '+ self._directory)
            else:
                print('폴더가 존재합니다.\n기존 폴더에 이미지를 추가로 내려받습니다.')
        except OSError:
            print('에러: 이미 생성되었습니다.' + self._directory)

    def webOpen(self):
        """
        크롬 드라이버 오픈 함수(webOpen)
        > 크롬드라이버 실행
        > 탭 2개를 추가로 실행
        > 각 탭에 mainUrl에 맞는 포털사이트를 입력 후 접속
        """
        global soups, tabs, driver

        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome('chromedriver')

        driver.execute_script('window.open("about:blank", "_blank");');
        driver.execute_script('window.open("about:blank", "_blank");');

        tabs = driver.window_handles

        soups = []

        for i in range(0, 3):           #html 코드 긁어모으기
            driver.switch_to_window(tabs[i])
            driver.get(self.mainUrl[i])
            time.sleep(2)
            req = driver.page_source
            time.sleep(2)
            soups.append(bs(req, 'html.parser'))



    def downloadImage(self):
        """
        이미지 다운로드 함수(downloadImage)
        > 각 포털에서 html언어를 정제
        > 정제한 언어로 createFolder함수로 제작한 폴더에 img파일을 추출하여 다운로드
        > plusUrl로 입력받은 이름명에 count하여 imgNums로 입력받은 개수만큼 저장
        """
        # 다음 시작
        driver.switch_to_window(tabs[0])
        daum_img = soups[0].select("#imgList > div > a > img")
        time.sleep(1)

        count = 1

        for thumbnail in daum_img:
            src = thumbnail["src"]    # 가져온 태그 정보중에 src만 가져옴
            dload.save(src, f'data/[{self._plusUrl}]images/{self._plusUrl}_{count}.jpg')    # 설정한 경로로 jpg파일로 다운로드
            print('다운로드중 ... {}'.format(count))

            count += 1
            if count == self.imgNums + 1:     #이미지 개수 지정
                break
        time.sleep(1)
        # 구글 시작
        driver.switch_to_window(tabs[1])
        google_img = soups[1].select("img.rg_i")

        time.sleep(1)
        imgurl = []

        for i in google_img:
            try:
                imgurl.append(i.attrs["src"])
            except KeyError:
                imgurl.append(i.attrs["data-src"])

        for i in imgurl:    # 해당 페이지의 이미지들의 태그들을 모두 가져옴
            urlretrieve(i, f'data/[{self._plusUrl}]images/{self._plusUrl}_{count}.jpg')    # 설정한 경로로 jpg파일로 다운로드
            print('다운로드중 ... {}'.format(count))
            count += 1
            if count == (self.imgNums * 2) + 1:
                break
        time.sleep(1)

        # 네이버 시작
        driver.switch_to_window(tabs[2])
        naver_img = soups[2].select("img._image")
        time.sleep(1)
        imgurl_2 = []

        for i in naver_img:
            try:
                imgurl_2.append(i.attrs["src"])
            except KeyError:
                imgurl_2.append(i.attrs["data-src"])

        for i in imgurl_2:    # 해당 페이지의 이미지들의 태그들을 모두 가져옴
            urlretrieve(i, f'data/[{self._plusUrl}]images/{self._plusUrl}_{count}.jpg')    # 설정한 경로로 jpg파일로 다운로드
            print('다운로드중 ... {}'.format(count))
            count += 1
            if count == (self.imgNums * 3) + 1:
                break

        print('다운로드 종료\n다운로드 성공: {}\n 5초뒤 종료됩니다.'.format(count - 1))

        time.sleep(5)
        driver.quit()

plusUrl = input("다운받을 이미지의 검색어를 입력하시오: ")

img = ImgCrawling(plusUrl, 'data/' + f'[{plusUrl}]images')

print(img)

img.createFolder()
img.webOpen()
img.downloadImage()
