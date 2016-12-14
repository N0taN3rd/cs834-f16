capitalize <- function(string) {
  substr(string, 1, 1) <- toupper(substr(string, 1, 1))
  string
}

min_y <- function(e,p) {
  emin <-  min(euclidMSE$mse)
  pmin <-  min(pearsonMSE$mse)
  if (emin < pmin) 
    emin
  else
    pmin
}

max_y <- function(e,p) {
  emin <-  max(euclidMSE$mse)
  pmin <-  max(pearsonMSE$mse)
  if (emin > pmin) 
    emin
  else
    pmin
}

min_x <- function(e,p) {
  emin <-  min(euclidMSE$user)
  pmin <-  min(pearsonMSE$user)
  if (emin < pmin) 
    emin
  else
    pmin
}

max_x <- function(e,p) {
  emin <-  max(euclidMSE$user)
  pmin <-  max(pearsonMSE$user)
  if (emin > pmin) 
    emin
  else
    pmin
}