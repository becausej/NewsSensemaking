#!/usr/bin/env python
# coding: utf-8

# jupyter nbconvert --to script 'ProjectTesting.ipynb

# In[1]:


import newspaper

url = "https://www.cnn.com/2024/10/29/politics/christianity-wrestling-trump-analysis/index.html"

article = newspaper.article(url)

text = article.text


with open('out.txt', 'w') as f:
    print(article.text, file=f)  


article.nlp()

print(article.keywords)

print(article.summary)


# In[ ]:




