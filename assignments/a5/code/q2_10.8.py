import multiprocessing
import numpy as np
import os
from util import read_pickle, dump_pickle
from collections import defaultdict
from movie_clazzes import get_movie_data
from math import sqrt

user_core_pickle = 'pickled/user_cor.pickle'


def pearson(rating_u1, rating_u2):
    if len(rating_u1) != len(rating_u2):
        raise Exception('U done goofed')
    length = len(rating_u1)
    mean_u1 = np.mean(rating_u1)
    mean_u2 = np.mean(rating_u2)
    numerator = sum([(rating_u1[i] - mean_u1) * (rating_u2[i] - mean_u2) for i in range(length)])
    denominator_u1 = sqrt(sum([(rating_u1[i] - mean_u1) ** 2 for i in range(length)]))
    denominator_u2 = sqrt(sum([(rating_u2[i] - mean_u2) ** 2 for i in range(length)]))
    if (denominator_u1 * denominator_u2) == 0:
        return 0
    correlation = numerator / (denominator_u1 * denominator_u2)
    return correlation


def cor_for_chunk(d):
    print('processing chunk %d' % d['chunk'])
    usr_cor = defaultdict(dict)
    for curUser, otherUsers in zip(d['users'], d['test']):
        for ouser in otherUsers:
            shared = curUser.reviewKeys & ouser.reviewKeys
            if len(shared) > 0:
                u1 = []
                u2 = []
                for sk in shared:
                    u1.append(curUser.reviews[sk].rating)
                    u2.append(ouser.reviews[sk].rating)
                cor = pearson(u1, u2)
                usr_cor[curUser.id][ouser.id] = cor
            else:
                usr_cor[curUser.id][ouser.id] = -1.0
    print('finished processing chunk %d' % d['chunk'])
    return usr_cor


def all_user_cor(usrs):
    if not os.path.exists(user_core_pickle):
        uids = set(usrs.keys())
        chunks = []
        temp = []
        tempu = []
        chunk_c = 1
        for uid in uids:
            test = uids.difference({uid})
            u = []
            for t in test:
                u.append(usrs[t])
            temp.append(u)
            tempu.append(usrs[uid])
            if len(temp) == 41:
                chunks.append({'chunk': chunk_c, 'test': list(temp), 'users': list(tempu)})
                chunk_c += 1
                temp.clear()
                tempu.clear()
        p = multiprocessing.Pool(4)
        ret = p.map(cor_for_chunk, chunks)
        all_cors = {}
        for it in ret:
            all_cors.update(it)
        dump_pickle(all_cors, user_core_pickle)
    else:
        all_cors = read_pickle(user_core_pickle)
    return all_cors


if __name__ == '__main__':
    users, reviews, movies = get_movie_data()
    user_cor = all_user_cor(users)
    print(len(list(user_cor.keys())))



# if length % i+1 == 0:
#     print(i)
# usr_compaired = defaultdict(set)
# usr_cor = defaultdict(dict)
# for uid in uids:
#     test = uids.difference({uid})
#     cur_user = users[uid]
#     for ouid in test:
#         usr_compaired[ouid].add(uid)
#         usr_compaired[uid].add(ouid)
#         ouser = users[ouid]
#         shared = cur_user.reviewKeys & ouser.reviewKeys
#         if len(shared) > 0:
#             u1 = []
#             u2 = []
#             for sk in shared:
#                 u1.append(cur_user.reviews[sk].rating)
#                 u2.append(ouser.reviews[sk].rating)
#             cor = pearson(u1, u2)
#             usr_cor[uid][ouid] = cor
#         else:
#             usr_cor[uid][ouid] = -1.0
# for user, cors in sorted(usr_cor.items(), key=lambda x: x[0]):
#     print(len(uids), len(cors.keys()))

# print(type(reviews))
# user_to_review = seq(reviews.values()).flat_map(lambda x:x).group_by(lambda review: review.uid).to_list()
# for it in user_to_review:
#     print(it)
