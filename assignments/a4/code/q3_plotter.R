library(ggplot2)
library(reshape2)
library(RColorBrewer)

metrics_all <- c('ndcg','R.prec','P500','ndcg5','ndcg1000','P30','ndcg10','p','P100','ndcg200','P10','ndcg30','P20','P5','ndcg100','ndcg20','P1000','P200','map','r','recip_rank','ndcg500')
metrics <- c('ndcg','R.prec','ndcg5','ndcg10','P10','P5','map')
scores <- read.csv('output_files/q3_rcompare_requested10.csv')
scores <- melt(scores,id.vars = c('q'), measure.vars = metrics)
ggplot(scores,aes(q,value,color=variable)) +geom_line(alpha = 0.3) +  geom_smooth(se=F) + labs(x = "Query", y='Score',color='Metric')

ggsave('images/q3_plot.png')

metrics <- c('ndcg','R.prec','ndcg20','P20','map')
scores <- read.csv('output_files/q3_rcompare_requested20.csv')
scores <- melt(scores,id.vars = c('q'), measure.vars = metrics)
ggplot(scores,aes(q,value,color=variable)) +geom_line(alpha = 0.3) +  geom_smooth(se=F) + labs(x = "Query", y='Score',color='Metric')
ggsave('images/q3_plot_r20.png')

metrics <- c('ndcg','R.prec','ndcg100','P100','map')
scores <- read.csv('output_files/q3_rcompare_requested100.csv')
scores <- melt(scores,id.vars = c('q'), measure.vars = metrics)
ggplot(scores,aes(q,value,color=variable)) +geom_line(alpha = 0.3) +  geom_smooth(se=F) + labs(x = "Query", y='Score',color='Metric')
ggsave('images/q3_plot_r100.png')

rel_count <-  read.csv('output_files/reldocs_count.csv')

out <- capture.output(xtable::xtable(subset(rel_count,count >= 10)))
cat(out, file="output_files/gt_10_table.txt", sep="\n", append=TRUE)