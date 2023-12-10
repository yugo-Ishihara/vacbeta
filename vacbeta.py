import subprocess as sp
import os
import pandas as pd
import sys
import plotly.graph_objects as go

if os.path.exists('owid-covid-data.csv') == True:
    # sp.call("rm owid-covid-data.csv",shell=True)
    sp.call("rm *.csv",shell=True)

else:
    pass

sp.call('wget https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv', shell=True)
sp.call('wget https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv', shell=True)
sp.call('wget https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/locations.csv', shell=True)

df_vaccination = pd.read_csv('vaccinations.csv')
df_owid_covid = pd.read_csv('owid-covid-data.csv')
df_vac_kind = pd.read_csv('locations.csv')

df_v = df_vaccination[['location', 'date', 'total_vaccinations', 'people_vaccinated',
                       'people_fully_vaccinated', 'total_boosters','daily_vaccinations', 'total_vaccinations_per_hundred', 'total_boosters_per_hundred']]
df_o = df_owid_covid[['location', 'date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths', 'population']]
df_vk = df_vac_kind[['location', 'vaccines']]

w = 'World'
# country = 'Japan'
# country = sys.argv[2:]
print('国名を入れてください')
country = input()
country = str(country)

df_country_vac = df_v.query('location == @country')
df_country_owid = df_o.query('location == @country')
vac_kind = df_vac_kind.query('location == @country')

world_pop = df_owid_covid.query('location == @w')
world_pop = world_pop['population'].max()

country_pop = df_country_owid['population'].max()

vac_name = str(vac_kind['vaccines'].iloc[-1])

dd_w = df_owid_covid.query('location == @w')
dd = df_country_owid.merge(df_country_vac, how="inner", on = ["date", 'location'])
dd_ = dd.merge(dd_w, how="inner", on = ["date"])
# dd['vac_score'] = dd['new_deaths'] / dd['total_vaccinations_per_hundred']
# dd['vac_boost_score'] = dd['new_deaths'] / dd['total_boosters_per_hundred']

dd_['beta_death_e'] = (dd_['new_deaths_x'] + dd_['new_deaths_y'] + 1) / (dd_['new_deaths_x'] + dd_['new_deaths_y'] + dd_["total_vaccinations_x"] - dd_['people_fully_vaccinated_x'] + 2)
dd_['beta_case_e'] = (dd_['new_cases_x'] + dd_['new_cases_y'] + 1) / (dd_['new_cases_x'] + dd_['new_cases_y'] + dd_["total_vaccinations_x"] - dd_['people_fully_vaccinated_x'] + 2)

dd.reset_index()
# dd['vac_score_diff'] = dd['vac_score'].pct_change()
# dd.to_csv('result.csv')

# Japan
# dd_ = dd_[dd_.shape[0]-650:dd_.shape[0]]
# others
dd_ = dd_[dd_.shape[0]-730:dd_.shape[0]]


fig = go.Figure()
# fig.add_trace(go.Scatter(
#     x=dd['date'], y=dd['vac_score'], mode='lines', name="vac_score", yaxis='y1'))
# fig.add_trace(go.Scatter(
#     x=dd['date'], y=dd['vac_boost_score'], mode='lines', name="vac_boost_score", yaxis='y2'))
# fig.add_trace(go.Scatter(
#     x=dd['date'], y=dd['vac_score_diff'], mode='lines', name="vac_score_diff", yaxis='y2'))

fig.add_trace(go.Scatter(
    x=dd_['date'], y=dd_['beta_death_e'], mode='lines', name="booster_deaths", yaxis='y1'))
fig.add_trace(go.Scatter(
    x=dd_['date'], y=dd_['beta_case_e'], mode='lines', name="booster_newcases", yaxis='y2'))

# fig.add_trace(go.Scatter(
#     x=dd['date'], y=dd['new_deaths'], mode='lines', name="new_deaths", yaxis='y1'))

fig.update_layout(yaxis1=dict(side='left'),
                  yaxis2=dict(side='right', 
                              showgrid=False,
                              overlaying='y'),
                    title=country + '<br>' + 'Boosted Expected value' + '<br>' + 'vaccines : ' + vac_name)

fig.show()