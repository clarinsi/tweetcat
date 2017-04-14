#read the data
csv<-"../2-extraction/hbs-twitter.tsv"
tw<-read.csv(csv,sep="\t",quote="",header=F)

#print number of instances
print(length(tw[,1]))

#remove noise marked during the variable extraction process
tw<-tw[tw[,15]!="noise"]
tw[,15]<-NULL

#define lon column
lonidx<-3

#define lat column
latidx<-4

#define text column
textidx<-5

#define linguistic columns
cols<-7:length(tw[1,])

#df with only the linguistic info
tw.attr<-tw[,cols]

#calculating the number of NAs per line
tw.attr.na<-apply(tw.attr, MARGIN = 1, FUN = function(x) length(x[is.na(x)]) )

#tweets with no linguistic information are filtered
tw<-tw[tw.attr.na<length(cols),]
rm(tw.attr)
rm(tw.attr.na)

#print number of instances surviving the removal of instances without any linguistic information
print(length(tw[,1]))

#summarise
summary(tw[,cols])

#read all the functions
source("analysis.R")

#define the variable index of interest
varidx<-11

#calculate the spatial signal for each level of each linguistic variable
print(spatialSignal(tw,latidx,lonidx,varidx))

#visualise the variable values on a map with texts of the (trimmed) original tweets available as metadata
mapTweets(tw,latidx,lonidx,varidx,textidx)

#visualise the dominant levels on a map taking into account the level distributions
dominantLevel(tw,latidx,lonidx,varidx)

#visualise the dominant levels on a map without taking into account the level distributions
dominantLevel(tw,latidx,lonidx,varidx,normalised=T)
