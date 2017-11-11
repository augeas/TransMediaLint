r = requests.get('https://www.thesun.co.uk/?s=transgender')
s=bs4(r.text,'html5lib')
#x=s.find(lambda t: 'searchresults' in t.get('class',[]))
x=s.find_all('div', attrs={'class':'searchresults'})
f=x.find_all(lambda t: 'search-date' in t.get('class',[]))
i=x.find('div', attrs={'class':'teaser-item--search'})
#i[2].find(lambda t: 'teaser__subdeck' in t.get('class',[])).text
i[2].find('p', attrs={'class':'teaser__subdeck'}).text
i[2].find('div', attrs={'class':'search-date'}).text
i[2].find('a')['href']
tag=s.find_all('div', attrs={'class':'tags--search'})
[t.text for t in tag[5].find_all('a')]
[t['href'] for t in tag[5].find_all('a')]
#['https://www.thesun.co.uk/who/hugh-hefner/', 'https://www.thesun.co.uk/topic/playboy/']


