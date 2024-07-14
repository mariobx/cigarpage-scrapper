from bs4 import BeautifulSoup
from selenium import webdriver
import re
from selenium.webdriver.support.ui import WebDriverWait
import numpy as np
from prettytable import PrettyTable, ALL
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
import os
from datetime import datetime
import threading
import sys
url_list = ['https://www.cigarpage.com/class-34-fugazi-compare-to-davidoff-white-label-aniversario.html', 'https://www.cigarpage.com/oliva-serie-v.html', 'https://www.cigarpage.com/montecristo-classic.html', 'https://www.cigarpage.com/e-p-carrillo-pledge-prequel.html', 'https://www.cigarpage.com/padron-1926-serie.html']


start_line = 'cigar-alt-name'
end_line = 'addToCartDiv' 



class ReturnValueThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None

    def run(self):
        if self._target is None:
            return  # could alternatively raise an exception, depends on the use case
        try:
            self.result = self._target(*self._args, **self._kwargs)
        except Exception as exc:
            print(f'{type(exc).__name__}: {exc}', file=sys.stderr)  # properly handle the exception

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self.result
    




def create_cigar_info_txt(html_text):
    flag = False
    relevant_txt = []
    html_text = html_text.split('\n')
    with open('cigarpage.txt', 'w') as f:
        for i in range(len(html_text)):
            html_text[i].strip()
            if start_line in html_text[i]:
                flag = True
            if flag:
                relevant_txt.append(html_text[i])
                f.write(html_text[i] + '\n')
            if end_line in html_text[i]:
                flag = False
    f.close()
    relevant_txt = [i.strip() for i in relevant_txt]
    return relevant_txt

def populate_lists(relevant_text):
    for i in range(len(relevant_text)):
        if cigar_name_info in relevant_text[i]:
            i += 1
            cigar_name_list.append(relevant_text[i])
        if pack_value_info in relevant_text[i]:
            i+=1
            if is_pack_string(relevant_text[i]):
                pack_values_list.append(relevant_text[i])
        if price_info in relevant_text[i]:
            i+=1
            w=i-2
            if 'visible-xs a-right' not in relevant_text[w]:
                price_list.append(relevant_text[i])
        if cigar_nationality_info in relevant_text[i]:
            i+=3
            cigar_nationality_list.append(relevant_text[i])
        if wrapper_info in relevant_text[i]:
            i+=3
            wrapper_list.append(relevant_text[i])
        if filler_info in relevant_text[i]:
            i+=3
            filler_list.append(relevant_text[i])
        if original_price_info in relevant_text[i]:
            i+=2
            w=i-8
            if 'visible-xs a-right' not in relevant_text[w]:
                original_price_list.append(relevant_text[i])
        if is_points_string(relevant_text[i]):
            points_info_list.append(relevant_text[i])

def get_lists_of_information(string_of_html):
    relevant_txt = create_cigar_info_txt(string_of_html)
    populate_lists(relevant_text=relevant_txt)


    for i in range(len(points_info_list) - 1, -1, -1):
        if i % 2 == 0:
            del points_info_list[i]
    fix_price_list = []
    for i in range(len(price_list)):
        if bool(re.match(r'^\$\d+\.\d+$', price_list[i])):
            fix_price_list.append(price_list[i])
    
    price_list.clear()
    price_list.extend(fix_price_list)

def is_pack_string(s):
    pattern = [r'^\d+-PACK$', r'^BOX OF \d+$', r'^\d+ CIGARS']
    for i in pattern:
        if bool(re.match(i, s)):
            return True
    return False

def is_points_string(s):
    pattern = r'^Earn \d+ Cigar Points$'
    return bool(re.match(pattern, s))

def extract_number(s):
    if is_points_string(s):
        parts = s.split()
        number = parts[1]
        return int(number)
    return None

def percent_off(original_price, sale_price):
    if original_price != 0:
        return '%'+str(round((np.multiply(np.divide((np.subtract(original_price, sale_price)), original_price), 100)), 2))+' off!'
    else:
        return

def get_html_info(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(0.5)
    html = driver.execute_script("return document.documentElement.innerHTML;")
    soup = BeautifulSoup(html, 'html.parser')
    html_txt = soup.prettify()
    return html_txt




def thread_chrome_driver(urls):
    threads = []
    results = []
    for i in range(len(urls)):
        threads.append(ReturnValueThread(target=get_html_info, args=(urls[i],)))
        threads[i].start()
    
    for i in range(len(threads)):
        threads[i].join()
        result = threads[i].result
        results.append(result)
                       
    return results




def remove_dollar_sign_and_convert(price_string):
    return float(price_string.replace('$', ''))







def update_past_data_csv():
    today = datetime.today().date()
    if not os.path.isfile('past_data.csv'):
            df = pd.DataFrame(rows)
            df.to_csv('past_data.csv')

    df = pd.read_csv('past_data.csv')
    current_df = pd.DataFrame(rows)

    if today not in df['Time'].values:
        print("Today's date: ", today)
        df = pd.concat([df, current_df], ignore_index=True)
        df['Percent float'] = df['Percent Sale'].apply(lambda x: float(re.findall(r'\d+', x)[0]))

        df.to_csv('past_data.csv')


def average_percent_off():
    df = pd.read_csv('past_data.csv')
    
    grouped_df = df.groupby('Cigar')['Percent float'].mean().reset_index()
    
    grouped_df.columns = ['Cigar', 'Average Percent Off']
    
    grouped_df.to_csv('cigar_analysis.csv', index=False)



def get_float_from_percent_string(s):
    return float(re.findall(r'\d+', s)[0])




















string_of_html = ''
lists_thread_cigar = thread_chrome_driver(url_list)


for i in range(len(lists_thread_cigar)):
    string_of_html = string_of_html + lists_thread_cigar[i]


cigar_name_info = 'cigar-alt-name'
pack_value_info = 'white-space: nowrap'
price_info = 'price'
cigar_nationality_info = 'Origin'
wrapper_info = 'Wrapper'
filler_info = 'Filler'
original_price_info = 'strikethrough'
points_info = 'font-weight:bold;color:red;'
end_cigar_info_line = 'In Stock'

cigar_name_list = []
pack_values_list = []
price_list = []
cigar_nationality_list = []
wrapper_list = []
filler_list = []
original_price_list = []
points_info_list = []
rows = []






get_lists_of_information(string_of_html=string_of_html)



float_price_list = []
original_float_price_list = []
percent_off_list = []
time_list = []
statistically_significant = []

for i in range(len(price_list)):
    float_price_list.append(remove_dollar_sign_and_convert(price_list[i]))
    original_float_price_list.append(remove_dollar_sign_and_convert(original_price_list[i]))
    time_list.append(datetime.today().date())
    percent_off_list.append(percent_off(original_float_price_list[i], float_price_list[i]))
    analysis_df = pd.read_csv('cigar_analysis.csv')
    if cigar_name_list[i] in analysis_df['Cigar'].values:
        average_percent_off_for_cigar = analysis_df.loc[analysis_df['Cigar'] == cigar_name_list[i], 'Average Percent Off'].values[0]
        if get_float_from_percent_string(percent_off_list[i]) >= average_percent_off_for_cigar:
            statistically_significant.append('Yes')
        else:
            statistically_significant.append('No')
    else:
        statistically_significant.append('No')

        
for i in range(len(cigar_name_list)):
    rows.append({'Cigar': cigar_name_list[i], 'Pack': pack_values_list[i], 
                    'Price': price_list[i], 'Original Price': original_price_list[i],'Percent Sale': percent_off_list[i], 'Statistically Significant': statistically_significant[i] ,'Cigar Nationality': cigar_nationality_list[i], 
                    'Wrapper': wrapper_list[i], 'Filler': filler_list[i], 'Points': points_info_list[i], 'Time': time_list[i]})


# print(      
#     len(cigar_name_list),
#     len(pack_values_list),
#     len(price_list),
#     len(cigar_nationality_list),
#     len(wrapper_list),
#     len(filler_list),
#     len(original_price_list),
#     len(points_info_list),
#     len(time_list),
#     len(statistically_significant)
# )


update_past_data_csv()
average_percent_off()


current_info = pd.DataFrame(rows)
# current_info.to_csv('current_info.csv', index=False)


prettytable = PrettyTable()
prettytable.field_names = ['Cigar', 'Pack', 'Price', 'Original Price', 'Percent Sale', 'Statistically Significant' ,'Cigar nationality', 'Wrapper', 'Filler', 'Points', 'Time']
for row in rows:
    prettytable.add_row([row['Cigar'], row['Pack'], row['Price'], row['Original Price'], row['Percent Sale'], row['Statistically Significant'] ,row['Cigar Nationality'], row['Wrapper'], row['Filler'], row['Points'], row['Time']])
prettytable.hrules = ALL
prettytable.vrules = ALL

print(prettytable)





