# how run the file to set the workdirectory 'tmpdir' 
# and use parameters from params.yaml
nextflow run -w tmpdir -params-file params.yaml SmartRNASeqCaller_pipeline.nf

# run pipeline with docker from the nextflow.config profile
nextflow run -w tmpdir -params-file params.yaml SmartRNASeqCaller_pipeline.nf -profile docker


