import re
import os
import codecs
from functional import seq
from contextClasses import SelectFromFile
from util import dump_pickle, read_pickle

user_file = 'data/ml-100k/u.user'
usr_review_file = 'data/ml-100k/u.data'
movie_f = 'data/ml-100k/u.item'

usr_pickle = 'pickled/movie_user.pickle'
usr_review_pickle = 'pickled/movie_user_review.pickle'
movie_pickle = 'pickled/movie_movies.pickle'

usr_split = re.compile('\\|')
usr_ratting = re.compile('\s+')
msanity = re.compile('[|]+')
msplit = re.compile('\\|')


class User:
    def __init__(self, splitted, reviews=None):
        self.id = int(splitted[0])
        self.age = int(splitted[1])
        self.gender = splitted[2]
        self.job = splitted[3]
        self.zcode = splitted[4]
        self.reviews = {}
        self.reviewKeys = set()
        if reviews is not None:
            for r in reviews.get(self.id, None):
                self.reviewKeys.add(r.itemid)
                self.reviews[r.itemid] = r

    def check(self, age, gender, job):
        if self.age == age:
            if self.gender == gender:
                if self.job == job:
                    return True
        return False

    def __str__(self):
        return "id: %d, age: %d, gender: %s, job: %s, reviewed: %d" % (
            self.id, self.age, self.gender, self.job, len(list(self.reviews.keys())))

    def __repr__(self):
        return self.__str__()


class URating:
    def __init__(self, split):
        self.uid = int(split[0])
        self.mname = None
        self.itemid = int(split[1])
        self.rating = int(split[2])
        self.tstamp = split[3]

    def __eq__(self, other):
        if not isinstance(other, URating):
            return False
        else:
            return self.uid == other.uid and self.itemid == other.itemid

    def __str__(self):
        return "uid: %d, itemid: %d, movie: %s, rating: %d, tstamp: %s" % (
            self.uid, self.itemid, self.mname, self.rating, self.tstamp)

    def __repr__(self):
        return self.__str__()


class Movie:
    def __init__(self, split):
        length = len(split)
        if length < 24:
            howMuch = 24 - length
            for _ in range(howMuch):
                split.append(0)
        self.mid = int(split[0])
        self.mtitle = split[1]
        self.rdate = split[2]
        self.vrdate = split[3]
        self.ibmdurl = split[4]
        self.unknown = int(split[5])
        self.action = int(split[6])
        self.adventure = int(split[7])
        self.animation = int(split[8])
        self.children = int(split[9])
        self.comedy = int(split[10])
        self.crime = int(split[11])
        self.documentary = int(split[12])
        self.drama = int(split[13])
        self.fantasy = int(split[14])
        self.filmnoir = int(split[15])
        self.horror = int(split[16])
        self.musical = int(split[17])
        self.mystery = int(split[18])
        self.romance = int(split[19])
        self.scifi = int(split[20])
        self.thriller = int(split[21])
        self.war = int(split[22])
        self.western = int(split[23])

    def __str__(self):
        return 'mid: %s, mtitle: %s' % (self.mid, self.mid)

    def __repr__(self):
        return self.__str__()


def get_users(reviews=None):
    if not os.path.exists(usr_pickle):
        def user_trans(lines):
            return map(lambda line: User(usr_split.split(line), reviews), lines)

        usrs = {}
        with SelectFromFile(user_file, transformer=user_trans, selector=lambda x: list(x)) as it:
            for u in it:
                usrs[u.id] = u
        dump_pickle(usrs, usr_pickle)
    else:
        usrs = read_pickle(usr_pickle)
    return usrs


def get_reviews(movie_map):
    if not os.path.exists(usr_review_pickle):
        def review_mapper(line):
            ur = URating(usr_ratting.split(line.rstrip()))
            ur.mname = movie_map.get(ur.itemid, None)
            return ur

        def trans(rvs):
            return seq(rvs).map(review_mapper).group_by(lambda ur: ur.uid).to_dict()

        with SelectFromFile(usr_review_file, transformer=trans, selector=lambda x: x) as r:
            reviews = r
        dump_pickle(reviews, usr_review_pickle)
    else:
        reviews = read_pickle(usr_review_pickle)

    return reviews


def get_movies():
    if not os.path.exists(movie_pickle):
        def move_clean_split(line):
            return Movie(msplit.split(msanity.sub('|', line.rstrip())))

        movie_map = {}
        with codecs.open(movie_f, 'r', encoding='utf-8', errors='replace') as movs:
            for mov in map(move_clean_split, movs):
                movie_map[mov.mid] = mov
        dump_pickle(movie_map, movie_pickle)
    else:
        movie_map = read_pickle(movie_pickle)
    return movie_map


def get_movie_data():
    movies = get_movies()
    reviews = get_reviews(movies)
    users = get_users(reviews)
    return users, reviews, movies
