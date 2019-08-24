import pandas as pd

# 处理训练数据 -> dict{user_id:{item_id:rating}}
df = pd.read_csv('../row_data/u.data',
                 sep='\t',
                 nrows=10,
                 names=['user_id','item_id','rating','timestamp'])
# print(max(df['rating']))
# print(min(df['rating']))
# print(df.dtypes)

d = dict()
for _,row in df.iterrows():
    # 类型转换
    user_id = str(row['user_id'])
    item_id = str(row['item_id'])
    rating = row['rating']
    if user_id not in d.keys():
        d[user_id] = {item_id:rating}
    else:
        d[user_id][item_id] = rating
# print(d)