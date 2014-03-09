import BioTK.io.Treebank as Treebank 
from BioTK.text import HMMTagger

def test_train_hmm_tagger():
    trees = Treebank.fetch("GENIA")
    tagger = HMMTagger.train(trees)
    tokens = [t.word for t in trees[0].tokens]
    tokens = "Colorless green ideas sleep furiously .".split()
    predicted_tags = tagger.predict(tokens)
