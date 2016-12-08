library(ggplot2)
library(reshape2)
library(RColorBrewer)

colors <- c('#1B9E77','#D95F02','#7570B3','#66A61E','#E6AB02','#A6761D','#666666')
scores <- melt(read.csv('output_files/q2_all_rel.csv'),id.vars = c('q'), measure.vars = c('MAP', 'R.Prec', 'NDCG5', 'NDCG10', 'P10'))
ggplot(scores,aes(q,value,color=variable)) + geom_line() + scale_color_manual(values=colors) + labs(x = 'Query', y='Score',color='Metric')

ggsave('images/q2_plot.png')

# extra 
metrics <- c('p','r')
scores <- read.csv('output_files/q3_rcompare_requested10.csv')
scores <- melt(scores,id.vars = c('q'), measure.vars = metrics)
ggplot(scores,aes(q,value,color=variable)) + geom_line() + 
  scale_color_manual(values=colors,name ='Metric',breaks=c('p', 'r'),labels=c('Precision', 'Recall')) + 
  labs(x = 'Query', y='Score',color='Metric')

ggsave('images/q2_plot_rp.png')

rel_count <-  read.csv('output_files/reldocs_count.csv')
ggplot(rel_count,aes(q,count)) + geom_line() + 
  labs(x = 'Query', y='Relevant Document Count Per Query',color='Metric')

ggsave('images/q2_plot_rc.png')