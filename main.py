import sqlite3
from statistics import median_grouped
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas
import requests
url='https://opcoes.net.br/opcoes/bovespa/ABEV3'


def atualizar_preco_opcoes():
    opcoes_para_chrome=Options()
    opcoes_para_chrome.headless=True
    driver=webdriver.Chrome(options=opcoes_para_chrome)
    driver.get(url)
    time.sleep(2)
    soup=BeautifulSoup(driver.page_source,"html.parser")
    driver.quit()
    lista_opcoes=soup.find(id="tblListaOpc").prettify()
    lista_opcoes=lista_opcoes.replace(',','.')
    list_of_dataframe=pandas.read_html(lista_opcoes,header=1)
    df=pandas.concat(list_of_dataframe)
    resultado_em_csv=df.to_csv(encoding='utf-8')
    
    with open('./preco.csv','w',encoding='utf-8') as f:
        f.write(resultado_em_csv)
        print('Salvado em preco.csv')
    
    return df

def atualizar_preco_atual():
    r=requests.get('https://statusinvest.com.br/acoes/abev3')
    soup=BeautifulSoup(r.text,'html.parser')
    bomdia=soup.select_one('#main-2 > div > div > div > div > div > div > div > strong')
    preco_atual=bomdia.contents
    return preco_atual

def salvar_precos_no_db(df):


    con=sqlite3.connect('options.sqlite3')

    df.to_sql('df',con,if_exists="replace")
    con.commit()
    con.close()

def print_df():
    con=sqlite3.connect('options.sqlite3')
    df=pandas.read_sql('SELECT * FROM df',con)
    print(df)

if __name__=="__main__":
    menu_options={
        1:'atualizar preco abev3 e salvar no db',
        2:'Mostrar a tabela de opcoes',
        3:'Sair'
    }
    def print_menu():
        for i in menu_options.keys():
            print(i,menu_options[i])

    preco_ticker_atual = atualizar_preco_atual()
    while(True):
        print("\n\n*** menu ***\n\nAbev3: "+ preco_ticker_atual[0]+"\n")
        print_menu()
        option=''
        try:
            option=int(input('Escolha: '))
        except:
            print('Por favor escrever um numero: ')
        if option == 1:
            temp_df_precos=atualizar_preco_opcoes()
            salvar_precos_no_db(temp_df_precos)
        elif option==2:
            print_df()
        elif option==3:
            print('Bye.')
            exit()
        else:
            print('Escolha invalido, escolher um numero.')

