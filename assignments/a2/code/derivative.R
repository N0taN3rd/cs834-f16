library(Ryacas)
k <- Sym("k")
n <- Sym("n")
c <- Sym("c")
p <- Sym("p")

dc <- deriv((k*n/c)+(p*c/2),c)
PrettyForm(dc)
TeXForm(dc)
