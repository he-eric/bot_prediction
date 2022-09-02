import scattertext as st
import spacy
from pprint import pprint

# convention_df = st.SampleCorpora.ConventionData2012.get_data()
# nlp = spacy.load('en')
#
# corpus = st.CorpusFromPandas(convention_df,
#                                 category_col='party',
#                                 text_col='text',
#                                 nlp=nlp).build()
#
# html = st.produce_scattertext_explorer(corpus,
#                                         category='democrat',
#                                         category_name='Democratic',
#                                         not_category_name='Republican',
#                                         width_in_pixels=1000,
#                                         metadata=convention_df['speaker'])
#
# open("Convention-Visualization.html", 'wb').write(html.encode('utf-8'))
import json
import pandas as pd

print('Build df')
with open('data/troll_comments.txt') as json_file:
    troll_data = json.load(json_file)

with open('data/normie_comments1.txt') as json_file:
    normie_data = json.load(json_file)

# with open('data/normie_comments2.txt') as json_file:
#     normie_data2 = json.load(json_file)
#     for key in normie_data:
#         normie_data[key] += normie_data2

data = troll_data
for key in troll_data:
    data[key] += normie_data[key]

df = pd.DataFrame(data)
df = df.iloc[0:10000]

print('feat_builder')
feat_builder = st.FeatsFromOnlyEmpath()

print('empath_corpus')
empath_corpus = st.CorpusFromParsedDocuments(df,
                                            category_col='label',
                                            feats_from_spacy_doc=feat_builder,
                                            parsed_col='comments').build()

print('html')
html = st.produce_scattertext_explorer(empath_corpus,
                                category = '0',
                                category_name = 'Democratic',
                                not_category_name = 'Republican',
                                width_in_pixels = 1000,
                                metadata = df['user'],
                                use_non_text_features = True,
                                use_full_doc = True,
                                topic_model_term_lists = feat_builder.get_top_model_term_lists())

print('open')
open("Reddit-Trolls-Empath.html", 'wb').write(html.encode('utf-8'))