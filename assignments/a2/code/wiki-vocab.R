library(ggplot2)
library(RColorBrewer)
library(scales)



small <- function() {
  colors <- brewer.pal(8, 'Dark2')
  wsv <- read.csv('output_files/wsmall-vocab.csv')
  wsvb  <- read.csv('output_files/wsmall-vocabB.csv')
  wsvr  <- read.csv('output_files/wsmall-vocabR.csv')
  
  wsvNLS <- nls(vc ~ K * wc ^ B,data = wsv)
  wsvBNLS <- nls(vc ~ K * wc ^ B,data = wsvb)
  wsvRNLS <- nls(vc ~ K * wc ^ B,data = wsvr)
  ggplot(wsv,aes(x = wc, y = vc)) + 
    geom_line(color=colors[1]) + 
    geom_line(data=data.frame(x=wsv$wc,y=predict(wsvNLS)),aes(x,y),color=colors[2]) + 
    scale_x_continuous(breaks =c(1,1e+06,2e+06,3e+06,4e+06,4.5e+06),labels = comma) +
    scale_y_continuous(breaks = c(1,50000,100000,150000,200000,250000),labels = comma) +
    labs(title='Vocabulary Growth Wiki Small',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiSmallVG.pdf')
  ggplot(wsvb,aes(x = wc, y = vc)) + 
    geom_line(color=colors[1]) + 
    geom_line(data=data.frame(x=wsvb$wc,y=predict(wsvBNLS)),aes(x,y),color=colors[2]) + 
    scale_x_continuous(breaks =c(1,1e+06,2e+06,3e+06,4e+06,4.5e+06),labels = comma) +
    scale_y_continuous(breaks = c(1,50000,100000,150000,200000,250000),labels = comma) +
    labs(title='Vocabulary Growth Wiki Small Backwards',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiSmallVGB.pdf')
  ggplot(wsvr,aes(x = wc, y = vc)) + 
    geom_line(color=colors[1]) + 
    geom_line(data=data.frame(x=wsvr$wc,y=predict(wsvRNLS)),aes(x,y),color=colors[2]) + 
    scale_x_continuous(breaks =c(1,1e+06,2e+06,3e+06,4e+06,4.5e+06),labels = comma) +
    scale_y_continuous(breaks = c(1,50000,100000,150000,200000,250000),labels = comma) +
    labs(title='Vocabulary Growth Wiki Small Random',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiSmallVR.pdf')
}

large <- function() {
  colors <- brewer.pal(8, 'Dark2')
  wsv <- read.csv('output_files/wlarge-vocab.csv')
  wsvb  <- read.csv('output_files/wlarge-vocabB.csv')
  wsvr  <- read.csv('output_files/wlarge-vocabR.csv')
  
  wsvNLS <- nls(vc ~ K * wc ^ B,data = wsv)
  wsvBNLS <- nls(vc ~ K * wc ^ B,data = wsvb)
  wsvRNLS <- nls(vc ~ K * wc ^ B,data = wsvr)
  ggplot(wsv,aes(x = wc, y = vc)) +
    geom_line(color=colors[1]) +
    geom_line(data=data.frame(x=wsv$wc,y=predict(wsvNLS)),aes(x,y),color=colors[2]) +
    scale_x_continuous(breaks =c(1,2e+07, 4e+07, 6e+07,  9e+07),labels = comma) +
    scale_y_continuous(breaks = c(1,200000,  400000,  600000,  800000, 1000000, 1200000, 1400000, 1650000),labels = comma) +
    labs(title='Vocabulary Growth Wiki Large',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiLargeVG.pdf')
  ggplot(wsvb,aes(x = wc, y = vc)) +
    geom_line(color=colors[1]) +
    geom_line(data=data.frame(x=wsvb$wc,y=predict(wsvBNLS)),aes(x,y),color=colors[2]) +
    scale_x_continuous(breaks =c(1,2e+07, 4e+07, 6e+07,  9e+07),labels = comma) +
    scale_y_continuous(breaks = c(1,200000,  400000,  600000,  800000, 1000000, 1200000, 1400000, 1650000),labels = comma) +
    labs(title='Vocabulary Growth Wiki Large Backwards',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiLargeVGB.pdf')
  ggplot(wsvr,aes(x = wc, y = vc)) +
    geom_line(color=colors[1]) +
    geom_line(data=data.frame(x=wsvr$wc,y=predict(wsvRNLS)),aes(x,y),color=colors[2]) +
    scale_x_continuous(breaks =c(1,2e+07, 4e+07, 6e+07,  9e+07),labels = comma) +
    scale_y_continuous(breaks = c(1,200000,  400000,  600000,  800000, 1000000, 1200000, 1400000, 1650000),labels = comma) +
    labs(title='Vocabulary Growth Wiki Large Random',x = 'Word Count', y = 'Vocab Count')
  ggsave('wikiLargeVGR.pdf')
}

small()
large()
