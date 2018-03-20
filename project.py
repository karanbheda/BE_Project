import sys
import json
import re, string,math
import random
import bisect
from numpy import cumsum, random
import copy
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from collections import Counter
from textblob import TextBlob
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
from flask import Flask, render_template
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
WORD = re.compile(r'\w+')
p = nltk.PorterStemmer()
app = Flask(__name__)

answerDictionary = {}
allSentiments = ['positive','negative']
totalFeedbacks = 0

class project():
    def __init__(self):
        fetched_tweets = {}
        self.tweets = [] 
        fileName = sys.argv[1]
        totalFeedbacks = 0
        with open(fileName + '.json', 'r') as f:
            print("Reading ",fileName,".json")
            for line in f:
                totalFeedbacks += 1 
                tweet = json.loads(line)
                fetched_tweets[tweet['id']] = tweet
                
        self.tweets = self.parseTweets(fetched_tweets)
        self.storePolarizedTweets()
        
        for x,i in zip(allSentiments,range(len(allSentiments))):
            self.feedbacks = self.getFeedbacks(fileName + '-' + x + '.json')
            self.allClusters = {}
            self.allClustersDictionary = {}
            self.initializeClustering()
            answerDictionary[i] = self.createAnswerDictionary()
            #self.printPieChart()

        print(answerDictionary)
        
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
        
    def createAnswerDictionary(self):
        dictionary = dict()
        for i in range(len(self.allClusters)):
            dictionary[self.getClusterLabel(i)] = self.allClusters[i]
        
        return dictionary
    
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
        except TypeError:
            print ("Invalid type. Type set expected.")

    def getThreshold(self, setA, setB):
        try:
            return (len(setA.union(setB))/(len(setA.difference(setB)) + len(setB.difference(setA)) + len(setA.intersection(setB))))
        except TypeError:
            print ("Invalid type. Type set expected.")
    
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
        self.allClusters[0] = {self.feedbacks[0]['id']}
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
                    self.allClusters[ID2].add(self.feedbacks[i]['id'])
                    self.allClustersDictionary[ID2] = self.addToDictionary(self.allClustersDictionary[ID2], cleanText1)
                    flag = 1
                    break
                ID2 = ID2 + 1
        
            if flag == 0:
                self.allClusters[len(self.allClusters)] = {self.feedbacks[i]['id']}
                dictionary = dict()
                self.allClustersDictionary[len(self.allClustersDictionary)] = self.addToDictionary(dictionary, cleanText1)
    
    
    def storePolarizedTweets(self):
        fileName = sys.argv[1].split('.')[0]
        
        for x in allSentiments:
            print("Storing all the ",x," feedbacks")
            sentimentalFeedbacks = [tweet for tweet in self.tweets if tweet['sentiment'] == x]
            
            f = open(fileName + "-" + x + ".json",'w')
            for tweet in sentimentalFeedbacks:
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

@app.route('/result')
def result():
    return render_template('index.html', result1 = 100, result2 = 10)
   
         
def main():
    if len(sys.argv) != 2:
        print >> sys.stderr, 'Usage: %s [json file]' % (sys.argv[0])
        exit(-1)
        
    xyz = project()
      
if __name__ == '__main__':
    main()
    app.run(debug = True)
