import pickle
import random


df = pickle.load(open(
    "C:\\Users\\Priyanka\\Desktop\\petnet\\jewelry-shop\\store\\product_list.pkl", 'rb'))
similarity = pickle.load(open(
    "C:\\Users\\Priyanka\\Desktop\\petnet\\jewelry-shop\\store\\similarity.pkl", 'rb'))

# with open('product_list.pkl','rb') as prodict:
#     df = pickle.load(prodict)
#     with open('similarity.pkl','rb') as simi:
#         similarity = pickle.load(simi)


def recommend(product):
    index = df[df['id_x'] == product].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    ids = []
    for i in distances[1:6]:
        ids.append(df.iloc[i[0]].id_x)
    return ids



def user_recommendation(products):
    times = 0
    if len(products) == 1:
        times = 5
    elif  len(products) ==2 :
        times = 3
    else:
        times = 2
    ids = []
    for i in products:
        index = df[df['id_x'] == i].index[0]
        distances = sorted(
            list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        for i in distances[0:times]:
            ids.append(df.iloc[i[0]].id_x)
    random.shuffle(list(set(ids)))
    return ids