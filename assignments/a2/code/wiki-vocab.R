library(ggplot2)
library(RColorBrewer)
library(scales)

small <- function() {
  wsv <- read.csv('output_files/wsmall-vocab.csv')
  wsvb  <- read.csv('output_files/wsmall-vocabB.csv')
  wsvr  <- read.csv('output_files/wsmall-vocabR.csv')
  wsvb$c <- rep(c('Actual'),length(wsvb$wc))
  wsv$c <- rep(c('Actual'),length(wsv$wc))
  wsvr$c <- rep(c('Actual'),length(wsvr$wc))

  wsvNLS <- nls(vc ~ K * wc ^ B,data = wsv)
  wsvBNLS <- nls(vc ~ K * wc ^ B,data = wsvb)
  wsvRNLS <- nls(vc ~ K * wc ^ B,data = wsvr)
  ggplot(wsv,aes(x = wc, y = vc)) + 
    geom_line(aes(colour=c)) + 
    geom_line(data=data.frame(x=wsv$wc,y=predict(wsvNLS),c=rep(c('Heaps'),length(wsv$wc))),aes(x,y,colour=c)) + 
    scale_x_continuous(breaks =c(1,1000000, 2000000,3000000, 4100000),labels = comma) +
    scale_y_continuous(breaks = c(1,50000,100000,150000,200000,235000),labels = comma) +
    scale_colour_brewer('Vocab Growth',palette='Dark2') +
    labs(title='Vocabulary Wiki Small',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiSmallVG2.png')
  ggplot(wsvb,aes(x = wc, y = vc)) + 
    geom_line(aes(colour=c)) + 
    geom_line(data=data.frame(x=wsvb$wc,y=predict(wsvBNLS),c=rep(c('Heaps'),length(wsvb$wc))),aes(x,y,colour=c)) + 
    scale_x_continuous(breaks =c(1,1000000, 2000000,3000000, 4100000),labels = comma) +
    scale_y_continuous(breaks = c(1,50000,100000,150000,200000,235000),labels = comma) +
    scale_colour_brewer('Vocab Growth',palette='Dark2') +
    labs(title='Vocab Wiki Small Backwards',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiSmallVGB2.png')
  ggplot(wsvr,aes(x = wc, y = vc)) + 
    geom_line(aes(colour=c)) + 
    geom_line(data=data.frame(x=wsvr$wc,y=predict(wsvRNLS),c=rep(c('Heaps'),length(wsvr$wc))),aes(x,y,colour=c)) + 
    scale_x_continuous(breaks =c(1,1000000, 2000000,3000000, 4100000),labels = comma) +
    scale_y_continuous(breaks = c(1,50000,100000,150000,200000,235000),labels = comma) +
    scale_colour_brewer('Vocab Growth',palette='Dark2') +
    labs(title='Vocab Wiki Small Random',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiSmallVR2.png')
}

large <- function() {
  wsv <- read.csv('output_files/wlarge-vocab.csv')
  wsvb  <- read.csv('output_files/wlarge-vocabB.csv')
  wsvr  <- read.csv('output_files/wlarge-vocabR.csv')
  wsvb$c <- rep(c('Actual'),length(wsvb$wc))
  wsv$c <- rep(c('Actual'),length(wsv$wc))
  wsvr$c <- rep(c('Actual'),length(wsvr$wc))

  wsvNLS <- nls(vc ~ K * wc ^ B,data = wsv)
  wsvBNLS <- nls(vc ~ K * wc ^ B,data = wsvb)
  wsvRNLS <- nls(vc ~ K * wc ^ B,data = wsvr)
  ggplot(wsv,aes(x = wc, y = vc)) +
    geom_line(aes(colour=c)) + 
    geom_line(data=data.frame(x=wsv$wc,y=predict(wsvNLS),c=rep(c('Heaps'),length(wsv$wc))),aes(x,y,colour=c)) + 
    scale_x_continuous(breaks =c(1,2e+07, 4e+07, 6e+07, 8.3e+07),labels = comma) +
    scale_y_continuous(breaks = c(1,400000,  800000, 1200000, 1530000),labels = comma) +
    scale_colour_brewer('Vocab Growth',palette='Dark2') +
    labs(title='Vocab Wiki Large',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiLargeVG2.png')
  ggplot(wsvb,aes(x = wc, y = vc)) +
    geom_line(aes(colour=c)) + 
    geom_line(data=data.frame(x=wsvb$wc,y=predict(wsvBNLS),c=rep(c('Heaps'),length(wsvb$wc))),aes(x,y,colour=c)) +
    scale_x_continuous(breaks =c(1,2e+07, 4e+07, 6e+07, 8.3e+07),labels = comma) +
    scale_y_continuous(breaks = c(1,400000,  800000, 1200000, 1530000),labels = comma) +
    scale_colour_brewer('Vocab Growth',palette='Dark2') +
    labs(title='Vocab Wiki Large Backwards',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiLargeVGB2.png')
  ggplot(wsvr,aes(x = wc, y = vc)) +
    geom_line(aes(colour=c)) + 
    geom_line(data=data.frame(x=wsvr$wc,y=predict(wsvRNLS),c=rep(c('Heaps'),length(wsvr$wc))),aes(x,y,colour=c)) + 
    scale_x_continuous(breaks =c(1,2e+07, 4e+07, 6e+07, 8.3e+07),labels = comma) +
    scale_y_continuous(breaks = c(1,400000,  800000, 1200000, 1530000),labels = comma) +
    scale_colour_brewer('Vocab Growth',palette='Dark2') +
    labs(title='Vocab Wiki Large Random',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiLargeVGR2.png')
}

small()
large()
