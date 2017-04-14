library(sp)
library(GISTools)
library(raster)
library(leaflet)

spatialSignal<-function(df,latidx,lonidx,varidx){
  df<-df[,c(lonidx,latidx,varidx)]
  names(df)<-c("y","x","attr")
  
  #remove instances which do not have a value for this variable
  df<-df[!is.na(df$attr),]
  
  #if there are more than 5000 samples, a random subset of 5000 samples is selected
  if(nrow(df)>5000){
    df<-df[round(runif(5000,1,nrow(df))),]
  }
  
  df$attr<-factor(df$attr)
  #check whether there are at least two levels
  if(length(levels(df$attr))<2){
    return(data.frame(feature=NA, level=NA, distLevel=NA,distFeature=NA,distRel=NA, nValues=NA))
  }
  
  #produce a SpatialPointsDataFrame
  coordinates(df)<-~x+y
  proj4string(df)<-CRS("+init=epsg:4326")
  
  #calculate the median of distances between points
  df.dist<-median(spDists(df, longlat = TRUE))*1000
  
  #for each level calculate the median of distances between points
  output<-data.frame(feature=integer(), level=factor(), distLevel=double(),distFeature=double(),distRel=double(), nValues=integer())
  for(i in levels(df@data$attr)){
    df.sub<-subset(df,attr==i)
    df.sub.dist<-median(spDists(df.sub, longlat = TRUE))*1000
    output<-rbind(output,data.frame(feature=varidx,level=i,distLevel=df.sub.dist,distFeature=df.dist,distRel=df.sub.dist/df.dist,nValues=length(df.sub)))
  }
  
  return(output)
}

mapTweets<-function(df,latidx,lonidx,varidx,textidx){
  df<-df[,c(latidx,lonidx,varidx,textidx)]
  names(df)<-c("y","x","attr","text")
  
  df<-df[!is.na(df$attr),]
  df<-df[!is.na(df$text),]
  
  coordinates(df)<-~x+y
  proj4string(df)<-CRS("+init=epsg:4326")
  
  pal <- colorFactor('RdYlBu', df@data$attr)
  
  print(table(df$attr))
  print(paste("n measures:",length(df)))
  
  m <- leaflet(df) %>%
    ##background map
    addTiles() %>%
    ##own idw raster
    addCircleMarkers(df@coords[,1],df@coords[,2], color=~pal(attr),radius=5,stroke=FALSE,popup = df@data$text,fillOpacity = 0.5)%>%
    
    addLegend(position = 'topright',colors = ~pal(levels(attr)), labels = ~levels(attr))   
  #execute the leaflet object and thus create the visualisation
  m
}

dominantLevel<-function(df,latidx,lonidx,varidx,normalised=F,filtQuart=1,h=2){
  df<-df[,c(latidx,lonidx,varidx)]
  names(df)<-c("y","x","attr")
  
  df<-df[!is.na(df$attr),]
  
  if(!normalised){
    df.props<-prop.table(table(df$attr))
  }
  
  coordinates(df)<-~x+y
  proj4string(df)<-CRS("+init=epsg:4326")
  
  df.dens.feature<-kde.points(df,h=h,n=500,lims=df)
  df.dens.feature@data$kde<-df.dens.feature@data$kde/mean(df.dens.feature@data$kde)
  for(i in levels(df@data$attr)){
    df.sub<-subset(df,attr==i)
    df.sub.dens<-kde.points(df.sub,h=h,n=500,lims=df)
    #print(attributes(df.sub.dens@data$kde))
    #print(class(df.sub.dens@data$kde*props[i]))
    df.dens.feature@data[,i]<-df.sub.dens@data$kde/mean(df.sub.dens@data$kde)
    if(!normalised){df.dens.feature@data[,i]<-df.dens.feature@data[,i]*2*df.props[i]}
  }
  
  #sum(df.dens.feature@data$kde)
  #sum(df.dens.feature@data$r)
  #sum(df.dens.feature@data$`r-drop`)
  
  
  maxLevel<-colnames(df.dens.feature@data)[apply(df.dens.feature@data,1,which.max)]
  maxValue<-apply(df.dens.feature@data,1,max)
  values<-maxValue<=sort(maxValue)[round(filtQuart*length(maxValue)/4)]
  maxLevel[values]<-NA
  
  df.dens.feature.summary<-df.dens.feature
  df.dens.feature.summary@data<-data.frame(maxLevel=maxLevel)
  
  df.raster<-raster(df.dens.feature.summary)
  
  pal <- colorFactor('RdYlBu', factor(df.raster@data@values))
  
  m <- leaflet() %>%
    
    #background map
    addTiles() %>%
    
    #hexagons
    addRasterImage(df.raster , colors= pal, project=T, opacity = 0.3, group="Dominance") %>%
    
    #legend for percipitation meassures
    addLegend(position = 'topright',colors = pal(levels(factor(df.raster@data@values))), labels = levels(df.raster@data@attributes[[1]]$levels))%>%  
    #interactive legend
    addLayersControl(
      overlayGroups = c("Dominance"),
      options = layersControlOptions(collapsed = TRUE)
    )
  #execute m
  m
}

