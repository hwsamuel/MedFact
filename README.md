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

For training the medical phrases identifier, you will need to download the following datasets into the `datasets` folder

- [Word2vec embeddings embeddings pre-trained on text from MEDLINE/PubMed Baseline 2018 by AUEB's NLP group](http://nlp.cs.aueb.gr)
- [Simple English Wikipedia (SEW)](http://pikes.fbk.eu/eval-sew.html)
- [Consumer Health Vocabulary (CHV)](https://github.com/Planeshifter/node-chvocab)
- [SNOMED CT International (requires UMLS account)](https://www.nlm.nih.gov/healthit/snomedct/international.html)

## Workflow

TBD