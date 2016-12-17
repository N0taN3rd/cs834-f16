library(ggplot2)
library(dplyr)
library(scales)
library(ggrepel)
library(RColorBrewer)

source('code/q2_plotter_helper.R')

euclid <- read.csv('output_files/user_pred_rated_euclid_10.csv')
ggplot(euclid,aes(mid)) + 
  geom_histogram(aes(fill=as.factor(score)),binwidth = 200) + 
  scale_fill_brewer('Scores',breaks = rev(levels(as.factor(euclid$score))),palette='Set3')  + 
  facet_wrap(~which,labeller = labeller(which = capitalize)) +
  labs(x = 'Movie Id Bin', y = 'Score Count')

ggsave('images/euclid_predicted_bmovie.png')

ggplot(euclid,aes(user)) + 
  geom_histogram(aes(fill=as.factor(score)),binwidth = 50) + 
  scale_fill_brewer('Scores',breaks = rev(levels(as.factor(euclid$score))),palette='Set3')  + 
  facet_wrap(~which,labeller = labeller(which = capitalize)) +
  labs(x = 'User Id Bin', y = 'Score Count')

ggsave('images/euclid_predicted_buser.png')

pearson <- read.csv('output_files/user_pred_rated_pearson_10.csv')
ggplot(pearson,aes(user)) + 
  geom_histogram(aes(fill=as.factor(score)),binwidth = 50) + 
  scale_fill_brewer('Scores',breaks = rev(levels(as.factor(euclid$score))),palette='Set3')  + 
  facet_wrap(~which,labeller = labeller(which = capitalize)) +
  labs(x = 'User Id Bin', y = 'Score Count')

ggsave('images/pearson_predicted_buser.png')

euclidMSE <- read.csv('output_files/user_pred_rated_mse_euclid_10.csv')
pearsonMSE <- read.csv('output_files/user_pred_rated_mse_pearson_10.csv')

ggplot() + 
  geom_line(data=euclidMSE,aes(user,mse)) +
  geom_smooth(data=euclidMSE,aes(user,mse)) +
  geom_line(data=pearsonMSE,aes(user,mse)) +
  geom_smooth(data=pearsonMSE,aes(user,mse)) +
  scale_y_continuous(limits = c(min_y(euclidMSE,pearsonMSE),max_y(euclidMSE,pearsonMSE)),breaks = seq(0,7,by=.5)) +
  scale_x_continuous(limits = c(min_x(euclidMSE,pearsonMSE),max_x(euclidMSE,pearsonMSE)+50),breaks = pretty_breaks(n=6)) +
  facet_wrap(~which) +
  labs(x='User',y='Mean Squared Error') 

ggsave('images/user_predicted_mse.png')
