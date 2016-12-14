library(network)
library(sna)
library(ggplot2)
library(ggnetwork)
library(ggnet)

names <- c('1','2','3','4','5','6','7')
adjm <- read.table('data/adjm.txt',row.names = names,col.names=names,check.names=FALSE)
iter <- read.csv(paste('output_files/q1_iteration',1,'.csv',sep=''))
net <- as.network(as.matrix(adjm), directed = TRUE, loops = FALSE, matrix.type = 'adjacency')

it = c()
for (i in 1:network.size(net)) {
  it <- c(it,'LETTERS[ vertex.names ]')
  set.vertex.attribute(net,'HubScore',iter$hs)
  set.vertex.attribute(net,'AuthorityScore',iter$as)
  set.vertex.attribute(net,'PageRank',iter$pr)
}

# https://briatte.github.io/ggnetwork/#geom_nodetext_repel-and-geom_nodelabel_repel

ggnet2(net,label=T,arrow.size = 12, arrow.gap = 0.025,label = c('HubScore PageRank')) 


# for(i in 1:5){
#   iter <- read.csv(paste('output_files/q1_iteration',i,'.csv',sep=''))
#   v_attr = list()
#   for(idx in 1:nrow(iter)) {
#     v_attr <- list(v_attr,as.numeric(iter[idx,]))
#   }
#   # apply(iter, 1, f)
#   print(v_attr)
#   net <- as.network(as.matrix(adjm), directed = TRUE, loops = FALSE, matrix.type = 'adjacency',vertex.attrnames=v_attr_names,vertex.attr=v_attr)
#   ggnet2(net,label=T,arrow.size = 12, arrow.gap = 0.025)
#   # print(unname(unlist(iter[,1])))
#  # print(lapply( split(iter,seq_along(iter[,1])), f2))
# }

