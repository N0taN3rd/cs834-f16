library(dplyr)
library(scales)
library(ggplot2)
library(RColorBrewer)


# Multiple plot function
#
# ggplot objects can be passed in ..., or to plotlist (as a list of ggplot objects)
# - cols:   Number of columns in layout
# - layout: A matrix specifying the layout. If present, 'cols' is ignored.
#
# If the layout is something like matrix(c(1,2,3,3), nrow=2, byrow=TRUE),
# then plot 1 will go in the upper left, 2 will go in the upper right, and
# 3 will go all the way across the bottom.
#
multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  library(grid)
  
  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)
  
  numPlots = length(plots)
  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }
  
  if (numPlots==1) {
    print(plots[[1]])
    
  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}

doplot <- function(df) {
  plots <- list()
  count <- 1
  for(l in levels(df$covers)) {
    print(l)
    plots[[count]] <- ggplot(df[df$covers == l,],aes(sizeClass,matches)) + 
      geom_point() +
      scale_y_continuous(breaks=pretty_breaks(n=4))+
      geom_jitter(height = 0.2) + labs(title = l)
    count <- count +1 
  }
  
  multiplot(plotlist = plots, cols = 2)
}

names <- c('Lancaster','PorterStemmer','SnowballStemmer','WordNetLemmatizer')
for(name in names) {
  lc <- read.csv(paste('/home/john/Documents/cs834-f16/assignments/a3/code/output_files/window50/',name,'_stemclass_connected.csv',sep = ''))
  lsc <- read.csv(paste('/home/john/Documents/cs834-f16/assignments/a3/code/output_files/window50/',name,'_stemclass_sconnected.csv',sep = ''))
  ggplot(lc,aes(sizeClass,count)) + 
    geom_jitter(aes(color=covers,shape=factor(matches)),height = .005) + 
    scale_color_brewer(palette = 'BrBG')  + theme(legend.position="bottom") + guides(col = guide_legend(ncol = 2, byrow = TRUE))
  ggsave(paste(name,'connected.png',sep=''))
  ggplot(lsc,aes(sizeClass,count)) + 
    geom_jitter(aes(color=covers,shape=factor(matches)),height = .005) + 
  scale_color_brewer(palette = 'BrBG') + theme(legend.position="bottom") + guides(col = guide_legend(ncol = 2, byrow = TRUE))
  ggsave(paste(name,'sconnected.png',sep=''))
  # png(paste(name,'connected.png',sep=''),width = 1000,height = 565)
  # doplot(lc)
  # dev.off()
  # png(paste(name,'sconnected.png',sep=''),width = 835,height = 565)
  # doplot(lsc)
  # dev.off()
  
}


display.brewer.all()
