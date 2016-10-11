library(ggplot2)
library(ggrepel)
library(ggthemes)
library(scales)
library(gridExtra)
library(RColorBrewer)
library(numDeriv)

colors <- brewer.pal(3, 'Dark2')

skip_distance1  <- function(c) { ((4 * 1000000) / c) + ((1000 * c) / 2) }
skip_distance2 <- function(c) {  ((4 * 1000000) / c) + ((10000 * c) / 2) }

x1 <- c(1:1000)
sd <- data.frame(
  x = c(x1,x1),
  y = c(
    sapply(x1,skip_distance1),
    sapply(x1,skip_distance2)
  ),
  P = c(
    rep(c('1000'),1000),
    rep(c('10000'),1000)
  )
)

ggplot(sd, aes(x,y)) +
  scale_y_continuous(labels = comma) +
  geom_point(aes(colour = P),position = position_jitter(width = 0.5, height = 0.5)) +
  scale_colour_brewer('P=',palette='Dark2') +
  labs(title='Skip Distance P=1000 & P=10000',x = 'C Values', y = 'Function Values')

ggsave('skipDistanceBoth.png')
 
skip_distanceD <- function(c) {(1000/2) - ((4 * 1000000)/c^2)}
skip_distanceD2 <- function(c) {(10000/2) - ((4 * 1000000)/c^2)}

xd <- c(10:200)
skipD <- data.frame(
  x = xd,
  y = grad(skip_distance1,xd)
)

xd2 <-c(10:100)
skipD2 <- data.frame(
  x = xd2,
  y = grad(skip_distance2,xd2)
)

skd_maxX_zero <- max(skipD[skipD$y<=0,])
skd2_maxX_zero <- max(skipD2[skipD2$y<=0,])

skd_oc <- skipD[skipD$x == skd_maxX_zero,]
skd_oc2 <- skipD2[skipD2$x == skd2_maxX_zero,]

ggplot(skipD, aes(x,y)) +
  geom_point( data=skd_oc,colour =colors[1]) +
  geom_line(colour =colors[1]) +
  geom_text_repel(data=skd_oc,aes(label = paste('Optimal C Value =',x)),
                  size = 5,
                  fontface = 'bold',
                  box.padding = unit(1.5, 'lines'),
                  point.padding = unit(0.5, 'lines'),
                  segment.color = '#555555',
                  segment.size = 0.7,
                  arrow = arrow(length = unit(0.01, 'npc')),
                  force = 1,
                  max.iter = 2e3) +
  labs(title='Skip Distance Derivative P=1000',x = 'C Values', y = 'Derivative Function Values')
ggsave('skipDistanceD.png')
ggplot(skipD2, aes(x,y)) +
  geom_point( data=skd_oc2,colour =colors[2]) +
  geom_line(colour =colors[2]) +
  geom_text_repel(data=skd_oc2,aes(label = paste('Optimal C Value =',x)),
                  size = 5,
                  fontface = 'bold',
                  box.padding = unit(1.5, 'lines'),
                  point.padding = unit(0.5, 'lines'),
                  segment.color = '#555555',
                  segment.size = 0.7,
                  arrow = arrow(length = unit(0.01, 'npc')),
                  force = 1,
                  max.iter = 2e3) +
  labs(title='Skip Distance Derivative P=10000',x = 'C Values', y = 'Derivative Function Values')
ggsave('skipDistanceD2.png')



