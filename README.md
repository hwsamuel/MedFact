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

## Datasets

The following datasets are required in the `datasets` folder, and can be downloaded from [GDrive](https://drive.google.com/drive/folders/1LfIrmbMG-yyhaSM9wFGqCTDMLBF7ZSj9). Links to sources are provided for reference.

- [Word2vec embeddings embeddings pre-trained on text from MEDLINE/PubMed Baseline 2018 by AUEB's NLP group](http://nlp.cs.aueb.gr)
- [Simple English Wikipedia (SEW)](http://pikes.fbk.eu/eval-sew.html)
- [Consumer Health Vocabulary (CHV)](https://github.com/Planeshifter/node-chvocab)
- [SNOMED CT International (requires UMLS account)](https://www.nlm.nih.gov/healthit/snomedct/international.html)

## Workflow

1. For a given incoming text paragraph, identify key phrases using `tbd()` from `medclass.py`
2. From the set of key phrases, identify medical phrases using `predict()` from `medclass.py`
3. Use the incoming medical phrases to query the TRIP database with `query()`
4. Construct the facts corpus using the results via `tbd()` (both functions in `trip.py` )
5. Compare the incoming medical phrases with the corpus phrases to compute veracity metrics via `tbd()` in `tbd.py`

## Additional Resources

- Optionally also query Health Canada's knowledge base using `query()` and `tbd()` in `healthcanada.py` to build the facts corpus
- For websites, the workflow can be iteratively used to score each web page retrieved with web scraping
- The readability of the text being processed can also be judged via `metrics()` in `readability.py`

## Road Map

- RESTful API for calling MedFact via Python Flash application (hosted on Cybera)
- Retraining & refactoring supervised learning pipelines including PubMed word embeddings, medical words classifier, and agreement classifier
- Websites scraper for bulk mode website veracity ranking