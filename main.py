#%%
import flask
from flask_cors import CORS
from flask import Flask,request
import pandas as pd
import json
from datetime import datetime
import numpy as np

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

listing_simple = pd.read_csv('./static/data/listings.csv')
neighbourhood = pd.read_csv('./static/data/neighbourhoods.csv')
listing_all = pd.read_csv('./static/data/detail/listings.csv')
review_all = pd.read_csv('./static/data/detail/reviews.csv')

csvf = open("./static/data/csvname.json", encoding='utf-8')
cname = json.load(csvf)

@app.route("/geojson",methods=["GET"])
def read_data():
    f = open("./static/data/neighbourhoods.geojson", encoding='utf-8')
    res = json.load(f)
    return json.dumps(res, ensure_ascii=False)

@app.route("/json/subway",methods=["GET"])
def read_data_subway():
    # f = open("./static/data/subway.json", encoding='utf-8')
    # res = {}
    # res['subway'] = json.load(f)
    # f2 = open("./static/data/subwayTime.json", encoding='utf-8')
    # res['subwayInfo'] = json.load(f2)

    f = open("./static/data/subway.geojson", encoding='utf-8')
    res = json.load(f)
    return json.dumps(res, ensure_ascii=False)


@app.route("/neighbourhood_count",methods=["GET"])
def get_neighbourhood_count():
    all_neighbourhood = list(neighbourhood['neighbourhood'])
    res = {}
    for n in all_neighbourhood:
        res[n] = len(listing_simple[listing_simple['neighbourhood']==n])
    return json.dumps(res, ensure_ascii=False)

@app.route("/location_data",methods=["GET"])
def get_location_data():
    region = request.args.get('region')
    bounds = request.args.get('bounds')
    cols = list(listing_simple)
    cols.insert(0,cols.pop(cols.index('longitude')))
    cols.insert(1,cols.pop(cols.index('latitude')))
    res = {}
    tmp = listing_simple.loc[:,cols]
    tmp = tmp.dropna(axis=0,how='all').fillna(0)
    print(region)
    if region != None:
        tmp = tmp[tmp['neighbourhood'].str.contains(region)]
    if bounds != None:
        bounds = bounds.split(',')
        bounds = [float(i) for i in bounds]
        leftlong = bounds[0]
        rightlong = bounds[1]
        bottomlat = bounds[2]
        toplat = bounds[3]
        tmp = tmp[(tmp['longitude'] < rightlong) & (tmp['longitude'] > leftlong) & (tmp['latitude'] > bottomlat) & (tmp['latitude'] < toplat)]

    res['data'] = tmp.values.tolist()
    return json.dumps(res, ensure_ascii=False)


@app.route("/location_data_title",methods=["GET"])
def get_location_data_title():
    cols = list(listing_simple)
    cols.insert(0,cols.pop(cols.index('longitude')))
    cols.insert(1,cols.pop(cols.index('latitude')))
    res = {}
    res['title'] = cols
    res['titleCname'] = cname['listing.csv']
    return json.dumps(res, ensure_ascii=False)


@app.route("/data_correlation",methods=["GET"])
def get_data_correlation():
    # TODO: 添加相关性分析，返回的数据将相关性高的放在一块
    cols = list(listing_all)
    res = {}
    tmp = listing_all.sample(500)
    tmp = tmp.dropna(axis=0,how='all').fillna(0)

    res['data'] = tmp.values.tolist()
    res['title'] = cols
    return json.dumps(res, ensure_ascii=False)


@app.route("/detail",methods=["GET"])
def get_detail():
    listing_id = request.args.get('id')
    listing_id = int(listing_id)
    one = listing_all[listing_all['id'] == listing_id]
    one = one.fillna(0)
    res = one.to_dict(orient='records')[0]
    return json.dumps(res, ensure_ascii=False)


@app.route("/one_reviews",methods=["GET"])
def get_one_listing_reviews():
    listing_id = request.args.get('id')
    listing_id = int(listing_id)
    oneReviews = review_all[review_all['listing_id'] == listing_id]
    oneReviews = oneReviews[oneReviews['date'] > '2019-12-01']
    listReviews = oneReviews.values.tolist()
    resdata = []
    for i in range(len(listReviews)):
        resdata.append([listReviews[i][2], 1, listReviews[i][4], listReviews[i][5]])
    # TODO: 添加对评论的情感分析
    res = {
        'smile': resdata,
        'sad': []
    }
    return json.dumps(res, ensure_ascii=False)

@app.route("/tenant/relation",methods=["GET"])
def get_tenant_relation():
    co = listing_all[listing_all['review_scores_rating']>99]
    co['has_availability'] = co['has_availability'].map(dict(t=1, f=0)) 
    co['cleaning_fee'] = co['cleaning_fee'].map(dict(t=1, f=0)) 
    co['instant_bookable'] = co['instant_bookable'].map(dict(t=1, f=0)) 
    co['weekly_price'] = pd.to_numeric(co['weekly_price'].str.replace(r'$', '').str.replace(r',', ''))
    co['price'] = pd.to_numeric(co['price'].str.replace(r'$', '').str.replace(r',', ''))
    co['monthly_price'] = pd.to_numeric(co['monthly_price'].str.replace(r'$', '').str.replace(r',', ''))

    co = co.fillna(0)
    cotype = [
    # 'host_listings_count',
    # 'host_total_listings_count',
    'accommodates',
    'bathrooms',
    'bedrooms',
    'beds',
    # 'square_feet',
    'price',
    'weekly_price',
    'monthly_price',
    # 'cleaning_fee',
    'guests_included',
    'minimum_nights',
    'maximum_nights',
    # 'minimum_minimum_nights',
    # 'maximum_minimum_nights',
    # 'minimum_maximum_nights',
    # 'maximum_maximum_nights',
    # 'minimum_nights_avg_ntm',
    # 'maximum_nights_avg_ntm',
    # 'has_availability',
    # 'availability_30',
    # 'availability_60',
    # 'availability_90',
    # 'availability_365',
    'number_of_reviews',
    # 'number_of_reviews_ltm',
    'review_scores_rating',
    # 'review_scores_accuracy',
    # 'review_scores_cleanliness',
    # 'review_scores_checkin',
    # 'review_scores_communication',
    # 'review_scores_location',
    # 'review_scores_value',
    'instant_bookable',
    'calculated_host_listings_count',
    # 'calculated_host_listings_count_entire_homes',
    # 'calculated_host_listings_count_private_rooms',
    # 'calculated_host_listings_count_shared_rooms',
    'reviews_per_month']
    co = co[cotype]
    realtion = co.corr().fillna(0)
    res = {}
    tmp = realtion.values.tolist()
    res['title'] = cotype
    data = []
    for i in range(len(tmp)):
        for j in range(len(tmp)):
            data.append([i, j, tmp[i][j]])
    res['data'] = data
    f = open("./static/data/tenant_wordcount.json", encoding='utf-8')
    res['wordcount'] = json.load(f)
    f = open("./static/data/csvname.json", encoding='utf-8')
    csvname = json.load(f)['listings.csv.gz']
    title = [csvname[i] for i in cotype]
    res['ctitle'] = title
    return json.dumps(res, ensure_ascii=False)


@app.route('/')
def index():
    return flask.send_from_directory('static', 'index.html')


@app.route('/tenant')
def tenant():
    return flask.send_from_directory('static', 'tenant.html')

@app.route('/owner')
def owner():
    return flask.send_from_directory('static', 'owner.html')


@app.route('/traffic')
def traffic():
    return flask.send_from_directory('static', 'traffic.html')


app.run(host='127.0.0.1', port=8080, debug=True)




