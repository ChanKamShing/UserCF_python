import pandas as pd

def generate_train_data(nrows=10):
    # 处理训练数据 -> dict{user_id:{item_id:rating}}
    df = pd.read_csv('../row_data/u.data',
                     sep='\t',
                     nrows=nrows,
                     names=['user_id', 'item_id', 'rating', 'timestamp'])

    # d为每个用户的商品及对应打分的列表
    d = dict()
    for _, row in df.iterrows():
        # 类型转换
        user_id = str(row['user_id'])
        item_id = str(row['item_id'])
        rating = row['rating']
        if user_id not in d.keys():
            d[user_id] = {item_id: rating}
        else:
            d[user_id][item_id] = rating
    return d