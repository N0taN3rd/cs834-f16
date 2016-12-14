import numpy as np
import math
import pandas as pd
import os
from collections import defaultdict
from contextClasses import AutoSaveCsv
from q2_helpers import get_review_df, get_reviewer_sim, get_movies_df
from util import dump_pickle, read_pickle

review_file_pickle = 'pickled/movies_predicted_%s_%d.pickle'
review_file_mean_pickle = 'pickled/movies_predicted_%s_%d.pickle'
review_file_rated_pickle = 'pickled/movies_predicted_rated_%s_%d.pickle'
review_file_rated_mean_pickle = 'pickled/movies_predicted_rated_%s_%d.pickle'

user_pred_rate_csv = 'output_files/user_pred_rated_%s_%d.csv'
user_pred_rate2_csv = 'output_files/user_pred_rated2_%s_%d.csv'
user_pred_rate_mse_csv = 'output_files/user_pred_rated_mse_%s_%d.csv'
user_pred_rate_mse2_csv = 'output_files/user_pred_rated_mse2_%s_%d.csv'


class UserReviewedPred(dict):
    def __missing__(self, key):
        res = self[key] = {}
        return res

    def add_movie(self, mid, mtitle, pred, act):
        self[mid]['mtile'] = mtitle
        self[mid]['pred'] = pred
        self[mid]['act'] = act


class UserPred(dict):
    def __missing__(self, key):
        res = self[key] = {}
        return res

    def add_movie(self, mid, mtitle, pred):
        self[mid]['mtile'] = mtitle
        self[mid]['pred'] = pred


def pick_knn(user_sim, method='pearson_seq', k=10):
    sims = user_sim[user_sim.sim_method == method][np.isfinite(user_sim.sim)].sort_values(by=['sim'])
    return sims.tail(k)


def predict_rated(method='pearson_seq', k=10):
    want = review_file_rated_pickle % (method, k)
    if not os.path.exists(want):
        user_predictions = defaultdict(UserReviewedPred)
        review_df = get_review_df()
        reviewer_sims = get_reviewer_sim(review_df)
        movies = get_movies_df()
        users = review_df.user_id.sort_values().unique()
        for user in users:
            user_reviews = review_df[review_df.user_id == user]
            similar_to_user = reviewer_sims[reviewer_sims.user == user]
            knn = pick_knn(similar_to_user, method=method, k=k)
            user_mean = user_reviews.rating.mean()
            sum_user = 1 / knn.sim.sum()
            neighbors = review_df[review_df.user_id.isin(knn.other_user.unique())]
            reviewed_same = neighbors[neighbors.item_id.isin(user_reviews.item_id)]
            neighbor_reviewed_ids = reviewed_same.item_id.unique()
            for neighbor_review_id in neighbor_reviewed_ids:
                movie_reviewed = reviewed_same[reviewed_same.item_id == neighbor_review_id]
                the_movie = movies[movies.movie_id.isin(movie_reviewed.item_id)]
                movie_reviewed_title = the_movie.movie_title.iat[0]
                neighbor_reviews = neighbors[neighbors.item_id == neighbor_review_id]
                acum = []
                for _, row in neighbor_reviews.iterrows():
                    neighbor_who_did_id = row['user_id']
                    neighbor_who_did_rating = row['rating']
                    neighbor_who_did_mean_rating = review_df[review_df.user_id == neighbor_who_did_id].rating.mean()
                    neighbor_who_did_sim_to_cur_u = knn[knn.other_user == neighbor_who_did_id].sim.iat[0]
                    acum.append(
                        neighbor_who_did_sim_to_cur_u * (neighbor_who_did_rating - neighbor_who_did_mean_rating))
                sum_neighbors = sum(acum)
                predicted_score = user_mean + (sum_user * sum_neighbors)
                the_movie_id = the_movie.movie_id.iat[0]
                actual_r = user_reviews[user_reviews.item_id == the_movie_id].rating.iat[0]
                user_predictions[user].add_movie(the_movie_id, movie_reviewed_title, predicted_score, actual_r)
        dump_pickle(user_predictions, want)
        return user_predictions
    else:
        return read_pickle(want)


def predict(method='pearson_seq', k=10):
    want = review_file_pickle % (method, k)
    if os.path.exists(want):
        user_predictions = defaultdict(UserPred)
        review_df = get_review_df()
        reviewer_sims = get_reviewer_sim(review_df)
        movies = get_movies_df()
        users = review_df.user_id.sort_values().unique()
        for user in users:
            user_reviews = review_df[review_df.user_id == user]
            similar_to_user = reviewer_sims[reviewer_sims.user == user]
            knn = pick_knn(similar_to_user, method=method, k=k)
            user_mean = user_reviews.rating.mean()
            sum_user = 1 / knn.sim.sum()
            neighbors = review_df[review_df.user_id.isin(knn.other_user.unique())]
            not_reviewed = neighbors[~neighbors.item_id.isin(user_reviews.item_id)]
            neighbor_reviewed_ids = not_reviewed.item_id.unique()
            for neighbor_review_id in neighbor_reviewed_ids:
                movie_not_reviewed = not_reviewed[not_reviewed.item_id == neighbor_review_id]
                the_movie_not_reviewed = movies[movies.movie_id.isin(movie_not_reviewed.item_id)]
                movie_not_reviewed_title = the_movie_not_reviewed.movie_title.iat[0]
                neighbor_reviews = neighbors[neighbors.item_id == neighbor_review_id]
                acum = []
                for _, row in neighbor_reviews.iterrows():
                    neighbor_who_did_id = row['user_id']
                    neighbor_who_did_rating = row['rating']
                    neighbor_who_did_mean_rating = review_df[review_df.user_id == neighbor_who_did_id].rating.mean()
                    neighbor_who_did_sim_to_cur_u = knn[knn.other_user == neighbor_who_did_id].sim.iat[0]
                    acum.append(
                        neighbor_who_did_sim_to_cur_u * (neighbor_who_did_rating - neighbor_who_did_mean_rating))
                sum_neighbors = sum(acum)
                predicted_score = user_mean + (sum_user * sum_neighbors)
                the_movie_id = the_movie_not_reviewed.movie_id.iat[0]
                user_predictions[user].add_movie(the_movie_id, movie_not_reviewed_title, predicted_score)
        dump_pickle(user_predictions, want)
        return user_predictions
    else:
        return read_pickle(want)


def gen_mse_prdr_csv(k=10):
    mse_headers = ['user', 'mse', 'which']
    pre_headers = ['user', 'mid', 'mtitle', 'score', 'which']
    preds_pearson = predict_rated(k=k)
    preds_euclid = predict_rated(method='euclid', k=k)
    want_euclid = user_pred_rate_csv % ('euclid', k)
    want_euclid_mse = user_pred_rate_mse_csv % ('euclid', k)
    want_pearson = user_pred_rate_csv % ('pearson', k)
    want_pearson_mse = user_pred_rate_mse_csv % ('pearson', k)
    if os.path.exists(want_euclid):
        with AutoSaveCsv(list, want_euclid_mse, mse_headers) as mseo, \
                AutoSaveCsv(list, want_euclid, pre_headers) as upe:
            for user, user_preds in preds_euclid.items():
                uprs_len = len(list(user_preds.values()))
                acum = []
                for mid, score in user_preds.items():
                    pred = score['pred']
                    act = score['act']
                    upe.append(
                        {'user': user, 'mid': mid, 'mtitle': score['mtile'], 'score': math.floor(pred),
                         'which': 'predicted'})
                    upe.append(
                        {'user': user, 'mid': mid, 'mtitle': score['mtile'], 'score': act,
                         'which': 'actual'})
                    acum.append((math.floor(pred) - act) ** 2)
                pma_sum = sum(acum)
                mse = ((1 / uprs_len) * pma_sum)
                mseo.append({'user': user, 'mse': mse, 'which': 'Euclidian'})
    if os.path.exists(want_pearson):
        with AutoSaveCsv(list, want_pearson_mse, mse_headers) as mseo, \
                AutoSaveCsv(list, want_pearson, pre_headers) as upe:
            for user, user_preds in preds_pearson.items():
                uprs_len = len(list(user_preds.values()))
                acum = []
                for mid, score in user_preds.items():
                    pred = score['pred']
                    act = score['act']
                    upe.append(
                        {'user': user, 'mid': mid, 'mtitle': score['mtile'], 'score': math.floor(pred),
                         'which': 'predicted'})
                    upe.append(
                        {'user': user, 'mid': mid, 'mtitle': score['mtile'], 'score': act,
                         'which': 'actual'})
                    acum.append((math.floor(pred) - act) ** 2)
                pma_sum = sum(acum)
                mse = ((1 / uprs_len) * pma_sum)
                mseo.append({'user': user, 'mse': mse, 'which': 'Pearson'})


if __name__ == '__main__':
    r_df = get_review_df()
    m_df = get_movies_df()
    rsim_df = get_reviewer_sim(r_df)
    gen_mse_prdr_csv()
