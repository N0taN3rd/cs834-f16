library(Ryacas)
library(numDeriv)
k <- Sym("k")
n <- Sym("n")
c <- Sym("c")
p <- Sym("p")

dc <- deriv((k*n/c)+(p*c/2),c)
TeXForm(dc)

func0 <- function(c){ (4*1000000)/c + (1000*c)/2 }
grad(func0, c(50:200))

func1 <- function(c){ (4*1000000)/c + (10000*c)/2 }
grad(func0, c(10:100))