# MedFact

MedFact is a set of algorithms that help assign a veracity score to text paragraphs about medical claims.

Please cite the following [publication](http://dx.doi.org/10.1007/978-3-319-89656-4_9) when using our source code for your research. This project is supported by the [Alberta Machine Intelligence Institute (Amii)](http://amii.ca).

```
@inproceedings{SamuelZaiane2018,
  title = {{MedFact: Towards Improving Veracity of Medical Information in Social Media using Applied Machine Learning}},
  author = {Samuel, Hamman and Zaiane, Osmar},
  booktitle = {{31st CAIAC Canadian Conference on Artificial Intelligence (CAI)}},
  pages = {108--120},
  year = {2018},
  organization = {{CAIAC}}
}
```

## Prerequisites

- This code is developed in [Python 2.7.15](https://docs.python.org/2.7/) and tested on [Anaconda](https://www.anaconda.com/distribution/)
- The related Python libraries for this project can be installed via `pip install -r requirements.txt` (file generated via `pipreqs --savepath=requirements.txt .`)
- The datasets required in the `datasets` folder can be downloaded from [GDrive](https://drive.google.com/drive/folders/1LfIrmbMG-yyhaSM9wFGqCTDMLBF7ZSj9). 

## Datasets

- [Word2vec embeddings embeddings pre-trained on text from MEDLINE/PubMed Baseline 2018 by AUEB's NLP group](http://nlp.cs.aueb.gr)
- [Simple English Wikipedia (SEW)](http://pikes.fbk.eu/eval-sew.html)
- [Consumer Health Vocabulary (CHV)](https://github.com/Planeshifter/node-chvocab)
- [SNOMED CT International (requires UMLS account)](https://www.nlm.nih.gov/healthit/snomedct/international.html)
- [Medical Sciences Stack Exchange (scraped via API)](https://api.stackexchange.com/docs/questions)
- [Health Stack Exchange (outdated with inconsistencies)](https://archive.org/download/stackexchange)

## Workflow

1. Train the medical phrases classifier by running `train()` in `medclass.py` which will generate and persist the trained model
2. For a given incoming text paragraph, identify key phrases and medical phrases using `predict()` from `medclass.py`
3. Use the incoming medical phrases to query the TRIP database with `query()` to get related articles. Optionally, also query Health Canada's knowledge base using `query()` in `healthcanada.py`
4. Extract the corpus phrases from the TRIP (and optionally Health Canada) articles with `extract()` in `article.py`
5. Train the accord/agreement classifier via `train()` in `accordcnn.py`
6. Compare the incoming medical phrases with the corpus medical phrases via `predict()` in `accordcnn.py`
7. Calculate the veracity score via `veracity()` in `medfact.py`
8. Compute the confidence score via `confidence()` in `medfact.py`
9. Compute the triage label via `triage()` in `medfact.py`
10. Readability of the text being processed can be quantified with `metrics()` in `readability.py`

## Bulk Mode

- The veracity of websites can be computed via the batch mode which samples pages on the given website using a web crawler
- Pages to sample are arbitrarily selected from the site map, and the number of pages to sample can be configured for more coverage
- To use bulk mode for a specific website, use `bulk()` in `medfact.py`

## RESTful API

- The live [MedFact API](http://199.116.235.207) will be using IaaS hosting with [Cybera](http://www.cybera.ca)
- To run the Flask web app locally, use the command `python medfact.py api`
- In your web browser, go to [http://127.0.0.1:5000/api/](http://127.0.0.1:5000/api/)
- When using IaaS hosting, you can serve the Flask web app using [uWSGI](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04)
- PaaS hosting configurations depend on the provider, but here is one for [Heroku](https://medium.com/the-andela-way/deploying-a-python-flask-app-to-heroku-41250bda27d0)