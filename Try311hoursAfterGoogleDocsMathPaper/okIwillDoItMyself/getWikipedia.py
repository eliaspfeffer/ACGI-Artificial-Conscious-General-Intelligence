import wikipedia
from wikipedia.exceptions import PageError

def filterWikiReply(result):
    """filters the reply from wikipedia from errors. Only returns the summary or the multiple result options"""
    if "may refer to:" in result:
        #return everything after (may refer to:)
        return result.split("may refer to:")[1]
    elif "does not match any pages. Try another id!" in result:
        return None
    else:
        return result

def researchAboutThisTopic(topic):
    try:
        result = wikipedia.summary(topic, sentences=3)
        result = filterWikiReply(result)
        if result:
            print(result)
            return result
        else:
            print("No summary found for the topic " + topic + ".")
            return None
    except PageError:
        print("No page found for the topic " + topic + ".")
        return None
   
    

researchAboutThisTopic("Happiness")
# result = wikipedia.summary("Happiness", sentences=3)
# print(result)