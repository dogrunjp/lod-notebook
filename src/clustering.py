import pandas as pd
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA

MONGOHOST = "localhost:27017"
MONGODB = "lod_notebook"

client = MongoClient(MONGOHOST)
db_connect = client[MONGODB]


def read_mongo():
    cur = db_connect["area_data"].find()
    df = pd.DataFrame(list(cur))

    df_pp = pd.DataFrame()
    for k, v in df.iteritems():
        # 数値であるなら人口一人当たりの値に変換する
        try:
            s = df[k].astype(float)/df.total.astype(float)
            df_pp[k] = s
        except:
            df_pp[k] = df[k]

    # 村等特定の値が含まれないデータをのぞく
    df_pp = df_pp[df_pp.byoin.notnull()]
    # 文字列のデータをレンジ指定で外すためにソートする。
    df_pp = df_pp.rename(columns={'_id': '_area', 'city': '_city', 'pref': '_pref'})
    df_pp.sort_index(axis=1, inplace=True)
    # 標準化するためにNaNを0で埋める
    df_pp.fillna(0, inplace=True)
    # 数値データを標準化
    scale = StandardScaler()
    df_pp.ix[:, 3:] = scale.fit_transform(df_pp.ix[:, 3:])

    """
    # データをMinMaxScalerで正規化した場合
    mms = MinMaxScaler()
    df_pp.ix[:,3:] = mms.fit_transform(df_pp.ix[:,3:])
    """
    pca = PCA(n_components=2)

    pca_result = pca.fit_transform(df_pp.ix[:, 3:])
    # arrayとして取得できる
    pca_result[:, 0]

    pca_df = pd.DataFrame(pca.fit_transform(df_pp.ix[:, 3:]), columns=('PC1', 'PC2'))
    pca_df.plot(kind='scatter', x='PC1', y='PC2')


