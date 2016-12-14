# unmerged pr to the scales repo 
# https://github.com/hrbrmstr/scales/blob/b27b8acefe4188ede47d9cf479c383ce1b35405c/R/formatter.r

byte_format <- function(symbol="auto", units="binary") {
  function(x) bytes(x, symbol, units)
}

Kb <- byte_format("Kb", "binary")
Mb <- byte_format("Mb", "binary")
Gb <- byte_format("Gb", "binary")


bytes <- function(x, symbol="auto", units=c("binary", "si")) {
  
  symbol <- match.arg(symbol, c("auto",
                                "b",  "Kb",  "Mb",  "Gb",  "Tb",  "Pb",  "Eb",  "Zb",  "Yb",
                                "B",  "KB",  "MB",  "GB",  "TB",  "PB",  "EB",  "ZB",  "YB",
                                "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"))
  
  units <- match.arg(units, c("binary", "si"))
  
  base <- switch(units, `binary`=1024, `si`=1000)
  
  if (symbol == "auto") {
    symbol <-
      if      (max(x) >= (base^5)) { "Pb" }
    else if (max(x) >= (base^4)) { "Tb" }
    else if (max(x) >= (base^3)) { "Gb" }
    else if (max(x) >= (base^2)) { "Kb" }
    else if (max(x) >= (base^1)) { "Mb" }
    else                         {  "b" }
  }
  
  switch(symbol,
         "b" =,  "B"  = paste(x,                  "bytes"),
         
         "Kb" =, "KB" = paste(round(x/(base^1), 1L), "Kb"),
         "Mb" =, "MB" = paste(round(x/(base^2), 1L), "Mb"),
         "Gb" =, "GB" = paste(round(x/(base^3), 1L), "Gb"),
         "Tb" =, "TB" = paste(round(x/(base^4), 1L), "Tb"),
         "Pb" =, "PB" = paste(round(x/(base^5), 1L), "Pb"),
         "Eb" =, "EB" = paste(round(x/(base^6), 1L), "Eb"),
         "Zb" =, "ZB" = paste(round(x/(base^7), 1L), "Zb"),
         "Yb" =, "YB" = paste(round(x/(base^8), 1L), "Yb"),
         
         "KiB"        = paste(round(x/(base^1), 1L), "KiB"),
         "MiB"        = paste(round(x/(base^2), 1L), "MiB"),
         "GiB"        = paste(round(x/(base^3), 1L), "GiB"),
         "TiB"        = paste(round(x/(base^4), 1L), "TiB"),
         "PiB"        = paste(round(x/(base^5), 1L), "PiB"),
         "EiB"        = paste(round(x/(base^6), 1L), "EiB"),
         "ZiB"        = paste(round(x/(base^7), 1L), "ZiB"),
         "YiB"        = paste(round(x/(base^8), 1L), "YiB")
  )
  
}