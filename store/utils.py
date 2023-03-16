import pickle


df = pickle.load(open('./reco_model/product_list.pkl','rb'))
similarity = pickle.load(open('./reco_model/similarity.pkl','rb'))


def recommend(product):
    index = df[df['id_x'] == product].index[0]
    distances = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
    ids = []
    for i in distances[1:6]:
        ids.append(df.iloc[i[0]].id_x)
    print(ids)
    return ids    
    
recommend(17)