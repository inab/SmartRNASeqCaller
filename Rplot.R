args <- commandArgs(TRUE)
library(UpSetR)
datavar <- read.csv(args[1],header=T,sep='\t',stringsAsFactors=F, na.strings=c("","NA"))
pdf(args[2], width=10, height=7, onefile=F)
upset(fromList(datavar), nsets=6, order.by = "freq")
dev.off()


