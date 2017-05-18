#read the data
tw<-read.csv("../2-extract/bi_geo.csv",header=F)

#print number of instances
print(length(tw[,1]))

#define lon column
lonidx<-3

#define lat column
latidx<-4

#define text column
textidx<-6

#summarise additional columns
summary(tw[,7:length(tw[1,])])

#most frequent sources
sort(table(tw$V9),decreasing=T)[1:20]

#read all the functions
source("analysis.R")

#geographical outliers
mapTweets(tw,latidx,lonidx,5,textidx)
tw<-tw[tw$V4>50 & tw$V4<60 & tw$V3>-11 & tw$V3<2,]
mapTweets(tw,latidx,lonidx,5,textidx)

#old vs. new accounts
mapTweets(tw,latidx,lonidx,10,textidx)
dominantLevel(tw,latidx,lonidx,10,normalised=T)

#country vs. account age
table(tw$V10,tw$V5)
prop.table(table(tw$V10,tw$V5),margin=2)
plot(table(tw$V10,tw$V5))
chisq.test(tw$V10,tw$V5)

#text length vs. account age
plot(tw$V13~tw$V10)
wilcox.test(tw$V13~tw$V10)

#where is Instagram the main source of tweets
tw$V16<-as.factor(grepl("Instagram",tw$V9))
mapTweets(tw,latidx,lonidx,16,textidx)
dominantLevel(tw,latidx,lonidx,16)

#where is automation dominant
tw$V16<-as.factor(grepl("dlvr.it",tw$V9))
mapTweets(tw[tw$V16=="TRUE",],latidx,lonidx,16,textidx)
mapTweets(tw,latidx,lonidx,16,textidx)
dominantLevel(tw,latidx,lonidx,16,normalised=T)

#Android vs. iOS
tw$V16<-NA
tw[grepl("iOS",tw$V9)|grepl("iPad",tw$V9)|grepl("iPhone",tw$V9)|grepl("Apple",tw$V9),]$V16<-"iOS"
tw[grepl("Android",tw$V9),]$V16<-"Android"
tw$V16<-as.factor(tw$V16)
summary(tw$V16)
mapTweets(tw,latidx,lonidx,16,textidx)
dominantLevel(tw,latidx,lonidx,16,normalised=T)
