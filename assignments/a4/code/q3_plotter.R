library(ggplot2)
library(reshape2)
library(RColorBrewer)

metrics_all <- c('ndcg','R.prec','P500','ndcg5','ndcg1000','P30','ndcg10','p','P100','ndcg200','P10','ndcg30','P20','P5','ndcg100','ndcg20','P1000','P200','map','r','recip_rank','ndcg500')
metrics <- c('ndcg','R.prec','ndcg5','ndcg10','P10','P5','map')
scores <- read.csv('output_files/q3_rcompare_requested10.csv')
scores <- melt(scores,id.vars = c('q'), measure.vars = metrics)
ggplot(scores,aes(q,value,color=variable)) +geom_line(alpha = 0.3) +  geom_smooth(se=F) + labs(x = "Query", y='Score',color='Metric')

ggsave('images/q3_plot.png')