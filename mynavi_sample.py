import os
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# Chromeを起動する関数



def set_driver(headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    #return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

#logの処理
def add_log(message):
    with open("log.txt", mode='a') as f:
        f.write(message+"\n")


# main処理
def main():
    search_keyword = input("キーワードを入力してください\n>>>")
    # driverを起動
    driver = set_driver(False)
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
 
    try:
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
        time.sleep(5)
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
    except:
        pass
    
    # 検索窓に入力
    driver.find_element_by_class_name("topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

    #現在のURLを取得
    time.sleep(5)
    current_url = driver.current_url
    current_url = current_url.split("?")
    url_before = current_url[0]
    url_after ="?"+current_url[1]

    name =['会社名','サブコピー','メインコピー','仕事内容','対象となる方','勤務地','給与','初年度年収']
    df = pd.DataFrame(columns=name)

    #求人のIDのカウント
    count = 0

    #求人の件数
    num_jobs = int(driver.find_element_by_xpath("//p[@class='result__num']/em").text)
    add_log(f"{num_jobs}件の求人が見つかりました")
    #ページを取得する回数
    search_repeat_num = num_jobs//50 +1

    # ページ終了まで繰り返し取得
    for i in range (search_repeat_num):
        #pgを入れない
        if i == 0:
            url = url_before+url_after
        #pgを入れる
        else:
            url = f"{url_before}pg{i+1}{url_after}"
        try:
            driver.get(url)
            time.sleep(5)
            #ページ内の全情報を取得
            info_list = driver.find_elements_by_xpath("//div[@class='container__inner']/div[contains(@class,'cassetteRecruit')]")
            add_log(f"{i+1}/{search_repeat_num}ページ目のデータの取得に成功しました")
        except:
            add_log(f"{i+1}/{search_repeat_num}ページ目のデータの取得に失敗しました")
            pass
        #詳細情報を取得してデータフレームを作成
        try:
            df,count = get_info(info_list,df,count)
        except:
            pass
    #CSVファイルにcp932で書き込む（エンコードできない文字は無視する）
    with open("result.csv", mode="w", encoding="cp932", errors="ignore") as f:
        #pandasでファイルオブジェクトに書き込む
        df.to_csv(f)
        
    

    
def get_info(info_list,df,count):
    for info in info_list:
        #IDを一つ増やす
        count += 1
        #各項目の値を初期化
        company_name=copy_sub=copy_main=job_details=target=work_place=monthly_salary=yearly_salary= ""
        #会社名+短いコピー
        try:
            company_name_copy = info.find_element_by_tag_name("h3").text
            #会社名と短いコピーに分割
            company_name_copy = company_name_copy.split('|')
            company_name = company_name_copy[0]
            copy_sub = "|".join(company_name_copy[1:])
        except:
            add_log(f"{count}件目の会社名と短いコピーのデータが取得できませんでした")
            pass
        #メインコピー
        try:
            copy_main = info.find_element_by_xpath(".//p[contains(@class,'cassetteRecruit')]/a").text
        except:
            add_log(f"{count}件目のメインコピーのデータが取得できませんでした")
            pass
        #表の中の項目
        try:
            job_details = info.find_element_by_xpath(".//th[text() = '仕事内容']/following-sibling::td").text
        except:
            add_log(f"{count}件目の仕事内容のデータが取得できませんでした")
            pass
        try:
            target = info.find_element_by_xpath(".//th[text() = '対象となる方']/following-sibling::td").text
        except:
            add_log(f"{count}件目の対象となる方のデータが取得できませんでした")
            pass
        try:
            work_place = info.find_element_by_xpath(".//th[text() = '勤務地']/following-sibling::td").text
        except:
            add_log(f"{count}件目の勤務地のデータが取得できませんでした")
            pass
        try:
            monthly_salary = info.find_element_by_xpath(".//th[text() = '給与']/following-sibling::td").text
        except:
            add_log(f"{count}件目の給与のデータが取得できませんでした")
            pass
        try:
            yearly_salary = info.find_element_by_xpath(".//th[text() = '初年度年収']/following-sibling::td").text
        except:
            add_log(f"{count}件目のの初年度年収のデータが取得できませんでした")
            pass
        df.loc[count] = [company_name, copy_sub, copy_main,job_details,target,work_place,monthly_salary,yearly_salary]
        add_log(f"{count}件目の登録が終わりました")
    return [df,count]
    

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
