#!/usr/bin/env python
# coding: utf-8

# converting .ipynb to .py

# In[1]:


get_ipython().system(' pip install nbconvert')

# In[2]:


pip install jupyter_contrib_nbextensions


# In[3]:


get_ipython().system('jupyter nbconvert --to script template.ipynb')









