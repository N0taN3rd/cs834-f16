library(network)
library(sna)
library(ggplot2)
library(ggnet)
library(ggrepel)

names <- c('1','2','3','4','5','6','7')
adjm <- read.table('data/adjm.txt',row.names = names,col.names=names,check.names=FALSE)
net <- as.network(as.matrix(adjm), directed = TRUE, loops = FALSE, matrix.type = 'adjacency')
gplot <- ggnet2(net,label=T,arrow.size = 12, arrow.gap = 0.025) 

score_labeler <- function(df) {
  it = c()
  for(i in 1:length(df$hs)) {
    hs <- paste('HubScore:',df$hs[i])
    as <- paste('AuthorityScore:',df$as[i])
    pr <- paste('PageRank:',df$pr[i])
    it <- c(it,paste(hs,as,pr,sep = '\n'))
  }
  it
}

for(i in 1:5) {
  iter <- read.csv(paste('output_files/q1_iteration',i,'.csv',sep=''))
  score_labeles <- data.frame(
    x = gplot$data$x,
    y = gplot$data$y,
    labels = score_labeler(iter)
  )
  gplot + labs(title=paste('Iteration',i)) +
    geom_label_repel(data=score_labeles,aes(x,y,label=labels), box.padding = unit(0.5, 'lines'), point.padding = unit(2.6, 'lines'))
  ggsave(paste('images/','q1_iteration',i,'.png',sep=''))
}


