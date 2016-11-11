library(scales)
library(ggplot2)
library(RColorBrewer)

names <- c('Lancaster','PorterStemmer','SnowballStemmer','WordNetLemmatizer')
for(name in names) {
  lc <- read.csv(paste('output_files/window50/',name,'_stemclass_connected.csv',sep = ''))
  lsc <- read.csv(paste('output_files/window50/',name,'_stemclass_sconnected.csv',sep = ''))
  lsc$graph <- 'strong'
  lc$graph <- 'connected'
  ggplot(lsc,aes(sizeClass,count,shape=graph)) + 
    geom_jitter(aes(color=covers,shape=graph,height = .005)) + 
    geom_jitter(data=lc,aes(sizeClass,count,color=covers,height = .005)) +
    scale_y_continuous(breaks = pretty_breaks(n=5,min.n=4),expand=c(0.01, 0.25))+
  scale_color_brewer(palette = 'BrBG') + theme(legend.position="bottom") + guides(col = guide_legend(ncol = 2, byrow = TRUE))
  ggsave(paste(name,'connected.png',sep=''))
}