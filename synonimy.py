'''Spróbuję dwóch podejść:
1. znajdywanie słów w kontekście przez regexy
2. porównanie odległości edycyjnej do odrzucenia etymologii
'''
import re
import numpy as np
import unicodedata
import sys

debug = False
count  = True

def SynonymInQuotes(line):
    pattern = re.compile(r"'''(.*?)'''")
    found = pattern.findall(line)
    if found is None:
        return []
    return found

def SynonymInQuotes2(line):
    pattern = re.compile(r"'{2}(?!')(.*?)'{2}")
    found = pattern.findall(line)
    if found is None:
        return []
    return found
introductoryWords = ["właściwie", "właśc.", "inaczej"] #"lub", "albo",

def introducedSynonym(line):
    answer = []
    for word in introductoryWords:
        pattern = re.compile(fr"{word}\s+(.+?)(\,|\(|\)|-)")#\s+(.+?)\s")
        found = pattern.findall(line)
        found = [f.replace("'", "") for (f,g) in found]
        answer.extend(found)
    return answer

def levenshtein(a, b):
    sizeA = len(a) + 1
    sizeB = len(b) + 1
    a = a.lower()
    b = b.lower()
    dp = np.zeros((sizeA, sizeB))
    for i in range(sizeA):
        dp[i,0] = i
    for i in range(sizeB):
        dp[0,i] = i
    
    for i in range(1, sizeA):
        for j in range(1, sizeB):
            if a[i-1] == b[j-1]:
                dp[i,j] = min(dp[i-1,j]+1, dp[i-1,j-1], dp[i,j-1]+1)
            else:
                dp[i,j] = min(dp[i-1,j]+1, dp[i-1,j-1]+1, dp[i,j-1]+1)
    #print(dp)
    return dp[sizeA-1,sizeB-1]

def skipEtymology(original, candidates):
    newList = []
    #distList = []
    for cand in candidates:
        if len(cand) < 3:
            continue
        if 'LATIN' not in unicodedata.name(cand[0]):
            continue
        dist = levenshtein(original, cand)
        #distList.append(dist)
        if dist < len(original)/2:
            continue
        newList.append(cand)
    #print(distList)
    return newList



f = open("poczatki_wikipediowe.txt", "r")
#f = open("suplement.txt", "r")


originalWord = ''
orgPattern = re.compile(r"###\s(.*?)(\s\(|\n|$)")
for i,line in enumerate(f):
    if count and i%10000==0: #3 024 407
        print(i, file=sys.stderr)
    if i % 3 == 0:
        #originalWord = line[4:]
        #print(line)
        found = orgPattern.findall(line)
        if len(found) != 0:
            originalWord, _ = found[0]
        else:
            originalWord = "Niepoprawny tytuł artykułu"
        #print(originalWord)
        continue
    if i % 3 == 2:
        continue
    #print(line)
    
    tmp1 = SynonymInQuotes(line)
    tmp2 = introducedSynonym(line)
    tmp3 = SynonymInQuotes2(line)
    tmp4 = skipEtymology(originalWord, tmp3)
    if debug:
        print(originalWord)
        print(tmp1)
        print(tmp2)
        print(tmp3)
        print(tmp4)
        print(line)
    finalAnswer = set()
    for w in tmp1:
        if len(w) == 0:
            continue #bug z '''''' zamiast Tokyo
        if w != originalWord and 'LATIN' in unicodedata.name(w[0]):
            finalAnswer.add(w)
    for w in tmp2:
        finalAnswer.add(w)
    for w in tmp4:
        finalAnswer.add(w)
    if len(finalAnswer)!=0:
        print(originalWord, end=' ')
        for word in finalAnswer:
            print('# ', end='')
            print(word, end=' ')
        print()
    if debug:
        c = input()