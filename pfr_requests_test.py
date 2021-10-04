from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import pandas as pd
import numpy as np
import time
import requests
from bs4 import BeautifulSoup


def getProxies():
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    se_driver = webdriver.Chrome(options=opts)
    url = 'https://www.us-proxy.org'
    se_driver.get(url)
    el = se_driver.find_element_by_class_name('table-responsive')
    soup = BeautifulSoup(el.get_attribute('outerHTML'),'lxml')
    proxy_table = soup.find('tbody')
    proxies = []
    for row in proxy_table.find_all('tr'):
        check_https = row.find('td',class_='hx').string
        if 'y' in check_https:
            temp_ip = row.find('td').string
            port_td = row.find_all('td')[1]
            port = port_td.string
            proxies.append(temp_ip+':'+port)
        else:
            continue
    se_driver.quit()
    return proxies

proxy_list = getProxies()

games_df = pd.read_csv('games_df.txt')

pfr_scrapeDict = {
'Bills': '0buf',
'Dolphins': '0mia',
'Jets': '0nyj',
'Patriots': '0nwe',
'Ravens': '0rav',
'Browns': '0cle',
'Bengals': '0cin',
'Steelers': '0pit',
'Colts': '0clt',
'Titans': '0oti',
'Texans': '0htx',
'Jaguars': '0jax',
'Chiefs': '0kan',
'Chargers': '0sdg',
'Broncos': '0den',
'Eagles': '0phi',
'Giants': '0nyg',
'Cowboys': '0dal',
'Redskins': '0was',
'Packers': '0gnb',
'Vikings': '0min',
'Bears': '0chi',
'Lions': '0det',
'Buccaneers': '0tam',
'Saints': '0nor',
'Falcons': '0atl',
'Panthers': '0car',
'Seahawks': '0sea',
'49ers': '0sfo',
'Cardinals': '0crd',
'Rams': '0ram',
'Raiders': '0rai'
}



dts = []
for idx, row in games_df.iterrows():
    dts.append(pd.Timestamp(row['Date']).date())

games_df.drop('Date',axis=1,inplace=True)
games_df['Date']=pd.Series(dts)

h_fd = []
a_fd = []
hRush_yds_tds = []
hpCmp_att_yd_td_int = []
h_sacked_yds = []
hPassYds = []
hTotalYds = []
hFL = []
hTO = []
h_pens_yds = []
h_3dcr = []
h_4dcr = []
hToP = []
aRush_yds_tds = []
apCmp_att_yd_td_int = []
a_sacked_yds = []
aPassYds = []
aTotalYds = []
aFL = []
aTO = []
a_pens_yds = []
a_3dcr = []
a_4dcr = []
aToP = []


base = 'https://www.pro-football-reference.com/boxscores/'


software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.MAC.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

cur_prox_idx = 0

for idx, row in games_df.iterrows():
    if idx%10==0:
        print(idx)
    dt = row['Date']
    m = dt.month
    y = dt.year
    d = dt.day
    if m < 10:
      m_str = '0' + str(m)
    else:
      m_str = str(m)
    if d < 10:
      d_str = '0' + str(d)
    else:
      d_str = str(d)
    home = row['Home Team']
    url = base + str(y) + m_str + d_str + pfr_scrapeDict[home] + '.htm'
    cur_ua = user_agent_rotator.get_random_user_agent()
    headers = {'User-Agent':cur_ua}
    while (True):
        try:
            if cur_prox_idx >= len(proxy_list):
                soup = BeautifulSoup(requests.get(url,headers=headers).text,'lxml')
            else:
                cur_prox = proxy_list[cur_prox_idx]
                prox_dict = {'http': 'http://'+cur_prox, 'https': 'https://'+cur_prox}
                soup = BeautifulSoup(requests.get(url,headers=headers,proxies=prox_dict,verify=False,timeout=10).text,'lxml')
            break
        except requests.exceptions.Timeout:
            cur_prox_idx+=1
            continue
        except requests.exceptions.ProxyError:
            cur_prox_idx+=1
            continue
        except requests.exceptions.SSLError:
            cur_prox_idx+=1
            continue
    stats = soup.find('div',id='all_team_stats')
    stats_str = str(stats)
    st_idx = stats_str.index('<!--')
    e_idx = stats_str.index('-->')
    stats_str = stats_str[:st_idx]+stats_str[st_idx+4:e_idx]+stats_str[e_idx+3:]
    stats = BeautifulSoup(stats_str,'lxml')
    table = stats.find('table',id='team_stats').find('tbody')
    if table is None:
        print('error: ' + str(idx))
    else:
        t_idx = 0
        for row in table.find_all('tr'):
            #0:First Downs
            #1:Rush-Yds-TDs
            #2:Cmp-Att-Yd-TD-INT
            #3:Sacked-Yards
            #4:Net Pass Yards
            #5:Total Yards
            #6:Fumbles-Lost
            #7:Turnovers
            #8:Penalties-Yards
            #9:Third Down Conv.
            #10:Fourth Down Conv.
            #11:Time of Possession
            stat = row.find('th').string
            vals = row.find_all('td')
            vis_stat = vals[0].string
            home_stat = vals[1].string
            if t_idx == 0:
                h_fd.append(home_stat)
                a_fd.append(vis_stat)
            elif t_idx == 1:
                hRush_yds_tds.append(home_stat)
                aRush_yds_tds.append(vis_stat)
            elif t_idx == 2:
                hpCmp_att_yd_td_int.append(home_stat)
                apCmp_att_yd_td_int.append(vis_stat)
            elif t_idx == 3:
                h_sacked_yds.append(home_stat)
                a_sacked_yds.append(vis_stat)
            elif t_idx == 4:
                hPassYds.append(home_stat)
                aPassYds.append(vis_stat)
            elif t_idx == 5:
                hTotalYds.append(home_stat)
                aTotalYds.append(vis_stat)
            elif t_idx == 6:
                hFL.append(home_stat)
                aFL.append(vis_stat)
            elif t_idx == 7:
                hTO.append(home_stat)
                aTO.append(vis_stat)
            elif t_idx == 8:
                h_pens_yds.append(home_stat)
                a_pens_yds.append(vis_stat)
            elif t_idx == 9:
                h_3dcr.append(home_stat)
                a_3dcr.append(vis_stat)
            elif t_idx == 10:
                h_4dcr.append(home_stat)
                a_4dcr.append(vis_stat)
            else:
                hToP.append(home_stat)
                aToP.append(vis_stat)
            t_idx+=1
games_df['Home FDs']=pd.Series(h_fd)
games_df['Away FDs']=pd.Series(a_fd)
games_df['Home Rushing']=pd.Series(hRush_yds_tds)
games_df['Away Rushing']=pd.Series(aRush_yds_tds)
games_df['Home Passing Cmp']=pd.Series(hpCmp_att_yd_td_int)
games_df['Away Passing Cmp']=pd.Series(apCmp_att_yd_td_int)
games_df['Home Sacked']=pd.Series(h_sacked_yds)
games_df['Away Sacked']=pd.Series(a_sacked_yds)
games_df['Home Pass Yds']=pd.Series(hPassYds)
games_df['Away Pass Yds']=pd.Series(aPassYds)
games_df['Home Total Yds']=pd.Series(hTotalYds)
games_df['Away Total Yds']=pd.Series(aTotalYds)
games_df['Home Fumbles Lost']=pd.Series(hFL)
games_df['Away Fumbles Lost']=pd.Series(aFL)
games_df['Home Turnovers']=pd.Series(hTO)
games_df['Away Turnovers']=pd.Series(aTO)
games_df['Home Penalties']=pd.Series(h_pens_yds)
games_df['Away Penalties']=pd.Series(a_pens_yds)
games_df['Home 3rd Down Conv Rate']=pd.Series(h_3dcr)
games_df['Away 3rd Down Conv Rate']=pd.Series(a_3dcr)
games_df['Home 4th Down Conv Rate']=pd.Series(h_4dcr)
games_df['Away 4th Down Conv Rate']=pd.Series(a_4dcr)
games_df['Home ToP']=pd.Series(hToP)
games_df['Away ToP']=pd.Series(aToP)
games_df.to_csv('games_df.csv',index=False)
