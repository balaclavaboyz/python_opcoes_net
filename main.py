import sqlite3
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

def print_minhas_posicoes():
    con=sqlite3.connect('options.sqlite3')
    df=pandas.read_sql('SELECT * FROM minhas_posicoes',con)
    return df

def add_entrada():
    con=sqlite3.connect('options.sqlite3')
    cur=con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS minhas_posicoes (
        id INTEGER PRIMARY KEY,
        ticker TEXT,
        cv TEXT,
        ultimo REAL,
        preco REAL,
        quantidade INTERGER,
        investido REAL,
        status INTERGER,
        valor_total_aberto REAL,
        valor_total_fechado REAL,
        data BLOB
        )''')

    ticker=input('Escreva o ticker(abev3, abevh137...): ')
    data=input('Data que foi feito(dd/mm/aaaa): ')
    preco=input('Quando custa o ticker(1.01, 0.5...): ')
    quantidade=input('Quantos lotes(100, 300, 350...): ')
    resposta=input('Posicao esta aberto(s/n)?: ')
    status=-1
    while(True):
        if resposta=='s':
            status=1
            break
        elif resposta=='n':
            status=0
            break
        else:
            resposta=input('Posicao esta aberto(s/n)?: ')
    resposta=input('Comprou ou vendeu(c/v)?: ')
    cv=-1
    while(True):
        if resposta=='c':
            cv=1
            break
        elif resposta=='v':
            cv=0
            break
        else:
            resposta=input('Comprou ou vendeu(c/v)?: ')

    cur.execute('''
        INSERT INTO minhas_posicoes(
            ticker,cv,preco,quantidade,status,data
        )
        VALUES(
            ?,?,?,?,?,?
        )
    ''',(ticker,cv,preco,quantidade,status,data))
    con.commit()
    con.close()

if __name__=="__main__":
    # carregar o db e ja printar no menu
    # menu
    # db print
    menu_options={
        1:'atualizar preco abev3 e salvar no db',
        2:'Mostrar a tabela de opcoes',
        3:'adicionar entrada',
        4:'Sair'
    }
    def print_menu():
        for i in menu_options.keys():
            print(i,menu_options[i])

    preco_ticker_atual = atualizar_preco_atual()
    while(True):
        print("\n\n*** preco atual ***\n\nAbev3: "+ preco_ticker_atual[0]+"\n")
        print('*** minhas posicoes ***\n')
        print(print_minhas_posicoes())
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
            add_entrada()
        elif option==4:
            print('Bye.')
            exit()
        else:
            print('Escolha invalido, escolher um numero.')

