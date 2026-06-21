import random
import os

class MarkovChain:
    def __init__(self):
        self.model = {}
        self.starts = []
        self._rebuild()

    def _rebuild(self):
        self.model = {}
        self.starts = []
        words = []
        for fname in ['train.txt', 'learned.txt']:
            if os.path.exists(fname):
                with open(fname, 'r', encoding='utf-8') as f:
                    words.extend(f.read().split())

        for i in range(len(words) - 1):
            current = words[i]
            next_word = words[i + 1]
            if current not in self.model:
                self.model[current] = []
            self.model[current].append(next_word)
        self.starts = list(set(words)) if words else []

    def learn(self, text):
        text = text.strip().lower()
        if not text or len(text) > 100:
            return
        with open('learned.txt', 'a', encoding='utf-8') as f:
            f.write(text + '\n')
        self._rebuild()

    def generate(self, max_words=20):
        if not self.model:
            return "..."
        word = random.choice(self.starts)
        result = [word]
        for _ in range(max_words - 1):
            if word not in self.model or not self.model[word]:
                break
            word = random.choice(self.model[word])
            result.append(word)
            if word in ('.', '!', '?') or random.random() < 0.2:
                break
        return ' '.join(result)
