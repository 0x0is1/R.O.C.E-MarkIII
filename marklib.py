import calendar, time

def datetime2timestamp(str_date: str):
    datetime=str_date.split(', ')[1].split(' +0530')[0]
    month_str=datetime.split(' ')[1]
    datetime=datetime.replace(month_str, str(list(calendar.month_abbr).index(month_str)))
    timestamp=time.mktime(time.strptime(datetime, "%d %m %Y %H:%M:%S"))
    return timestamp

def rawdatagen(data):
    title=data.find('title').text
    link=data.find('link').next_sibling
    updatedat=data.find('updatedat').text
    description=data.find('description').text
    fullimage=data.find('fullimage').text
    return [title, link, updatedat, description, fullimage]

def newsgen(data, last_updated: str):
    store = []
    for i in data:
        current_last_updated=datetime2timestamp(i.find('pubdate').text)
        if current_last_updated > last_updated:r=rawdatagen(i);store.append(r)
    llast_updated=datetime2timestamp(data[-1].find('pubdate').text)
    return store, llast_updated

