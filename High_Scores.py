import os

class HighScores:
    def __init__(self, filename="highscores.txt"):
        self.filename = filename
        self.scores = self.load_scores()

    def load_scores(self):
        scores = []
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.rsplit(" - ", 1)
                    if len(parts) == 2:
                        name, score_str = parts
                        try:
                            score = int(score_str)
                            scores.append((name, score))
                        except ValueError:
                            pass
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def save_scores(self):
        with open(self.filename, "w") as file:
            for name, score in self.scores:
                file.write(f"{name} - {score}\n")

    def add_score(self, name, score):
        self.scores.append((name, score))
        self.scores.sort(key=lambda x: x[1], reverse=True)
        self.scores = self.scores[:10]
        self.save_scores()

    def display_scores(self, screen, font):
        y = 200
        for i, (name, score) in enumerate(self.scores[:5]):
            text = font.render(f"{i+1}. {name} - {score}", True, (255, 255, 255))
            screen.blit(text, (250, y))
            y += 40