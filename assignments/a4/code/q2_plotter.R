library(ggplot2)
library(reshape2)
library(RColorBrewer)

colors <- c("#1B9E77","#D95F02","#7570B3","#66A61E","#E6AB02","#A6761D","#666666")
scores <- melt(read.csv('output_files/q2_all_rel.csv'),id.vars = c('q'), measure.vars = c('MAP', 'R.Prec', 'NDCG5', 'NDCG10', 'P10'))
ggplot(scores,aes(q,value,color=variable)) + geom_line() + scale_color_manual(values=colors) + labs(x = "Query", y='Score',color='Metric')

ggsave('images/q2_plot.png')

