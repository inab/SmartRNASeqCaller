## Funcitons to be used 
#Evaluation NA 12878
library(caret)
# library(randomForest)
# library(ggplot2)
# library(pROC)
# library(parallel)
# library(doParallel)
# library(plyr)
# library(psych)
# library(RColorBrewer)
# library(PRROC)
library(ranger)

prepare_data = function(fname) {
  indata <- read.delim(fname, header=T, stringsAsFactors = T)
  input_vect = Filter(function(x)!all(is.na(x)), indata)
  input_vect= input_vect[input_vect$Genotype!= '1/2',]
  # input_vect$MLEAC = as.numeric(levels(input_vect$MLEAC))[input_vect$MLEAC]
  # input_vect$MLEAF = as.numeric(levels(input_vect$MLEAF))[input_vect$MLEAF]
  na_count <-sapply(input_vect, function(y) sum(length(which(is.na(y)))))
  fix_columns = c('BaseQRankSum','ClippingRankSum','LikelihoodRankSum',
                  'MQRankSum','ReadPosRankSum')
  #set these missing to '0'
  idx <- match(fix_columns, names(input_vect))
  idx <- sort(c(idx-1, idx))
  
  #remove missing context 
  input_vect = input_vect[!is.na(input_vect$Context),]
  
  for (i in idx){
    input_vect[is.na(input_vect[,i]),i] = 0
  }
  
  return(input_vect)
}



classify_me = function(model,testset){
  model= readRDS(model)
  testset = prepare_data(testset)
  testset$germline = predict(model,testset)
  return(testset[,c('ID','germline')])
}

#LOAD MODEL
#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)
model=args[1]
tdata=args[2]
outname=args[3]
tt = classify_me(model,tdata)
write.csv(tt,file=outname,quote=F, sep="\t",row.names = F)
