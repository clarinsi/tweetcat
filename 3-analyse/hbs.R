#read the data
csv<-"../2-extraction/hbs.csv"
tw<-read.csv(csv,sep=",",header=F)

#print number of instances
print(length(tw[,1]))

#remove noise marked during the variable extraction process
tw<-tw[tw[,16]!="noise"]
tw[,16]<-NULL

#define lon column
lonidx<-3

#define lat column
latidx<-4

#define text column
textidx<-6

#define linguistic columns
cols<-7:length(tw[1,])

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
