library(ggplot2)
library(dplyr)
library(scales)
library(ggrepel)
library(RColorBrewer)

source('code/byte_formater.R')

wikiSizeVocab <- function() {
  sizes <- read.csv('output_files/wsmall_sizes.csv')
  plot <- sizes[sizes$new_size != -1,]
  ggplot(plot) +  geom_line(aes(idx,dif))  + annotate("text", x=3000, y=805000, label= paste(length(plot$idx),'files total'))+
    scale_y_continuous(limits = c(min(plot$dif),max(plot$dif)),breaks = pretty_breaks(n=7),labels = Kb) +
    labs(x='Wiki Small File',y='File Size Differnce From Live Web Version In Bytes',title='Wiki Small Files Whoes Live Web Counterpart Could Be Retrieved',color='none') 
  ggsave('images/wikismall_dif.png')
  
  plot2 <- sizes[sizes$new_size == -1,]
  ggplot(plot2) +  geom_line(aes(idx,old_size))  + annotate("text", x=5000, y=300000, label= paste(length(plot2$idx),'files total'))+
    scale_y_continuous(limits = c(min(plot2$old_size),max(plot2$old_size)),breaks = pretty_breaks(n=8),labels = Kb) +
    labs(x='Wiki Small File',y='File Size In Bytes',title='Wiki Small Files Whoes Live Web Counterpart Could Be Not Retrieved',color='none') 
  ggsave('images/wikismall_nolive.png')
  
  
  wsv <- read.csv('output_files/wsmall-vocab-combines.csv')
  wsvl <- wsv[wsv$which == 'Live Web',]
  wsvd <- wsv[wsv$which == 'Data Set',]
  ggplot() +  
    geom_line(data=wsvl,aes(x=wc,y=vc,color=which)) +
    geom_line(data=wsvd,aes(x=wc,y=vc,color=which)) +
    scale_x_continuous(limits = c(min(wsvl$wc),max(wsvl$wc)),breaks = pretty_breaks(n=7),labels = comma) +
    scale_y_continuous(limits = c(min(wsvl$vc),max(wsvl$vc)),breaks = pretty_breaks(n=6),labels = comma) +
    scale_colour_brewer('Vocab Growth',palette='Dark2') +
    labs(title='Vocabulary Wiki Small Live Web VS Data Set',x = 'Word Count', y = 'Vocab Count')
  ggsave('images/wikismall_vocab_compare.png')
}



