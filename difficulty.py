import csv
from nltk.stem.wordnet import WordNetLemmatizer
from operator import itemgetter

lem = WordNetLemmatizer()

new_rows = []
stop = 0
white_list = "abcdefghijklmnopqrstuvwxyz01234567890' "
frequent_words = []

with open('frequent_words.csv', 'rb') as e:
    reader = csv.reader(e)
    for rank, word, part, frequency, dispersion in reader:
        word = word.lower()
        for char in word:
            if char not in white_list:
                word = word.replace(char, "")
        frequent_words.append(word)

def is_number(word):
    try:
        number = int(word)
        return True
    except:
        return False

def get_rank(the_list, item):
    if item in the_list:
        return the_list.index(item) + 1
    elif is_number(item):
        return 1
    else:
        return False

def judge_freq(lem, word, frequent_words):
    rank1 = get_rank(frequent_words, lem.lemmatize(word, 'n'))
    rank2 = get_rank(frequent_words, lem.lemmatize(word, 'v'))
    
    if rank1 and rank1 < rank2:
        return rank1
    else:
        return rank2

def rate_word(lem, word, frequent_words):
    length = len(word)
    rank = judge_freq(lem, word, frequent_words)
    if not rank:
        score = 6
    elif rank < 100:
        score = 0
    elif rank < 500:
        score = 1
    else:
        score = 3
    
    if length <= 6:
        score += 0
    elif length <= 9:
        score += 1
    elif length <= 13:
        score += 6
    else:
        score += 10
    return score

results_list = []

with open('books2.csv', 'rb') as f:
    reader = csv.reader(f)
    for id, title, author, rating, votes, language, genre, description in reader:
        if "english" not in language.lower():
            continue
        title_fixed = title.lower().replace("'s", "").replace("'re", "").replace("n't", "").replace("/", " ").replace("-", " ")
        for char in title_fixed:
            if char not in white_list:
                title_fixed = title_fixed.replace(char, "")
        title_list = title_fixed.strip().split()
        
        title_length = len(title_list)
        #title_lengths = [len(word) for word in title_list]
        #rare_words =  [word for word in title_list if word not in frequent_words]
        #rare_length = len(rare_words)
        
        scores_list = [rate_word(lem, word, frequent_words) for word in title_list]
        score = sum(scores_list)
        
        if title_length < 20:
            results_list.append([title, title_length, score, scores_list])

results_list.sort(key=itemgetter(2), reverse=True)

for title, length, score, scores_list in results_list[:20]:
        
        print "{0}  --  {1}".format(title, score)
        print "{0}".format(scores_list)
        print "---------------------------------"

#with open('books3.csv', 'wb') as g:
#    writer = csv.writer(g)
#    writer.writerows(new_rows)