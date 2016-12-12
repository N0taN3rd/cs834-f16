from collections import defaultdict
from random import sample
import numpy as np
import pandas as pd
import os
from q2_helpers import get_review_df, get_reviewer_sim, get_movies_df
from util import dump_pickle, read_pickle

review_file_pickle = 'pickled/movies_predicted_%s_%d.pickle'
review_file_rated_pickle = 'pickled/movies_predicted_rated_%s_%d.pickle'


def pick_knn(user_sim, method='pearson_seq', k=10):
    sims = user_sim[user_sim.sim_method == method][np.isfinite(user_sim.sim)].sort_values(by=['sim'])
    return sims.tail(k)


def predict_rated(method='pearson_seq', k=10):
    want = review_file_rated_pickle % (method, k)
    if not os.path.exists(want):
        user_predictions = defaultdict(dict)
        review_df = get_review_df()
        reviewer_sims = get_reviewer_sim(review_df)
        movies = get_movies_df()
        # print(reviewer_sims)
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

            def neighbor_sum(neighbors_for_movie):
                acum = []
                for idx, row in neighbors_for_movie.iterrows():
                    neighbor_who_did_id = row['user_id']
                    neighbor_who_did_rating = row['rating']
                    neighbor_who_did_mean_rating = review_df[review_df.user_id == neighbor_who_did_id].rating.mean()
                    neighbor_who_did_sim_to_cur_u = knn[knn.other_user == neighbor_who_did_id].sim.iat[0]
                    acum.append(
                        neighbor_who_did_sim_to_cur_u * (neighbor_who_did_rating - neighbor_who_did_mean_rating))
                return np.sum(acum)

            for neighbor_review_id in neighbor_reviewed_ids:
                movie_reviewed = reviewed_same[reviewed_same.item_id == neighbor_review_id]
                movie_reviewed_title = movies[movies.movie_id.isin(movie_reviewed.item_id)].movie_title.iat[0]
                # print('User %s did not review %s' % (user, movie_not_reviewed_title))
                sum_neighbors = \
                    neighbors[neighbors.item_id == neighbor_review_id].groupby('user_id').apply(neighbor_sum).iat[0]
                predicted_score = user_mean + (sum_user * sum_neighbors)
                user_predictions[user][movie_reviewed_title] = predicted_score
                # print('According to the neighbors reviews this user would have rated it %.2f' % predicted_score)
        dump_pickle(user_predictions, want)
        return user_predictions
    else:
        return read_pickle(want)


def predict(method='pearson_seq', k=10):
    want = review_file_pickle % (method, k)
    if not os.path.exists(want):
        user_predictions = defaultdict(dict)
        review_df = get_review_df()
        reviewer_sims = get_reviewer_sim(review_df)
        movies = get_movies_df()
        # print(reviewer_sims)
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

            def neighbor_sum(neighbors_for_movie):
                acum = []
                for idx, row in neighbors_for_movie.iterrows():
                    neighbor_who_did_id = row['user_id']
                    neighbor_who_did_rating = row['rating']
                    neighbor_who_did_mean_rating = review_df[review_df.user_id == neighbor_who_did_id].rating.mean()
                    neighbor_who_did_sim_to_cur_u = knn[knn.other_user == neighbor_who_did_id].sim.iat[0]
                    acum.append(
                        neighbor_who_did_sim_to_cur_u * (neighbor_who_did_rating - neighbor_who_did_mean_rating))
                return np.sum(acum)

            for neighbor_review_id in neighbor_reviewed_ids:
                movie_not_reviewed = not_reviewed[not_reviewed.item_id == neighbor_review_id]
                movie_not_reviewed_title = movies[movies.movie_id.isin(movie_not_reviewed.item_id)].movie_title.iat[0]
                # print('User %s did not review %s' % (user, movie_not_reviewed_title))
                sum_neighbors = \
                    neighbors[neighbors.item_id == neighbor_review_id].groupby('user_id').apply(neighbor_sum).iat[0]
                predicted_score = user_mean + (sum_user * sum_neighbors)
                user_predictions[user][movie_not_reviewed_title] = predicted_score
                # print('According to the neighbors reviews this user would have rated it %.2f' % predicted_score)
        dump_pickle(user_predictions, want)
        return user_predictions
    else:
        return read_pickle(want)


if __name__ == '__main__':
    predict_rated()
    predict_rated(method='euclid')
        #
        #
        # a = u_mean + (1 / knn.sim.sum())
        # b = u_review.rating - u_mean
        # for nsim in knn.sim:
        #     for it in b:
        #         print(nsim * it)
        # print()
        # print('----------------------------------------')
        # print(u_sim)
