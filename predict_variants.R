## Funcitons to be used 
library(caret)
library(ranger)
library(optparse)


option_list = list(
  make_option(c("-i", "--input"), type="character", default=NULL, 
              help="input file name", metavar="character"),
  make_option(c("-m", "--model"), type="character", default=NULL, 
              help="model file to classify", metavar="character"),
	make_option(c("-o", "--out"), type="character", default="classified.tmp.csv", 
              help="output file name [default= %default]", metavar="character"),
  make_option(c("-a", "--aligner"), type="character", default="star", 
              help="Aligner type, [default= %default]. If set to bwa will adapt the selection threshold", metavar="character")
); 

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

if (is.null(opt$input) || is.null(opt$model)){
  print_help(opt_parser)
  stop("both model and input file need to be specified.\n", call.=FALSE)
}


prepare_data = function(fname) {
  indata <- read.delim(fname, header=T, stringsAsFactors = T)
  input_vect = indata #Filter(function(x)!all(is.na(x)), indata)
  input_vect= input_vect[input_vect$Genotype!= '1/2',]
  # input_vect$MLEAC = as.numeric(levels(input_vect$MLEAC))[input_vect$MLEAC]
  # input_vect$MLEAF = as.numeric(levels(input_vect$MLEAF))[input_vect$MLEAF]
  na_count <-sapply(input_vect, function(y) sum(length(which(is.na(y)))))
  fix_columns = c('BaseQRankSum','ClippingRankSum','LikelihoodRankSum',
                  'MQRankSum','ReadPosRankSum','DP')
  #set these missing to '0'
  idx <- match(fix_columns, names(input_vect))
  idx = sort(idx)
  #idx <- sort(c(idx-1, idx))
  
  #remove missing context 
  input_vect = input_vect[!is.na(input_vect$Context),]
  
  for (i in idx){
    input_vect[is.na(input_vect[,i]),i] = 0
  }
  
  return(input_vect)
}



classify_me = function(model,testset,threshold){
  model= readRDS(model)
  testset = prepare_data(testset)
  tmp_pred=predict(model,testset,type = 'prob')
  tmp_pred=tmp_pred$yes >= threshold

  testset$germline = as.numeric(tmp_pred)

  return(testset[,c('ID','germline')])
}

#LOAD MODEL
#!/usr/bin/env Rscript
#args = commandArgs(trailingOnly=TRUE)

opt_parser = OptionParser(option_list=option_list);
args = parse_args(opt_parser);
model=args$model
tdata=args$input
outname=args$out
threshold = 0.5 #default model threhsold
if (args$aligner == 'bwa'){
  threshold = 0.2
  }

tt = classify_me(model,tdata,threshold)
write.csv(tt,file=outname,quote=F, sep="\t",row.names = F)
