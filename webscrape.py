# Stardew Valley Farm Info Aggregator
# Pulls n farms randomly from upload.farm and aggregates certain pertinent data points about each farm into a pandas dataframe
# then saves to csv

import requests as req
import pandas as pd
from bs4 import BeautifulSoup
import random
from time import sleep

base_uri = "https://upload.farm/"
slug_list = []
n = 1000
for i in range(n):
    try:
        print(f'Randomly selecting farm {i+1} of {n}')
        rand_page = random.randint(1,16104)
        # rand_page = 16104
        full_uri = f'{base_uri}all?p={rand_page}'
        resp = req.get(full_uri)
        resp_bs4 = BeautifulSoup(resp.text, features="html.parser")
        divTags = resp_bs4.body.find_all('div', attrs={'class':'col-md-4 col-sm-6 text-center previewbox'})
        rand_entry = random.randint(1,len(divTags)) - 1
        # rand_entry = 1
        tag = divTags[rand_entry]
        link = tag.find_all('a')[0]
        slug_list.append([rand_page,rand_entry,link['href']])
    except Exception as e:
        print(f'ran into an error: {e}. continuing')
        continue

final_df = pd.DataFrame(slug_list, columns=['page_index', 'page_element_index', 'farm_id'])
final_df[["user_name", "farm_name", "gender", "spouse", "pet_type", "pet_name", "total_earnings", "favorite_thing"]] = ''

for index, row in final_df.iterrows():
    try:
        print(f'Pulling data for farm {index+1} of {n}.')
        farm_uri = f'{base_uri}{row["farm_id"]}'
        farm_resp = req.get(farm_uri)
        farm_resp_bs4 = BeautifulSoup(farm_resp.text, features="html.parser")
        # get username, spouse, pet type, pet name
        summary_farmDivTag = farm_resp_bs4.find_all('div', attrs={'class':'info--summary-text'})[0]
        body_farmDivTag = farm_resp_bs4.find_all('div', attrs={'class':'info--body'})[0]
        body_farmSubDivTag = body_farmDivTag.find_all('div')
        for i in body_farmSubDivTag:
            try:
                if i.find('dt').text == 'Gender':
                    final_df.at[index, 'gender'] = i.find('dd').text.strip()
                if i.find('dt').text == 'Favorite Thing':
                    final_df.at[index, 'favorite_thing'] = i.find('dd').text.strip()
                if i.find('dt').text == 'Total Earnings':
                    final_df.at[index, 'total_earnings'] = i.find('dd').text.strip()[:-1].replace(',','')
            except:
                continue
        summary_farmP = summary_farmDivTag.find('p')
        summary_farmB = summary_farmP.find_all('b')
        summary_farmP_text = summary_farmP.text
        if summary_farmP_text.find('and has a pet') > 0:
            pet_type = summary_farmP_text[summary_farmP_text.find('and has a pet')+15:summary_farmP_text.find('named',summary_farmP_text.find('and has a pet'))].strip()
            pet_name = summary_farmP_text[summary_farmP_text.find('named',summary_farmP_text.find('and has a pet'))+6:len(summary_farmP_text)].strip().replace('.','')
            final_df.at[index, 'pet_type'] = pet_type
            final_df.at[index, 'pet_name'] = pet_name
        else:
            final_df.at[index, 'pet_type'] = "NA"
            final_df.at[index, 'pet_name'] = "NA"

        final_df.at[index, 'user_name'] = summary_farmB[0].text

        if summary_farmP_text.find('unmarried') > 0:
            final_df.at[index, 'spouse'] = "Unmarried"
        else:
            final_df.at[index, 'spouse'] = summary_farmB[1].text


        # get farm name
        title_farmDivTag = farm_resp_bs4.find_all('div', attrs={'class':'title-title'})[0]
        final_df.at[index, 'farm_name'] = title_farmDivTag.text[:-5].strip()
    except Exception as e:
        print(f'ERROR: {e}. Con')
        final_df.at[index, 'total_earnings'] = "ERROR"
        final_df.at[index, 'favorite_thing'] = "ERROR"
        final_df.at[index, 'gender'] = "ERROR"
        final_df.at[index, 'user_name'] = "ERROR"
        final_df.at[index, 'spouse'] = "ERROR"
        final_df.at[index, 'pet_type'] = "ERROR"
        final_df.at[index, 'pet_name'] = "ERROR"
        final_df.at[index, 'farm_name'] = "ERROR"
print(final_df)

final_df.to_csv('stardewvalley_aggregator_data.csv')