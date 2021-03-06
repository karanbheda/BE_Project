# -*- coding: UTF-8 -*-
import sys
import json
import re, string,math
import random
import bisect
from numpy import cumsum, random
import copy
from nltk.corpus import stopwords
from collections import Counter
from textblob import TextBlob
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
from flask import Flask, render_template, request
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
WORD = re.compile(r'\w+')
p = nltk.PorterStemmer()
app = Flask(__name__)
allSentiments = ['positive','negative']
totalFeedbacks = {'positive': 0, 'negative': 0}
finalResult = dict()


class project():
    def __init__(self, fileName, startDate, endDate):
        fetched_tweets = {}
        self.tweets = [] 
        self.fileName = fileName
        self.send = []
        date = {}
        date[0] = [word for word in startDate.split("-")]
        date[1] = [word for word in endDate.split("-")]
            
        with open(fileName + '.json', 'r') as f:
            print("Reading ",fileName,".json")
            for line in f:
                tweet = json.loads(line)
                tweetDate = tweet['date'].split("-")
                flag = True
                for i in range(3):
                    if not (int(tweetDate[i]) >= int(date[0][i]) and int(tweetDate[i]) <= int(date[1][i])):
                        flag = False
                        break
                if flag:        
                    fetched_tweets[tweet['id']] = tweet
                
        self.tweets = self.parseTweets(fetched_tweets)
        self.feedbacks = []
        self.storePolarizedTweets()

        self.allClusters = {}
        self.allClustersDictionary = {}
        self.initializeClustering()
        self.formatFinalResult()
        
        print(finalResult)

    def formatFinalResult(self):
        for i in range(len(self.allClusters)):
            finalResult[self.getClusterLabel(i)] = self.allClusters[i]
        
    def printPieChart(self): 
        for i in range(len(answerDictionary)):
            labels = []
            values = []
            
            for k,v in answerDictionary[i].items():
                labels.append(k)
                values.append(len(v))
            
            plt.figure(i)
            plt.title(allSentiments[i] + "feedbacks")
            plt.pie(values, labels = labels, 
            startangle=90, shadow = True,
            radius = 1.2, autopct = '%1.1f%%')
            
            plt.legend()    
            
        plt.show()
        
    
    def getFeedbacks(self, fileName):
        tweets = []
        with open(fileName, 'r') as f:
            for line in f:
                tweet = json.loads(line)
                tweets.append(tweet)
        
        return tweets        
    
      
    def getClusterLabel(self, i):
        mydict = self.allClustersDictionary[i]
        for k in sorted(mydict, key=mydict.get, reverse=True):
            return k
    
    def jaccardIndex(self, setA, setB):
        try:
            return 1 - float(len(setA.intersection(setB))) / float(len(setA.union(setB)))
        except ZeroDivisionError:
            return 0

    def getThreshold(self, setA, setB):
        try:
            return (len(setA.union(setB))/(len(setA.difference(setB)) + len(setB.difference(setA)) + len(setA.intersection(setB))))
        except ZeroDivisionError:
            return 0
    
    def convertToNouns(self, line):
        textBlob = TextBlob(line)
        result = []
        for word,pos in textBlob.tags:
            if pos == 'NN':
                result.append(word)
            if pos == 'NNS':
                result.append(p.stem(word))
        
        return result
    
    
    def addToDictionary(self, dictionary, words):
        for word in words:
            if word in dictionary:
                dictionary[word] = dictionary[word] + 1
            else:
                dictionary[word] = 1
         
        return dictionary
    
  
    def initializeClustering(self):
        self.allClusters[0] = dict({'positive':set(), 'negative':set()})
        self.allClusters[0][self.feedbacks[0]['sentiment']] = {self.feedbacks[0]['id']}
        dictionary = dict()
        cleanText = self.convertToNouns(self.feedbacks[0]['text'])
        self.allClustersDictionary[0] = self.addToDictionary(dictionary, cleanText)
        flag = 0
        
        for i in range(1, len(self.feedbacks)):
            ID1 = self.feedbacks[i]['id']
            cleanText1 = self.convertToNouns(self.feedbacks[i]['text'])
            bag1 = set(cleanText1)
            flag = 0
            ID2 = 0
            while ID2 in range(len(self.allClusters)):
                bag2 = set(self.allClustersDictionary[ID2].keys())
                distance = self.jaccardIndex(bag1, bag2)
                threshold = self.getThreshold(bag1, bag2)

                if distance < threshold:
                    self.allClusters[ID2][self.feedbacks[i]['sentiment']].add(self.feedbacks[i]['id'])
                    self.allClustersDictionary[ID2] = self.addToDictionary(self.allClustersDictionary[ID2], cleanText1)
                    flag = 1
                    break
                ID2 = ID2 + 1
        
            if flag == 0:
                x = len(self.allClusters)
                self.allClusters[x] = dict({'positive':set(), 'negative':set()})
                self.allClusters[x][self.feedbacks[i]['sentiment']] = {self.feedbacks[i]['id']}
                dictionary = dict()
                self.allClustersDictionary[len(self.allClustersDictionary)] = self.addToDictionary(dictionary, cleanText1)
    
    
    def storePolarizedTweets(self):        
        for x in allSentiments:
            print("Storing all the ",x," feedbacks")
            
            f = open(self.fileName + "-" + x + ".json",'w')
            for tweet in self.tweets:
                if tweet['sentiment'] == x:
                    totalFeedbacks[x] = totalFeedbacks[x] + 1
                    self.feedbacks.append(tweet)
                    f.write("{\"id\":" + str(tweet['id']) + ",\"text\":\"" + tweet['text'] + "\",\"sentiment\":\"" + tweet['sentiment'] + "\"}\n")
                
            f.close();
    
    def clean_tweet(self, line):
        stop_free = " ".join([i for i in line.lower().split() if i not in stop])
        punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
        normalized = " ".join(word for word in punc_free.split())
        return normalized
    
 
    def get_tweet_sentiment(self, tweet):
        
        analysis = TextBlob(tweet)
        
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

        
    
    def parseTweets(self, fetched_tweets):
        print("Processing and cleaning all the feedbacks")
        polarizedtweets = []
        
        for ID in fetched_tweets:
            for sentences in fetched_tweets[ID]['text'].split('.'):
                parsed_tweet = {}
                parsed_tweet['id'] = fetched_tweets[ID]['id']
                parsed_tweet['text'] = self.clean_tweet(sentences)
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(parsed_tweet['text'])
                
                polarizedtweets.append(parsed_tweet)
         
        return polarizedtweets

@app.route('/')
def initialize():
    return render_template('index.html')
  
@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
      fileName = request.form['filename']
      startDate = request.form['startdate']
      endDate = request.form['enddate']
      xyz = project(fileName, startDate, endDate)
      
      return render_template("result.html", result = finalResult, result1 = totalFeedbacks['positive'], result2 = totalFeedbacks['negative'])
      
if __name__ == '__main__':
    app.run(debug = True)


