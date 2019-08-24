from cf.util import generate_train_data
# import cf.util.generate_train_data
import math
train_data_path = './mid_data/train.data'
sim_user_path = './mid_data/sim_user_user.txt'
# train_data = generate_train_data(None)
# with open(train_data_path,'w') as f:
#     f.write(str(train_data))
# 输入数据形式：train_data{u:{item:score}}
def user_normal_sim(train_data):
    w = dict()
    for u in train_data.keys():
        if u not in w:
            w[u] = dict()   # 存u用户相似的用户
        for v in train_data.keys():
            if u == v:
                continue
            # 相似度计算，及卡尔德相似度：通过两个用户共同拥有的物品集合数量，除以两个用户的物品的平均数量
            # 分别将u，v的集合转换成set形式，再互相&运算（各自去重，找两者的交集）
            w[u][v] = len(set(train_data[u]) & set(train_data[v])) # 此时的w的结构为w{u:{v:sim_itemNum}}
            w[u][v] = 2 * w[u][v] / (len(train_data[u])+len(train_data[v]))*1.0 # 此时的w的结构为w{u:{v:sim_rate}}
    # print(train_data)
    # print(w['196'])
    # print("all users cnt:",train_data.keys())
    # print("user['196'] sim users cnt:",len(w['196']))
    # print(train_data.items())
    return w

# 优化计算用户之间的相似度，user->items => item->users
def user_sim(train_data):
    item_users = dict()
    for u,items in train_data.items():  # .items返回key给u，value给items
        # print(u)    # u是用户id
        # print(items)    # items是一个“商品->分数”的集合
        # 倒排操作{item:{u,v,...}}
        for item in items.keys():
            if item not in item_users:
                # 如果item_users集合里面没有当前item，则将该item作为key加入到集合，并创建一个set集合的value
                item_users[item] = set()
            # 如果item_users集合里面存在当前item，则在该item所对应的set集合中添加当前遍历的user
            item_users[item].add(u)

    C = dict() # 存放统计用户与用户共同item数量
    N = dict() # 存放用户对应的item数量

    for item,users in item_users.items():
        for u in users:
            # 获取该用户对应的item数量，其实对于每一行item_users，N[u]只会累加1
            if N.get(u,-1) == -1:
                N[u] = 1
            N[u] += 1
            # 获取用户与用户之间的共同item数量
            if C.get(u,-1) == -1:
                C[u] = dict()
            for v in users: # 遍历同一个item下的users集合
                if u == v:
                    continue
                # 其实对于每一个users集合（每一行item_users），C[u][v]最多只会累加1
                if C[u].get(v,-1) == -1:
                    C[u][v] = 1
                # C[u][v] += 1 # 加的这个1，其实就是一个共同item； 此时的C的结构为C{u:{v:sim_itemNum}}
                # 优化：对热门商品降权 1/log(n+1) , n为购买该商品的用户量。
                # 实际开发中，是对每一个商品都进行降权操作，计算相似商品数量时，累加的不是1，而是降权之后的值。
                # 相当于，降权之前，物品的权重都是1，打分都一样，降权之后，每个商品都自己对应的打分。
                C[u][v] += 1/math.log(1+len(item_users[item]))

    del item_users
    # 计算最终相似度：u，v共同物品数量，除以（u的物品数量与v的物品数量的和的平均数）
    for u, v_itemNum in C.items():
        for v, itemNum in v_itemNum.items():
            C[u][v] = 2*C[u][v]/float(N[u]+N[v]) # 此时的C的结构为C{u:{v:sim_rate}}
    return C
# with open(sim_user_path,'w') as fw:
#     fw.write(str(user_sim(train_data)))

def recommend(user_id, C, train_data, k=5):
    rank = dict() # rank={v_item:cuv*v_rating}
    # 获取196用户对应的items
    interacted_items = train_data[user_id].keys()
    # 去相似的top k个用户。sorted第一个参数是待排序对象，key是基于排序的基础
    # C[user_id].items()：196用户对应的相似用户v，以及相似度cuv的字典
    # key=lambda x:x[1]：根据第二个（即cuv）排序
    for v,cuv in sorted(C[user_id].items(), key=lambda x:x[1],reverse=True)[0:k]:
        # 取出相似用户对应的item和rating
        for v_i, v_rating in train_data[v].items():
            # 过滤掉196用户已经评价过的电影（或已经购买过的物品）
            if v_i in interacted_items:
                continue
            elif rank.get(v_i,-1) == -1:
                rank[v_i] = 0
            # 计算物品打分：用户相似度*相似用户对电影（物品）的打分
            # 各个相似用户都评价了同一个item，那么user_id对应的这个item的可能评分是累加的
            rank[v_i] += cuv*v_rating

if __name__ == '__main__':
    # 读取数据
    train_data = dict()
    with open(train_data_path, 'r') as ft:
        train_data = eval(ft.read())
    C = dict()
    with open(sim_user_path, 'r') as fs:
        C = eval(fs.read())

    user_id = '196'
    k = 5
    rank = recommend(user_id,C,train_data,k)
    print(sorted(rank.items(),key=lambda x:x[1],reverse=True)[0:k])
