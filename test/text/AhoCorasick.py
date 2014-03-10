from BioTK.text import AhoCorasick

def test():
    trie = AhoCorasick.Trie(case_sensitive=False)
    trie.add("he")
    trie.add("she")
    trie.add("hers")
    trie.build()

    text = "he She is hers friend"
    for m in trie.search(text):
        print(m.start, m.end)
        print(text[m.start:m.end])

test()
