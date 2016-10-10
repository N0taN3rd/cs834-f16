library(ggplot2)
library(scales)
library(gridExtra)
library(RColorBrewer)

colors <- brewer.pal(3, 'Dark2')

skip_distance1  <- function(c, k = 4, n = 1000000, p = 1000) { (k * n / c) + (p * c / 2) }
skip_distance2 <- function(c, k = 4,n = 1000000, p = 10000) {  (k * n / c) + (p * c / 2) }

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
  labs(title='Skip Distance P=1000 & P=10000',x = 'C Values', y = 'Skip Distance')
 


skip_distanceD <- function(c,k = 4, n = 1000000, p = 1000) {p/2 - k * n/c^2}
skip_distanceD2 <- function(c,k = 4, n = 1000000, p = 10000) {p/2 - k * n/c^2}

xd <- c(1:100)
sdD <- data.frame(
  x = c(xd,xd),
  y = c(
    sapply(xd,skip_distanceD),
    sapply(xd,skip_distanceD2)
  ),
  P = c(
    rep(c('1000'),100),
    rep(c('10000'),100)
  )
)

ggplot(sdD, aes(x,y)) +
  scale_y_continuous(labels = comma) +
  geom_point(aes(colour = P),position = position_jitter(width = 0.5, height = 0.5)) +
  scale_colour_brewer('P=',palette='Dark2') +
  labs(title='Skip Distance P=1000 & P=10000',x = 'C Values', y = 'Skip Distance')

skipd1 <- ggplot(data.frame(x = c(0:50),y=sapply(c(0:50), skip_distanceD))) + 
  geom_point(aes(x,y)) +
  scale_y_continuous(labels = comma) +
  labs(title='P=1000',x=element_blank(),y=element_blank())

skipd2 <- ggplot(data.frame(x = c(0, 100)), aes(x)) +
  stat_function(fun = skip_distanceD2, colour = colors[2]) +
  scale_y_continuous(labels = comma) +
  labs(title='P=10000',x=element_blank(),y=element_blank())

bothd <- ggplot(data.frame(x = c(0, 200)), aes(x)) +
  stat_function(fun = skip_distanceD, colour = colors[1]) +
  stat_function(fun = skip_distanceD2, colour = colors[2]) +
  scale_y_continuous(labels = comma) +
  labs(title='Both Derivative Plots',x = 'C', y = 'Skip Distance')

grid.arrange(bothd, arrangeGrob(skipd1, skipd2), ncol = 2)

sddf <- data.frame(x = c(10:50),y=sapply(c(0:50), skip_distanceD))
coef(lm(x ~ y, data = sddf))
ggplot(sddf) + 
  geom_point(aes(x,y),colour = colors[1]) + 
  geom_abline(intercept = 37, slope = -5)

