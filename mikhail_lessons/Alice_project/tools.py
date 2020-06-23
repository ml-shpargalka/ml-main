from glob import glob


def prepare_train_set(path_to_csv_files, session_length=10, text=False):
    
    def union_all(list_files):
        pdfs = []
        for fl in list_files:
            pdf = pd.read_csv(fl)
            pdf["user_id"] = fl.replace(path_to_csv_files+"/",'').replace('user','').replace('.csv','').replace('0','')
            pdf['session_id'] = pdf.index/session_length
            pdfs.append(pdf)

        return pd.concat(pdfs, axis=0, ignore_index=True)


    frame = union_all(glob(path_to_csv_files + "/user*.csv"))

    frame["site"] = frame["site"].apply(
                lambda site: site.replace('.com','').replace('http://','').replace('www.',''))

    site_freq = dict()
    index = 0
    
    agg_df = frame[['site', 'timestamp']]\
    .groupby('site') \
    .count() \
    .reset_index('site') \
    .rename(columns = {'timestamp': 'count'}) \
    .sort_values(['count'], ascending=False)

    for row in agg_df.iterrows():
        index += 1
        site_freq[row[1]['site']] = (index,row[1]['count'])
    
    if not text:
        frame["site"] = frame["site"].apply(lambda s: site_freq[s][0])

    def get_num_sites(site_row):
        size = len(site_row)
        if size > session_length:
            site_row = site_row[:session_length]
        elif size < session_length:
            for r in range(session_length-size):
                site_row.append('0')
        return site_row
    
    frame_sites = frame\
    .groupby(['user_id','session_id'])['site']\
    .apply(list)\
    .reset_index('user_id')

    frame_sites['site'] = frame_sites['site'].apply(get_num_sites)

    frame_sites[['site'+str(r) for r in range(1,10+1)]] = pd.DataFrame(frame_sites['site'].values.tolist(), 
                                                                       index=frame_sites.index)

    frame_sites.drop('site', axis=1, inplace=True)

    return frame_sites, site_freq