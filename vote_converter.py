import csv

new_rows = []

downgrade = ["paranormal", "vampire", "urban fantasy", "chick lit", "dragon", "christian"]

with open('books.csv', 'rb') as f:
    reader = csv.reader(f)
    for id, title, author, rating, votes, language, genre, description in reader:
        for item in downgrade:
            if "christian" in genre.lower():
                if int(votes) > 100000:
                    print "{0}  --  {1}".format(title, votes)
                    votes = int(votes)/5
                    break
        if "classics" in genre.lower():
            votes = int(votes)*2
        new_rows.append([int(id), title, author, int(rating), votes, language, genre, description])

#with open('books2.csv', 'wb') as g:
#    writer = csv.writer(g)
#    writer.writerows(new_rows)