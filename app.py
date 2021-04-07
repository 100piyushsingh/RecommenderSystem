import flask
import difflib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = flask.Flask(__name__, template_folder='templates')

df2 = pd.read_csv('./model/NetflixFlattened.csv')

binary_df = pd.DataFrame({'Index':df.index})
binary_df = binary_df.set_index('Index')

 
# Single Value
for i in single_col:
    for j in df[i].unique():
        binary_df[j] = 0
for i in range(len(df)):
    row = df.index[i]
    for j in single_col:
        value = df[j][row]
        binary_df.loc[row,value] = 1
        
# Multiple Value

for i in multi_col:
    unique_list = []
    for j in df[i]:
        for x in j:
            unique_list.append(x)
    unique_set = set(unique_list)
    
    for value in unique_set:
        binary_df[value] = 0 

for i in range(len(df)):
    row = df.index[i]
    for j in multi_col:
        for value in df[j][row]:
            binary_df.loc[row,value] = 1


# Compute the cosine similarity matrix
cosine_sim = linear_kernel(binary_df, binary_df)

# Construct a reverse map of indices and movie titles
indices = pd.Series(df.index, index=df['title']).drop_duplicates()          

def recommendation_engine(title):
    
    title = title.lower()
    row_index = indices[title]
    sim_scores = list(enumerate(cosine_sim[row_index]))
    sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse = True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return df.iloc[movie_indices]['title'].str.upper()

# Set up the main route
@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))
            
    if flask.request.method == 'POST':
        m_name = flask.request.form['movie_name']
        m_name = m_name.title()
#        check = difflib.get_close_matches(m_name,all_titles,cutout=0.50,n=1)
        if m_name not in all_titles:
            return(flask.render_template('negative.html',name=m_name))
        else:
            result_final = recommendation_engine(m_name)
            names = []
            #dates = []
            for i in range(len(result_final)):
                names.append(result_final.iloc[i])
                #dates.append(result_final.iloc[i][1])

            return flask.render_template('positive.html',movie_names=names,movie_date=dates,search_name=m_name)

if __name__ == '__main__':
    app.run()
