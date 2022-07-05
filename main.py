import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas
url='https://opcoes.net.br/opcoes/bovespa/ABEV3'

con=sqlite3.connect('options.sqlite3')

cur=con.cursor()

def atualizar_precos_abev3():
    driver=webdriver.Chrome(options=Options().add_argument("--headless"))
    driver.get(url)
    time.sleep(2)
    soup=BeautifulSoup(driver.page_source,"html.parser")
    driver.quit()
    lista_opcoes=soup.find(id="tblListaOpc").prettify()
    # print(lista_opcoes)
    list_of_dataframe=pandas.read_html(lista_opcoes)
    df=pandas.concat(list_of_dataframe)
    resultado_em_csv=df.to_csv(encoding='utf-8')
    
    with open('preco.csv','w',encoding='utf-8') as f:
        f.write(resultado_em_csv)

def salvar_sqlite():

    cur.execute('''
    CREATE TABLE IF NOT EXISTS abev3 (id INTERGER PRIMARY KEY )
    ''')
    con.commit()
    con.close()


if __name__=="__main__":
    # atualizar_precos_abev3()
    salvar_sqlite()