import pickle


df = pickle.load(open(
    "C:\\Users\\vishw\\Downloads\\django-jewelry-shop-main\\django-jewelry-shop-main\\store\\product_list.pkl", 'rb'))
similarity = pickle.load(open(
    "C:\\Users\\vishw\\Downloads\\django-jewelry-shop-main\\django-jewelry-shop-main\\store\\similarity.pkl", 'rb'))

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
    print(ids)
    return ids
